"""
boolean_engine.py — VaartaVerse Classical IR Engine
=====================================================
Boolean Retrieval Engine: NOT > AND > OR precedence with parenthesization.

Grammar (recursive descent, standard precedence):
    or_expr   → and_expr ('OR' and_expr)*
    and_expr  → not_expr (('AND')? not_expr)*      # juxtaposition = implicit AND
    not_expr  → 'NOT' not_expr | atom
    atom      → '(' or_expr ')' | WORD

So:
    a OR b AND c        ==  a OR (b AND c)      (AND binds tighter than OR)
    jackal NOT tiger    ==  jackal AND NOT tiger
    jackal tiger        ==  jackal AND tiger     (implicit AND)

Syntax errors raise BooleanParseError with a precise message; the API layer
translates them to HTTP 422 so the client can show them. No silent fallbacks.

Results are ranked by summed TF-IDF document weight over the matched terms,
so boolean output is deterministic and meaningful rather than sorted by ID.
"""

import math
import re
from dataclasses import asdict
from typing import Optional

from app.core.inverted_index import InvertedIndex
from app.core.preprocessing import preprocess


class BooleanParseError(Exception):
    """Raised when a boolean query cannot be parsed."""

    def __init__(self, message: str, position: Optional[int] = None):
        super().__init__(message)
        self.position = position


_OPERATOR_WORDS = {"AND", "OR", "NOT"}


class _Tokenizer:
    """Breaks a boolean query string into tokens: words, AND, OR, NOT, (, )."""

    def __init__(self, text: str):
        # split on whitespace and parentheses (keep parens as tokens)
        self._tokens = re.findall(r"[()]|[^\s()]+", text.strip())
        self._pos = 0

    def peek(self) -> Optional[str]:
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return None

    def consume(self) -> str:
        if self._pos >= len(self._tokens):
            raise BooleanParseError("Unexpected end of boolean expression")
        tok = self._tokens[self._pos]
        self._pos += 1
        return tok

    def has_more(self) -> bool:
        return self._pos < len(self._tokens)


class _BoolParser:
    """Recursive-descent parser that evaluates a boolean expression against the index."""

    def __init__(self, index: InvertedIndex):
        self._index = index

    def parse_and_eval(self, query: str) -> set[str]:
        tokenizer = _Tokenizer(query)
        result = self._or_expr(tokenizer)
        if tokenizer.has_more():
            raise BooleanParseError(
                f"Unexpected token: {tokenizer.peek()!r} — check operator placement or parentheses"
            )
        return result

    def _or_expr(self, t: _Tokenizer) -> set[str]:
        """or_expr → and_expr ('OR' and_expr)*   (lowest precedence)"""
        result = self._and_expr(t)
        while t.peek() == "OR":
            t.consume()
            right = self._and_expr(t)
            result = result | right
        return result

    def _and_expr(self, t: _Tokenizer) -> set[str]:
        """
        and_expr → not_expr (('AND')? not_expr)*
        An operand without an explicit AND (juxtaposition) is an implicit AND.
        """
        result = self._not_expr(t)
        while True:
            nxt = t.peek()
            if nxt == "AND":
                t.consume()
                result = result & self._not_expr(t)
            elif nxt == "NOT" or nxt == "(" or (nxt is not None and nxt not in (")", "OR", "AND")):
                # Juxtaposition = implicit AND:
                #   "jackal tiger"  == "jackal AND tiger"
                #   "jackal NOT tiger" == "jackal AND (NOT tiger)"
                #   "jackal (lion OR tiger)" == "jackal AND (lion OR tiger)"
                result = result & self._not_expr(t)
            else:
                break
        return result

    def _not_expr(self, t: _Tokenizer) -> set[str]:
        """not_expr → 'NOT' not_expr | atom   (highest precedence)"""
        if t.peek() == "NOT":
            t.consume()
            operand = self._not_expr(t)
            return self._index.get_all_doc_ids() - operand
        return self._atom(t)

    def _atom(self, t: _Tokenizer) -> set[str]:
        """atom → '(' or_expr ')' | WORD"""
        tok = t.peek()
        if tok is None:
            raise BooleanParseError("Unexpected end of boolean expression")
        if tok == "(":
            t.consume()
            result = self._or_expr(t)
            if t.peek() != ")":
                raise BooleanParseError("Missing closing parenthesis ')'")
            t.consume()
            return result
        word = t.consume()
        if word in _OPERATOR_WORDS:
            raise BooleanParseError(f"Operator {word!r} in unexpected position")
        stems = preprocess(word)
        if not stems:
            raise BooleanParseError(
                f"Query term {word!r} consists only of stopwords — it cannot be matched"
            )
        # Intersect across all stems of the word (multi-token words are ANDed)
        result: Optional[set[str]] = None
        for stem in stems:
            posting_docs = set(self._index.get_postings(stem).keys())
            result = posting_docs if result is None else result & posting_docs
        return result or set()


