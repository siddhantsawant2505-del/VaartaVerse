"""
boolean_engine.py — VaartaVerse Classical IR Engine
=====================================================
Boolean Retrieval Engine: AND / OR / NOT with full parenthesization support.

Grammar (recursive descent parser):
    expr   → term (('AND' | 'OR') term)*
    term   → 'NOT' atom | atom
    atom   → '(' expr ')' | WORD

Returns an unranked set of matching doc_ids.
"""

import re
from dataclasses import asdict
from typing import Optional

from app.core.inverted_index import InvertedIndex
from app.core.preprocessing import preprocess


class BooleanParseError(Exception):
    pass


class _Tokenizer:
    """Breaks a boolean query string into tokens: words, AND, OR, NOT, (, )."""

    _OPERATORS = {"AND", "OR", "NOT"}

    def __init__(self, text: str):
        # split on whitespace and parentheses (keep parens as tokens)
        raw = re.findall(r"[()]|[^\s()]+", text.strip())
        self._tokens = raw
        self._pos = 0

    def peek(self) -> Optional[str]:
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return None

    def consume(self) -> str:
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
        result = self._expr(tokenizer)
        if tokenizer.has_more():
            raise BooleanParseError(f"Unexpected token: {tokenizer.peek()}")
        return result

    def _expr(self, t: _Tokenizer) -> set[str]:
        """expr → term (('AND' | 'OR') term)*"""
        result = self._term(t)
        while t.peek() in ("AND", "OR"):
            op = t.consume()
            right = self._term(t)
            if op == "AND":
                result = result & right
            else:
                result = result | right
        return result

    def _term(self, t: _Tokenizer) -> set[str]:
        """term → 'NOT' atom | atom"""
        if t.peek() == "NOT":
            t.consume()
            operand = self._atom(t)
            all_docs = self._index.get_all_doc_ids()
            return all_docs - operand
        return self._atom(t)

    def _atom(self, t: _Tokenizer) -> set[str]:
        """atom → '(' expr ')' | WORD"""
        tok = t.peek()
        if tok is None:
            raise BooleanParseError("Unexpected end of boolean expression")
        if tok == "(":
            t.consume()  # consume '('
            result = self._expr(t)
            if t.peek() != ")":
                raise BooleanParseError("Missing closing parenthesis ')'")
            t.consume()  # consume ')'
            return result
        # It's a keyword — stem it and look up postings
        word = t.consume()
        stems = preprocess(word)
        if not stems:
            return set()
        # Intersect across all stems of the word (multi-token words are ANDed)
        result = None
        for stem in stems:
            posting_docs = set(self._index.get_postings(stem).keys())
            result = posting_docs if result is None else result & posting_docs
        return result or set()


class BooleanEngine:
    """
    Public interface for Boolean retrieval.

    Supports:
        - Simple keyword queries ("jackal lion")
        - Boolean operators ("jackal AND lion NOT tiger")
        - Parenthesized expressions ("(jackal OR fox) AND (lion OR tiger)")
        - Optional metadata filters (region, tradition, collection)
    """

    def __init__(self, index: InvertedIndex):
        self._index = index
        self._parser = _BoolParser(index)

    def search(self, query: str, filters: dict | None = None) -> list[dict]:
        """
        Evaluate boolean query and return matching documents as metadata dicts.

        Args:
            query:   Boolean expression string.
            filters: Optional metadata filters e.g. {"region": "Bengal"}.

        Returns:
            List of doc metadata dicts (unranked, sorted by tale_id for stability).
        """
        # Normalise operators to uppercase
        normalized = re.sub(
            r"\b(and|or|not)\b", lambda m: m.group(0).upper(), query.strip()
        )

        # If no boolean operators detected, default to AND of all terms
        if not any(op in normalized.split() for op in ("AND", "OR", "NOT")):
            terms = [t.upper() if t.upper() in ("AND", "OR", "NOT") else t for t in normalized.split()]
            normalized = " AND ".join(terms)

        try:
            matching_ids = self._parser.parse_and_eval(normalized)
        except BooleanParseError as e:
            return [{"error": str(e)}]

        results = []
        for doc_id in sorted(matching_ids):
            meta = self._index.get_doc_meta(doc_id)
            if meta is None:
                continue
            # Apply optional metadata filters
            if filters:
                region_f = filters.get("region", "")
                tradition_f = filters.get("tradition", "")
                if region_f and region_f.lower() not in meta.region.lower():
                    continue
                if tradition_f and tradition_f.lower() not in meta.tradition.lower():
                    continue
            results.append(asdict(meta))

        return results
