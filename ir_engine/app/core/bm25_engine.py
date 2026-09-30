"""
bm25_engine.py — VaartaVerse Classical IR Engine
=================================================
BM25 (Okapi) ranking function — the standard classical probabilistic baseline.

    score(q, d) = Σ_{t ∈ q} idf(t) × (tf × (k1 + 1)) / (tf + k1 × (1 - b + b × |d|/avgdl))

    idf(t) = log(1 + (N - df + 0.5) / (df + 0.5))   (BM25+ style, always positive)

Zone handling: a match in the title contributes an extra title_boost multiplier
to that term's contribution (applied to the tf-driven part). k1, b and
title_boost are configurable per request.

BM25 uses raw term frequencies (not sublinear-scaled) and document length
normalization, which is exactly what plain TF-IDF lacks.
"""

import heapq
import math
from dataclasses import asdict
from typing import Optional

from app.core.inverted_index import InvertedIndex
from app.core.preprocessing import preprocess


class BM25Engine:
    """Okapi BM25 ranking over the same inverted index used by the VSM engine."""

    def __init__(self, index: InvertedIndex, k1: float = 1.5, b: float = 0.75):
        self._index = index
        self.k1 = k1
        self.b = b
        self._doc_len: dict[str, int] = {}
        self._avgdl: float = 0.0
        self._computed_for: Optional[int] = None  # N the stats were computed for

    # ------------------------------------------------------------------
    # Corpus statistics (computed lazily, invalidated on N change)
    # ------------------------------------------------------------------

    def _ensure_stats(self) -> None:
        N = self._index.doc_count()
        if self._computed_for == N and self._doc_len:
            return
        self._doc_len = {}
        total = 0
        for term, postings in self._index.postings_items():
            for doc_id, entry in postings.items():
                self._doc_len[doc_id] = self._doc_len.get(doc_id, 0) + entry.tf
                total += entry.tf
        n_docs = len(self._doc_len)
        self._avgdl = (total / n_docs) if n_docs else 0.0
        self._computed_for = N

    # ------------------------------------------------------------------
    # Public search
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 10,
        k1: Optional[float] = None,
        b: Optional[float] = None,
        title_boost: float = 1.5,
        collection_filter: Optional[str] = None,
        region_filter: Optional[str] = None,
    ) -> list[dict]:
        """
        Rank documents by BM25 for the query.

        Args:
            query:        Raw query text.
            top_k:        Number of results.
            k1:           TF saturation (default 1.5).
            b:            Length normalization strength (default 0.75).
            title_boost:  Multiplier for term occurrences in the title zone.
        """
        k1 = self.k1 if k1 is None else float(k1)
        b = self.b if b is None else float(b)

        query_terms = preprocess(query)
        if not query_terms:
            return []

        N = self._index.doc_count()
        if N == 0:
            return []

        self._ensure_stats()
        if not self._doc_len or self._avgdl <= 0:
            return []

        query_tf: dict[str, int] = {}
        for t in query_terms:
            query_tf[t] = query_tf.get(t, 0) + 1

        scores: dict[str, float] = {}
        matched_terms: dict[str, set[str]] = {}

        for term, _qtf in query_tf.items():
            postings = self._index.get_postings(term)
            df = len(postings)
            if df == 0:
                continue
            idf = math.log(1.0 + (N - df + 0.5) / (df + 0.5))
            for doc_id, entry in postings.items():
                meta = self._index.get_doc_meta(doc_id)
                if meta is None:
                    continue
                if collection_filter and collection_filter.lower() not in meta.source_collection.lower():
                    continue
                if region_filter and region_filter.lower() not in meta.region.lower():
                    continue

                # Effective tf with title-zone boost
                tf_title = len(entry.zones.get("title", []))
                tf_body = len(entry.zones.get("body", []))
                eff_tf = tf_body + title_boost * tf_title

                dl = self._doc_len.get(doc_id, 1)
                denom = eff_tf + k1 * (1.0 - b + b * dl / self._avgdl)
                contrib = idf * eff_tf * (k1 + 1.0) / denom if denom > 0 else 0.0

                scores[doc_id] = scores.get(doc_id, 0.0) + contrib
                matched_terms.setdefault(doc_id, set()).add(term)

        top = heapq.nlargest(top_k, scores.items(), key=lambda x: x[1])

        results = []
        for doc_id, score in top:
            meta = self._index.get_doc_meta(doc_id)
            if meta is None:
                continue
            result = asdict(meta)
            result["score"] = round(score, 6)
            result["engine"] = "bm25"
            result["bm25_params"] = {"k1": k1, "b": b, "title_boost": title_boost}
            result["terms_matched"] = sorted(matched_terms.get(doc_id, set()))
            results.append(result)

        return results
