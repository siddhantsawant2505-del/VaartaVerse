"""
query_expansion.py — VaartaVerse Classical IR Engine
=====================================================
WordNet-based synonym query expansion.

For each (already stemmed) query term, look up its first WordNet synset group
among noun → adjective → verb, and collect up to `max_per_term` single-word
synonym lemmas that (after the same preprocessing) exist in the index
vocabulary. Multi-word lemmas ("play a joke on") and the original term itself
are excluded.

The caller weights each synonym BELOW the original term (expansion_weight,
default 0.3), so original keywords dominate ranking — expansion widens recall
without hijacking it.

Design rules:
    - POS priority n → a → v: "clever" has no noun synsets but rich adjective
      ones (cunning, ingenious); "well" resolves via its noun sense only.
    - Only synonyms present in the index vocabulary are returned — pure noise
      ("canis aureus", "fountainhead") never enters the query vector unless a
      document actually contains it.
    - Deterministic: synset order from WordNet, dedupe preserving order.
"""

from typing import Optional

import nltk
from nltk.corpus import wordnet
from nltk.corpus.reader.wordnet import Synset

from app.core.preprocessing import preprocess

# POS priority for synset lookup
_POS_ORDER = ("n", "a", "v")


def _ensure_wordnet() -> bool:
    """Ensure WordNet corpora are available. Returns False if offline/missing."""
    for resource in ("wordnet", "omw-1.4"):
        try:
            nltk.data.find(f"corpora/{resource}")
        except LookupError:
            try:
                nltk.download(resource, quiet=True)
            except Exception:
                return False
    try:
        wordnet.synsets("test")
        return True
    except Exception:
        return False


_WORDNET_OK: Optional[bool] = None


def wordnet_available() -> bool:
    global _WORDNET_OK
    if _WORDNET_OK is None:
        _WORDNET_OK = _ensure_wordnet()
    return _WORDNET_OK


def _synonyms_for(term: str, max_synsets: int, max_per_term: int) -> list[str]:
    """Single-word in-vocabulary synonyms for one term (order-preserving)."""
    synsets: list[Synset] = []
    for pos in _POS_ORDER:
        found = wordnet.synsets(term, pos=pos)
        if found:
            synsets = found[:max_synsets]
            break
    if not synsets:
        return []

    out: list[str] = []
    seen: set[str] = {term}
    for syn in synsets:
        for lemma in syn.lemmas():
            name = lemma.name().lower().replace("_", " ")
            if " " in name or name in seen:  # skip multi-word lemmas and dupes
                continue
            # Stem the synonym so it lands in the same space as the index
            stems = preprocess(name)
            if len(stems) != 1:
                continue  # lemmatization collapsed/expanded it — too noisy
            stem = stems[0]
            if stem in seen:
                continue
            seen.add(stem)
            out.append(stem)
            if len(out) >= max_per_term:
                return out
    return out


def expand_terms(
    terms: list[str],
    vocabulary: Optional[set[str]] = None,
    max_synsets: int = 3,
    max_per_term: int = 3,
) -> dict[str, list[str]]:
    """
    Expand stemmed query terms with WordNet synonyms.

    Args:
        terms:        Stemmed query terms (output of preprocess()).
        vocabulary:   The index vocabulary. When provided, synonyms are kept
                      only if they exist in it (recommended).
        max_synsets:  Synsets to inspect per term (per POS, first matching POS).
        max_per_term: Maximum synonyms kept per term.

    Returns:
        {original_term: [synonym_stems]} — terms with no synonyms are omitted.
    """
    if not wordnet_available():
        return {}

    expansions: dict[str, list[str]] = {}
    all_terms = set(terms)
    for term in dict.fromkeys(terms):  # dedupe, preserve order
        syns = _synonyms_for(term, max_synsets, max_per_term)
        # Never re-add a term that is itself part of the query
        syns = [s for s in syns if s not in all_terms]
        if vocabulary is not None:
            syns = [s for s in syns if s in vocabulary]
        if syns:
            expansions[term] = syns
    return expansions
