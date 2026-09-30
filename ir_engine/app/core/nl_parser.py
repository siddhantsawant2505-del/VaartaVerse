"""
nl_parser.py — VaartaVerse Classical IR Engine
===============================================
Rule-Based Natural Language Query Parser.
No LLMs — purely regex patterns, dictionary lookup, and POS-inspired heuristics.

Pipeline:
    1. Pattern detection: detect boolean phrases ("tales about X and Y")
    2. Entity extraction: known regions, traditions, tale-type codes from lexicon
    3. Stop phrase removal: strip filler ("find me", "show tales about", "which stories")
    4. Query expansion: attach region/tradition filters if recognised
    5. Optional WordNet synonym expansion (see query_expansion.py) — expansion
       terms are reported in the parsed payload and weighted below the original
       query terms during retrieval
    6. Query routing: decide boolean vs VSM based on structure

Example:
    "stories about clever jackal tricking a lion in Panchatantra"
    → mode: vsm
    → normalized_query: "clever jackal trick lion panchatantra"
    → filters: {tradition: "Panchatantra"}

    "tales with lion AND jackal but not tiger"
    → mode: boolean
    → structured_query: "lion AND jackal NOT tiger"
"""

import re
from typing import Optional

from app.core.preprocessing import preprocess, tokenize
from app.core.query_expansion import expand_terms

# ---------------------------------------------------------------------------
# Lexicons — extended as corpus grows
# ---------------------------------------------------------------------------

KNOWN_TRADITIONS = {
    "panchatantra": "Panchatantra",
    "hitopadesha": "Hitopadesha",
    "hitopadesa": "Hitopadesha",
    "jataka": "Jataka",
    "vikramaditya": "Vikramaditya",
    "baital pachisi": "Vikramaditya",
    "baital": "Vikramaditya",
    "birbal": "Birbal-Akbar",
    "akbar": "Birbal-Akbar",
    "tenali": "Tenali Raman",
    "tenali raman": "Tenali Raman",
    "puranic": "Puranic/Mythological",
    "ramayana": "Puranic/Mythological",
    "mahabharata": "Puranic/Mythological",
}

KNOWN_REGIONS = {
    "kashmir": "Kashmir",
    "punjab": "Punjab",
    "bengal": "Bengal",
    "odisha": "Odisha",
    "magadha": "Magadha",
    "ujjain": "Ujjain",
    "andhra": "Andhra Pradesh",
    "karnataka": "Karnataka",
    "south india": "South India",
    "north india": "North India",
}

KNOWN_ATU_CODES = {
    r"atu[\s-]?122": "ATU-122",
    r"atu[\s-]?91": "ATU-91",
    r"atu[\s-]?910": "ATU-910",
    r"atu[\s-]?545": "ATU-545",
    r"atu[\s-]?1430": "ATU-1430",
    r"atu[\s-]?157": "ATU-157",
    r"atu[\s-]?2040": "ATU-2040",
    r"atu[\s-]?610": "ATU-610",
    r"atu[\s-]?217": "ATU-217",
}

# Filler phrases to strip before processing
FILLER_PATTERNS = [
    r"^(find|show|search for|give me|list|display)\s+(me\s+)?(all\s+)?(tales?|stories?|texts?|variants?)?\s*(about|on|regarding|from|in|with|where)?\s*",
    r"^(which|what)\s+(tales?|stories?)\s+(involve|feature|contain|include|are about)\s*",
    r"^tell me about\s*",
    r"\s*please\s*",
    r"\s*in the corpus\s*",
]

# Implicit boolean phrase patterns → structured boolean
BOOLEAN_PHRASE_PATTERNS = [
    (r"\bbut not\b", "NOT"),
    (r"\band not\b", "NOT"),
    (r"\bor else\b", "OR"),
    (r"\beither\b.*?\bor\b", "OR"),
    (r"\bboth\b.*?\band\b", "AND"),
]


