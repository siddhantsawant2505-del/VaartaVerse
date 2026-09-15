"""
vsm_engine.py — VaartaVerse Classical IR Engine
================================================
Vector Space Model (VSM) with TF-IDF scoring and zone/field weighting.

Scoring formula per document d for query q:
    score(q, d) = Σ_t [ tf_weight(t,d,zone) × idf(t) × tf_idf_query(t,q) ]

Where:
    tf_weight(t, d, zone) = (1 + log(tf_t_d)) × (w_title × tf_title + w_body × tf_body)
    idf(t)                = log((N + 1) / (df_t + 1))   [smoothed]
    cosine_sim            = dot(q_vec, d_vec) / (|q_vec| × |d_vec|)

Zone weights are configurable per-request (default: title=0.35, body=0.65).
Top-K retrieval uses a max-heap for efficiency.
"""

import heapq
import math
from dataclasses import asdict
from typing import Optional

from app.core.inverted_index import InvertedIndex
from app.core.preprocessing import preprocess


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

    # ------------------------------------------------------------------
    # Public Interface
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

        Returns top_k results sorted by descending score.
        """
        if zone_weights is None:
            zone_weights = {"title": 0.35, "body": 0.65}

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
            idf = math.log((N + 1) / (df + 1))
            query_vec[term] = _sublinear_tf(tf) * idf

        # Accumulate scores per document (inverted-index traversal)
        scores: dict[str, float] = {}
        doc_vec_sq_norms: dict[str, float] = {}

        for term, q_weight in query_vec.items():
            postings = self._index.get_postings(term)
            for doc_id, entry in postings.items():
                meta = self._index.get_doc_meta(doc_id)
                if meta is None:
                    continue
                # Apply corpus metadata filters
                if collection_filter and collection_filter.lower() not in meta.source_collection.lower():
                    continue
                if region_filter and region_filter.lower() not in meta.region.lower():
                    continue

                # Zone-weighted TF
                title_positions = entry.zones.get("title", []) if isinstance(entry.zones, dict) else []
                body_positions = entry.zones.get("body", []) if isinstance(entry.zones, dict) else []
                tf_title = len(title_positions) if isinstance(title_positions, list) else 0
                tf_body = len(body_positions) if isinstance(body_positions, list) else (entry.tf - tf_title)

                zone_score = (
                    zone_weights.get("title", 0.35) * _sublinear_tf(tf_title)
                    + zone_weights.get("body", 0.65) * _sublinear_tf(tf_body)
                )

                df = self._index.get_df(term)
                idf = math.log((N + 1) / (df + 1))
                d_weight = zone_score * idf

                scores[doc_id] = scores.get(doc_id, 0.0) + q_weight * d_weight
                doc_vec_sq_norms[doc_id] = doc_vec_sq_norms.get(doc_id, 0.0) + d_weight ** 2

        # Cosine normalization
        q_norm = math.sqrt(sum(w ** 2 for w in query_vec.values()))
        if q_norm == 0:
            return []

        cosine_scores: dict[str, float] = {}
        for doc_id, dot in scores.items():
            d_norm = math.sqrt(doc_vec_sq_norms.get(doc_id, 1.0))
            if d_norm == 0:
                continue
            cosine_scores[doc_id] = dot / (q_norm * d_norm)

        # Top-K via max-heap
        top = heapq.nlargest(top_k, cosine_scores.items(), key=lambda x: x[1])

        results = []
        for doc_id, score in top:
            meta = self._index.get_doc_meta(doc_id)
            if meta:
                result = asdict(meta)
                result["score"] = round(score, 6)
                result["zone_weights"] = zone_weights
                # Matched stems for snippet highlighting
                result["terms_matched"] = [
                    t for t in query_vec if t in self._index.get_postings(t)
                    and doc_id in self._index.get_postings(t)
                ]
                results.append(result)

        return results

    def get_document_vector(self, doc_id: str) -> dict[str, float]:
        """
        Return the full TF-IDF vector for a document as {term: weight}.
        Used by Rocchio feedback and divergence computation.
        """
        N = self._index.doc_count()
        if N == 0:
            return {}

        vec: dict[str, float] = {}
        for term in self._index.vocabulary():
            postings = self._index.get_postings(term)
            if doc_id not in postings:
                continue
            tf = postings[doc_id].tf
            df = self._index.get_df(term)
            idf = math.log((N + 1) / (df + 1))
            vec[term] = _sublinear_tf(tf) * idf
        return vec