class BooleanEngine:
    """
    Public interface for Boolean retrieval.

    Supports:
        - Simple keyword queries ("jackal lion")
        - Boolean operators ("jackal AND lion NOT tiger", "jackal OR lion AND tiger")
        - Parenthesized expressions ("(jackal OR fox) AND (lion OR tiger)")
        - Implicit AND via juxtaposition ("jackal tiger" == "jackal AND tiger")
        - Juxtaposed NOT ("jackal NOT tiger" == "jackal AND NOT tiger")
        - Optional metadata filters (region, tradition)

    Parse errors raise BooleanParseError — the API layer maps them to HTTP 422.
    Results are ranked by summed TF-IDF weight of matched query terms.
    """

    def __init__(self, index: InvertedIndex):
        self._index = index
        self._parser = _BoolParser(index)

    # ------------------------------------------------------------------
    # Ranking helper
    # ------------------------------------------------------------------

    def _rank(self, doc_ids: set[str], matched_terms: set[str]) -> list[tuple[str, float]]:
        """Score docs by summed tf-idf over matched terms (descending)."""
        N = self._index.doc_count()
        scored: list[tuple[str, float]] = []
        for doc_id in doc_ids:
            s = 0.0
            for term in matched_terms:
                entry = self._index.get_postings(term).get(doc_id)
                if entry is None:
                    continue
                df = self._index.get_df(term)
                idf = math.log(1.0 + N / df) if df > 0 else 0.0
                s += (1.0 + math.log(entry.tf)) * idf
            scored.append((doc_id, s))
        scored.sort(key=lambda x: (-x[1], x[0]))
        return scored

    def _collect_matched_terms(self, query: str) -> set[str]:
        """The (stemmed) terms actually usable in the index for ranking."""
        return {
            stem
            for w in re.findall(r"[^\s()]+", query)
            if w.upper() not in _OPERATOR_WORDS
            for stem in preprocess(w)
        }

    # ------------------------------------------------------------------
    # Public search
    # ------------------------------------------------------------------

    def search(self, query: str, filters: dict | None = None) -> list[dict]:
        """
        Evaluate a boolean query and return matching documents.

        Args:
            query:   Boolean expression string.
            filters: Optional metadata filters e.g. {"region": "Bengal"}.

        Returns:
            Ranked list of doc metadata dicts (score = summed tf-idf of matched terms).

        Raises:
            BooleanParseError: on malformed queries (mapped to HTTP 422 upstream).
        """
        normalized = re.sub(
            r"\b(and|or|not)\b", lambda m: m.group(0).upper(), query.strip()
        )

        has_explicit_bool = any(op in normalized.split() for op in _OPERATOR_WORDS)

        # Plain keyword lists ("jackal lion") become implicit ANDs by the grammar itself,
        # so no string rewriting is needed — the grammar handles juxtaposition.

        matching_ids = self._parser.parse_and_eval(normalized)

        # Ranking needs the stems that exist in the index. For NOT-dominated queries
        # the matched set can be huge; tf-idf ranking keeps it sensible.
        ranked = self._rank(matching_ids, self._collect_matched_terms(normalized))

        results = []
        for doc_id, score in ranked:
            meta = self._index.get_doc_meta(doc_id)
            if meta is None:
                continue
            if filters:
                region_f = filters.get("region", "")
                tradition_f = filters.get("tradition", "")
                if region_f and region_f.lower() not in meta.region.lower():
                    continue
                if tradition_f and tradition_f.lower() not in meta.tradition.lower():
                    continue
            result = asdict(meta)
            result["score"] = round(score, 6)
            results.append(result)

        return results