class NLQueryParser:
    """
    Rule-based NL parser that converts free-text queries into structured IR queries.
    """

    def parse(
        self,
        raw_query: str,
        expand_synonyms: bool = False,
        vocabulary: Optional[set] = None,
    ) -> dict:
        """
        Parse a natural-language query.

        Args:
            raw_query:       The user's free-text query.
            expand_synonyms: Add WordNet synonyms to the VSM query (off by default).
                             Only applied for VSM mode; boolean semantics must
                             stay exact.
            vocabulary:      Index vocabulary to filter synonyms against.

        Returns:
            {
                "mode": "vsm" | "boolean",
                "original_query": str,
                "normalized_query": str,      # cleaned for VSM retrieval
                "structured_query": str,      # boolean expression if mode=boolean
                "entities": {...},
                "filters": dict,
                "stemmed_terms": list[str],
                "expansions": {term: [synonyms]},   # empty unless expansion enabled
                "expanded_terms": list[str],        # flat synonym list actually used
            }
        """
        text = raw_query.strip().lower()

        # Step 1 — strip filler phrases
        for pattern in FILLER_PATTERNS:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()

        # Step 2 — extract entities (words are KEPT in the text; see module docstring).
        # Dedupe canonical values — e.g. "baital pachisi" matches two lexicon keys
        # that map to the same tradition.
        traditions_found = []
        regions_found = []
        atu_codes_found = []

        for keyword, canonical in KNOWN_TRADITIONS.items():
            if keyword in text and canonical not in traditions_found:
                traditions_found.append(canonical)

        for keyword, canonical in KNOWN_REGIONS.items():
            if keyword in text and canonical not in regions_found:
                regions_found.append(canonical)

        for pattern, code in KNOWN_ATU_CODES.items():
            if re.search(pattern, text, re.IGNORECASE) and code not in atu_codes_found:
                atu_codes_found.append(code)

        text = re.sub(r"\s{2,}", " ", text).strip()

        # Step 3 — detect boolean operators
        # Require uppercase AND/OR/NOT or explicit parentheses to distinguish
        # from natural English 'and'/'or'
        has_explicit_boolean = bool(
            re.search(r"\b(AND|OR|NOT)\b", raw_query) or re.search(r"\([^\)]+\)", raw_query)
        )
        has_implicit_boolean = any(
            re.search(p, text, re.IGNORECASE) for p, _ in BOOLEAN_PHRASE_PATTERNS
        )

        mode = "boolean" if (has_explicit_boolean or has_implicit_boolean) else "vsm"

        # Step 4 — build structured boolean query (if boolean mode)
        structured_query = text
        if has_implicit_boolean:
            structured_query = re.sub(r"\bbut not\b", " NOT ", structured_query, flags=re.IGNORECASE)
            structured_query = re.sub(r"\band not\b", " NOT ", structured_query, flags=re.IGNORECASE)
            structured_query = re.sub(r"\bboth\b", "", structured_query, flags=re.IGNORECASE)
            structured_query = re.sub(r"\band\b", " AND ", structured_query, flags=re.IGNORECASE)
            structured_query = re.sub(r"\bor\b", " OR ", structured_query, flags=re.IGNORECASE)
        elif has_explicit_boolean:
            structured_query = raw_query  # preserve the user's boolean expression

        # Step 5 — VSM normalized query
        stemmed_terms = preprocess(text)
        normalized_query = " ".join(stemmed_terms)

        # Step 6 — optional WordNet synonym expansion (VSM mode only)
        expansions: dict[str, list[str]] = {}
        if expand_synonyms and mode == "vsm" and stemmed_terms:
            expansions = expand_terms(stemmed_terms, vocabulary=vocabulary)

        filters: dict = {}
        if traditions_found:
            filters["tradition"] = traditions_found[0]
        if regions_found:
            filters["region"] = regions_found[0]
        if atu_codes_found:
            filters["tale_type"] = filters.get("tale_type") or atu_codes_found[0]

        return {
            "mode": mode,
            "original_query": raw_query,
            "normalized_query": normalized_query,
            "structured_query": structured_query.strip(),
            "entities": {
                "traditions": traditions_found,
                "regions": regions_found,
                "atu_codes": atu_codes_found,
            },
            "filters": filters,
            "stemmed_terms": stemmed_terms,
            "expansions": expansions,
            "expanded_terms": [s for syns in expansions.values() for s in syns],
        }
