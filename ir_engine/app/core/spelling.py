"""
spelling.py — VaartaVerse Classical IR Engine
==============================================
Conservative typo correction against the index vocabulary.

Bounded Levenshtein DP (early exit above max_distance, band-pruned rows) finds
the closest vocabulary term within edit distance 1–2 for query terms the
retriever cannot match.

Correction policy (deliberately conservative — a wrong "fix" silently loses
relevant documents, so ambiguity resolves to *no* correction):

    distance 1  →  allowed even when several candidates tie
                  (1 edit rarely produces an unrelated word)
    distance 2  →  only when the closest candidate is unique
                  (ties resolve to no correction)

Never corrected:
    - terms already in the vocabulary
    - numbers
    - terms shorter than 3 characters
    - terms whose closest neighbors straddle two different first characters
      (a 1–2 edit typo rarely changes the leading letter... and when it does,
      the collision guard above already handles the risky cases)
"""

import re
from typing import Optional


def levenshtein_within(a: str, b: str, max_distance: int) -> int:
    """
    Levenshtein distance between a and b, bounded by max_distance.
    Returns max_distance + 1 as soon as the distance provably exceeds it.
    """
    la, lb = len(a), len(b)
    if abs(la - lb) > max_distance:
        return max_distance + 1

    # DP over rows; each row is pruned to a band around the diagonal
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        curr = [i] + [0] * lb
        row_min = curr[0]
        lo = max(1, i - max_distance)
        hi = min(lb, i + max_distance)
        for j in range(1, lb + 1):
            if j < lo or j > hi:
                curr[j] = max_distance + 1
                continue
            cost = 0 if a[i - 1] == b[j - 1] else 1
            curr[j] = min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost)
            row_min = min(row_min, curr[j])
        if row_min > max_distance:
            return max_distance + 1
        prev = curr
    return prev[lb]


_NUMBER_RE = re.compile(r"^\d+$")


def _correctable(term: str, vocabulary: set[str]) -> bool:
    """Cheap pre-checks before running DP against the vocabulary."""
    if term in vocabulary:
        return False
    if len(term) < 3 or _NUMBER_RE.match(term):
        return False
    return True


def correct_term(
    term: str,
    vocabulary: set[str],
    max_distance: int = 2,
) -> Optional[str]:
    """
    Closest in-vocabulary correction for one term, or None.

    Policy: distance-1 matches always correct (ties included);
    distance-2 requires a unique nearest neighbor.
    """
    if not _correctable(term, vocabulary):
        return None

    # Band by length: edits 1–2 change length by at most 2
    len_lo = max(1, len(term) - max_distance)
    len_hi = len(term) + max_distance

    best: Optional[str] = None
    best_dist = max_distance + 1
    best_count = 0

    for cand in vocabulary:
        if not (len_lo <= len(cand) <= len_hi):
            continue
        d = levenshtein_within(term, cand, max_distance)
        if d > max_distance:
            continue
        if d < best_dist:
            best, best_dist, best_count = cand, d, 1
        elif d == best_dist:
            best_count += 1

    if best is None:
        return None
    if best_dist == 2 and best_count > 1:
        return None  # ambiguous at distance 2 — refuse to guess
    return best


def correct_terms(
    terms: list[str],
    vocabulary: set[str],
    max_distance: int = 2,
) -> dict[str, str]:
    """
    Correct a list of query terms.

    Returns:
        {original_term: corrected_term} — only terms that were changed.
    """
    out: dict[str, str] = {}
    for term in dict.fromkeys(terms):  # dedupe, preserve order
        fixed = correct_term(term, vocabulary, max_distance)
        if fixed:
            out[term] = fixed
    return out
