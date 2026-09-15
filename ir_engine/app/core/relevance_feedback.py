"""
relevance_feedback.py — VaartaVerse Classical IR Engine
========================================================
Rocchio Relevance Feedback — explicit and pseudo-relevance variants.

Rocchio's modified query formula:
    q_m = α·q₀ + β·(1/|Dr|)·Σ_{d∈Dr} d_vec - γ·(1/|Dnr|)·Σ_{d∈Dnr} d_vec

Where:
    q₀       — original query TF-IDF vector
    Dr        — set of documents judged relevant
    Dnr       — set of documents judged non-relevant
    α, β, γ  — configurable hyper-parameters (defaults: 1.0, 0.75, 0.15)

After computing q_m, we re-run VSM retrieval with the modified vector.

Pseudo-Relevance Feedback (PRF / Blind Feedback):
    Assume top-k documents from initial VSM run are relevant (Dr),
    no Dnr, then apply Rocchio expansion.
"""

import math
from typing import Optional

from app.core.vsm_engine import VSMEngine
from app.core.preprocessing import preprocess


def _vec_add(a: dict[str, float], b: dict[str, float], scale: float = 1.0) -> dict[str, float]:
    result = dict(a)
    for term, weight in b.items():
        result[term] = result.get(term, 0.0) + scale * weight
    return result


def _vec_scale(v: dict[str, float], s: float) -> dict[str, float]:
    return {t: w * s for t, w in v.items()}


def _vec_norm(v: dict[str, float]) -> float:
    return math.sqrt(sum(w ** 2 for w in v.values()))


def _cosine_sim_from_vec(q_vec: dict[str, float], d_vec: dict[str, float]) -> float:
    """Cosine similarity between two sparse TF-IDF vectors."""
    dot = sum(q_vec.get(t, 0.0) * w for t, w in d_vec.items())
    q_n = _vec_norm(q_vec)
    d_n = _vec_norm(d_vec)
    if q_n == 0 or d_n == 0:
        return 0.0
    return dot / (q_n * d_n)


class RocchioFeedback:
    """
    Rocchio explicit and pseudo-relevance feedback.

    Modifies the query vector using relevance judgements, then re-retrieves.
    """

    def __init__(self, vsm: VSMEngine):
        self._vsm = vsm

    def _build_query_vector(self, query: str) -> dict[str, float]:
        """Build a TF-IDF query vector from raw query text."""
        index = self._vsm._index
        N = index.doc_count()
        terms = preprocess(query)
        tf_map: dict[str, int] = {}
        for t in terms:
            tf_map[t] = tf_map.get(t, 0) + 1

        vec: dict[str, float] = {}
        for term, tf in tf_map.items():
            df = index.get_df(term)
            if df == 0:
                continue
            idf = math.log((N + 1) / (df + 1))
            vec[term] = (1.0 + math.log(tf)) * idf if tf > 0 else 0.0
        return vec

    def _centroid(self, doc_ids: list[str]) -> dict[str, float]:
        """Compute centroid of a set of document TF-IDF vectors."""
        if not doc_ids:
            return {}
        centroid: dict[str, float] = {}
        for doc_id in doc_ids:
            d_vec = self._vsm.get_document_vector(doc_id)
            for term, weight in d_vec.items():
                centroid[term] = centroid.get(term, 0.0) + weight
        n = len(doc_ids)
        return {t: w / n for t, w in centroid.items()}

    def rerank(
        self,
        query: str,
        relevant_ids: list[str],
        non_relevant_ids: list[str],
        top_k: int = 10,
        alpha: float = 1.0,
        beta: float = 0.75,
        gamma: float = 0.15,
    ) -> list[dict]:
        """
        Apply Rocchio modification and re-retrieve top-K documents.

        Args:
            query:           Original query text.
            relevant_ids:    Doc IDs marked relevant by user.
            non_relevant_ids: Doc IDs marked non-relevant.
            top_k:           Number of results to return.
            alpha, beta, gamma: Rocchio hyper-parameters.

        Returns:
            Re-ranked list of result dicts with updated cosine scores.
        """
        q0 = self._build_query_vector(query)
        dr_centroid = self._centroid(relevant_ids)
        dnr_centroid = self._centroid(non_relevant_ids)

        # q_m = α·q₀ + β·centroid(Dr) - γ·centroid(Dnr)
        q_m = _vec_scale(q0, alpha)
        q_m = _vec_add(q_m, dr_centroid, scale=beta)
        q_m = _vec_add(q_m, dnr_centroid, scale=-gamma)

        # Clip negative weights to 0 (Rocchio standard practice)
        q_m = {t: max(0.0, w) for t, w in q_m.items()}

        # Re-rank all documents using modified query vector
        index = self._vsm._index
        all_doc_ids = index.get_all_doc_ids()
        scored: list[tuple[float, str]] = []

        for doc_id in all_doc_ids:
            d_vec = self._vsm.get_document_vector(doc_id)
            sim = _cosine_sim_from_vec(q_m, d_vec)
            scored.append((sim, doc_id))

        scored.sort(reverse=True)

        results = []
        for score, doc_id in scored[:top_k]:
            meta = index.get_doc_meta(doc_id)
            if meta:
                from dataclasses import asdict
                result = asdict(meta)
                result["score"] = round(score, 6)
                result["feedback_applied"] = True
                results.append(result)

        return results

    def pseudo_relevance_feedback(
        self,
        query: str,
        top_k: int = 10,
        prf_k: int = 3,
        beta: float = 0.75,
    ) -> list[dict]:
        """
        Blind/Pseudo-Relevance Feedback (PRF).
        Assumes top-prf_k initial VSM results are relevant (no user input needed).

        Args:
            query:   Original query.
            top_k:   Final number of results.
            prf_k:   Number of top initial results to treat as pseudo-relevant.
            beta:    Centroid weight (gamma=0 since no non-relevant set).
        """
        initial = self._vsm.search(query, top_k=prf_k)
        pseudo_relevant_ids = [r["doc_id"] for r in initial if "doc_id" in r]
        return self.rerank(
            query=query,
            relevant_ids=pseudo_relevant_ids,
            non_relevant_ids=[],
            top_k=top_k,
            alpha=1.0,
            beta=beta,
            gamma=0.0,
        )
