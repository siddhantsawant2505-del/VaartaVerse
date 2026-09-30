"""
vsm_engine.py — VaartaVerse Classical IR Engine
================================================
Vector Space Model (VSM) with TF-IDF scoring and zone/field weighting.

Scoring: cosine similarity between query and document TF-IDF vectors.

    idf(t)               = log(1 + N / df_t)            (always > 0, even df = N)
    tf_weight(tf)        = 1 + log(tf)                  (sublinear scaling)
    doc weight w(t,d)    = (w_title·tfw(title_tf) + w_body·tfw(body_tf)) × idf(t)
    query weight w(t,q)  = tfw(qtf) × idf(t)
    cosine(q, d)         = dot(q, d) / (|q| × |d|)

Zone weighting note: document norms are computed over the FULL document vector
(all indexed terms for the doc), not just query terms. This is what makes the
title boost survive cosine normalization — a title match genuinely outranks an
equivalent body match. Norms are cached per zone-weight configuration.

No silent fallbacks: a query with no indexable terms returns [] (the API layer
pre-validates and returns HTTP 422 for stopword-only queries).
"""

import heapq
import math
from dataclasses import asdict
from typing import Optional

from app.core.inverted_index import InvertedIndex
from app.core.preprocessing import preprocess

# Zone weights are BOOST MULTIPLIERS (title matches count 2x body matches),
# not a weight distribution. With the original 0.35/0.65 "distribution" a body
# match outranked a title match — the opposite of the documented "title boost".
DEFAULT_ZONE_WEIGHTS = {"title": 2.0, "body": 1.0}


def _sublinear_tf(tf: int) -> float:
    """Sublinear TF scaling: 1 + log(tf) if tf > 0 else 0."""
    return 1.0 + math.log(tf) if tf > 0 else 0.0


class VSMEngine:
    """
    TF-IDF Vector Space Model retrieval engine.

    Documents and queries are represented as sparse TF-IDF weighted vectors.
    Cosine similarity is computed via dot product over shared terms (efficient
    for sparse high-dimensional space).
    """

    def __init__(self, index: InvertedIndex):
        self._index = index
        # (N, title_w, body_w) → {doc_id: full-vector norm}
        self._doc_norm_cache: dict[tuple[float, float, float], dict[str, float]] = {}

    # ------------------------------------------------------------------
    # Document norms (full-vector, zone-weighted, cached)
    # ------------------------------------------------------------------

    def _doc_norms(self, title_w: float, body_w: float) -> dict[str, float]:
        """
        Cosine denominator per document: |d| over the FULL document TF-IDF
        vector with zone weighting. Cached per (N, title_w, body_w); cache is
        invalidated when the API layer resets engine singletons after ingestion.
        """
        N = self._index.doc_count()
        key = (float(N), float(title_w), float(body_w))
        cached = self._doc_norm_cache.get(key)
        if cached is not None:
            return cached

        sq: dict[str, float] = {}
        for term, postings in self._index.postings_items():
            df = len(postings)
            if df == 0:
                continue
            idf = math.log(1.0 + N / df)
            for doc_id, entry in postings.items():
                tf_title = len(entry.zones.get("title", []))
                tf_body = len(entry.zones.get("body", []))
                w = (title_w * _sublinear_tf(tf_title) + body_w * _sublinear_tf(tf_body)) * idf
                sq[doc_id] = sq.get(doc_id, 0.0) + w * w

        norms = {doc_id: math.sqrt(v) for doc_id, v in sq.items() if v > 0}
        self._doc_norm_cache[key] = norms
        return norms

    # ------------------------------------------------------------------
    # Public search
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 10,
        zone_weights: Optional[dict] = None,
        collection_filter: Optional[str] = None,
        region_filter: Optional[str] = None,
    ) -> list[dict]:
        """
        Rank documents by cosine similarity to query using TF-IDF with zone weighting.

        Returns top_k results sorted by descending score. Empty list if the
        query has no indexable terms or the index is empty.
        """
        zw = dict(zone_weights) if zone_weights else dict(DEFAULT_ZONE_WEIGHTS)
        title_w = float(zw.get("title", 2.0))
        body_w = float(zw.get("body", 1.0))

        query_terms = preprocess(query)
        if not query_terms:
            return []

        N = self._index.doc_count()
        if N == 0:
            return []

        # Build query TF-IDF vector (term → weight)
        query_tf: dict[str, int] = {}
        for t in query_terms:
            query_tf[t] = query_tf.get(t, 0) + 1

        query_vec: dict[str, float] = {}
        for term, tf in query_tf.items():
            df = self._index.get_df(term)
            if df == 0:
                continue
            idf = math.log(1.0 + N / df)
            query_vec[term] = _sublinear_tf(tf) * idf

        if not query_vec:
            return []  # no query term exists in the vocabulary

        q_norm = math.sqrt(sum(w ** 2 for w in query_vec.values()))
        if q_norm == 0:
            return []

        # Accumulate dot products per document (inverted-index traversal)
        dots: dict[str, float] = {}
        for term, q_weight in query_vec.items():
            postings = self._index.get_postings(term)
            df = len(postings)
            idf = math.log(1.0 + N / df)
            for doc_id, entry in postings.items():
                meta = self._index.get_doc_meta(doc_id)
                if meta is None:
                    continue
                if collection_filter and collection_filter.lower() not in meta.source_collection.lower():
                    continue
                if region_filter and region_filter.lower() not in meta.region.lower():
                    continue

                tf_title = len(entry.zones.get("title", []))
                tf_body = len(entry.zones.get("body", []))
                d_weight = (title_w * _sublinear_tf(tf_title) + body_w * _sublinear_tf(tf_body)) * idf
                dots[doc_id] = dots.get(doc_id, 0.0) + q_weight * d_weight

        # Cosine normalization against full document norms
        doc_norms = self._doc_norms(title_w, body_w)
        cosine_scores: dict[str, float] = {}
        for doc_id, dot in dots.items():
            d_norm = doc_norms.get(doc_id)
            if not d_norm:
                continue
            cosine_scores[doc_id] = dot / (q_norm * d_norm)

        top = heapq.nlargest(top_k, cosine_scores.items(), key=lambda x: x[1])

        results = []
        for doc_id, score in top:
            meta = self._index.get_doc_meta(doc_id)
            if meta is None:
                continue
            result = asdict(meta)
            result["score"] = round(score, 6)
            result["zone_weights"] = {"title": title_w, "body": body_w}
            result["terms_matched"] = [
                t for t in query_vec if doc_id in self._index.get_postings(t)
            ]
            results.append(result)

        return results

    def get_document_vector(self, doc_id: str) -> dict[str, float]:
        """
        Return the full TF-IDF vector for a document as {term: weight}.
        Used by Rocchio feedback and divergence computation.

        Note: O(vocabulary) per call — acceptable at demo-corpus scale;
        precompute and cache if the corpus grows beyond a few thousand docs.
        """
        N = self._index.doc_count()
        if N == 0:
            return {}

        vec: dict[str, float] = {}
        for term, postings in self._index.postings_items():
            entry = postings.get(doc_id)
            if entry is None:
                continue
            df = len(postings)
            idf = math.log(1.0 + N / df)
            vec[term] = _sublinear_tf(entry.tf) * idf
        return vec
