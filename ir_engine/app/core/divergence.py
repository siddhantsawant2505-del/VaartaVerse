"""
divergence.py — VaartaVerse Classical IR Engine
================================================
Pairwise Cosine Divergence Calculator.

For a given tale_type_id, retrieves all variant doc vectors from the VSM engine
and computes a full N×N pairwise similarity matrix.

Also computes:
    - Vocabulary overlap % between each pair (|V_a ∩ V_b| / |V_a ∪ V_b|)
    - Jaccard similarity on term sets (binary)
    - Centroid vector for the entire tale-type cluster

This module is entirely within the classical IR toolkit — no LLMs or embeddings.
"""

import math
from dataclasses import asdict
from typing import Optional

from app.core.vsm_engine import VSMEngine


def _cosine_sim(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    """Cosine similarity between two sparse TF-IDF vectors."""
    if not vec_a or not vec_b:
        return 0.0
    shared_terms = set(vec_a) & set(vec_b)
    dot = sum(vec_a[t] * vec_b[t] for t in shared_terms)
    norm_a = math.sqrt(sum(w ** 2 for w in vec_a.values()))
    norm_b = math.sqrt(sum(w ** 2 for w in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _jaccard_sim(terms_a: set[str], terms_b: set[str]) -> float:
    """Jaccard similarity: |A ∩ B| / |A ∪ B|"""
    union = terms_a | terms_b
    if not union:
        return 0.0
    return len(terms_a & terms_b) / len(union)


def _vocab_overlap_pct(terms_a: set[str], terms_b: set[str]) -> float:
    """Shared vocabulary percentage relative to the union."""
    union = terms_a | terms_b
    if not union:
        return 0.0
    return 100.0 * len(terms_a & terms_b) / len(union)


class DivergenceCalculator:
    """
    Computes pairwise divergence between all variants of a given tale-type.

    Uses the VSM engine's TF-IDF document vectors for all comparisons.
    """

    def __init__(self, vsm: VSMEngine):
        self._vsm = vsm

    def compute_pairwise_matrix(self, tale_type_id: str) -> Optional[dict]:
        """
        Build full N×N pairwise cosine similarity matrix for a tale type.

        Returns:
            {
                "tale_type_id": str,
                "variants": [DocMeta dicts],
                "matrix": [
                    {
                        "source_a": tale_id_a, "source_b": tale_id_b,
                        "cosine_similarity": float,
                        "jaccard_similarity": float,
                        "vocab_overlap_pct": float,
                    },
                    ...
                ],
                "centroid_top_terms": list[str],  # most distinctive shared terms
                "summary": {avg_sim, min_sim, max_sim, most_similar_pair, most_divergent_pair}
            }
        """
        index = self._vsm._index
        variant_metas = index.get_variants_by_tale_type(tale_type_id)

        if not variant_metas:
            return None

        # Build doc_id → TF-IDF vector mapping
        doc_vectors: dict[str, dict[str, float]] = {}
        for meta in variant_metas:
            doc_id = meta["doc_id"]
            doc_vectors[doc_id] = self._vsm.get_document_vector(doc_id)

        doc_ids = list(doc_vectors.keys())
        n = len(doc_ids)

        # Pairwise comparisons
        matrix_entries: list[dict] = []
        sim_values: list[float] = []

        for i in range(n):
            for j in range(i + 1, n):
                id_a, id_b = doc_ids[i], doc_ids[j]
                vec_a, vec_b = doc_vectors[id_a], doc_vectors[id_b]

                cos_sim = _cosine_sim(vec_a, vec_b)
                terms_a = set(t for t, w in vec_a.items() if w > 0)
                terms_b = set(t for t, w in vec_b.items() if w > 0)
                jacc = _jaccard_sim(terms_a, terms_b)
                overlap_pct = _vocab_overlap_pct(terms_a, terms_b)

                # Retrieve tale_id for display
                meta_a = index.get_doc_meta(id_a)
                meta_b = index.get_doc_meta(id_b)
                tale_id_a = meta_a.tale_id if meta_a else id_a
                tale_id_b = meta_b.tale_id if meta_b else id_b

                entry = {
                    "source_a": tale_id_a,
                    "source_b": tale_id_b,
                    "doc_id_a": id_a,
                    "doc_id_b": id_b,
                    "cosine_similarity": round(cos_sim, 4),
                    "jaccard_similarity": round(jacc, 4),
                    "vocab_overlap_pct": round(overlap_pct, 2),
                }
                matrix_entries.append(entry)
                sim_values.append(cos_sim)

        # Summary statistics
        if sim_values:
            avg_sim = sum(sim_values) / len(sim_values)
            most_similar = max(matrix_entries, key=lambda x: x["cosine_similarity"])
            most_divergent = min(matrix_entries, key=lambda x: x["cosine_similarity"])
        else:
            avg_sim = 0.0
            most_similar = most_divergent = {}

        # Centroid — top N terms with highest average weight across all variants
        centroid: dict[str, float] = {}
        for vec in doc_vectors.values():
            for term, weight in vec.items():
                centroid[term] = centroid.get(term, 0.0) + weight
        n_docs = len(doc_vectors)
        centroid = {t: w / n_docs for t, w in centroid.items()}
        centroid_top_terms = sorted(centroid, key=lambda t: centroid[t], reverse=True)[:20]

        return {
            "tale_type_id": tale_type_id,
            "variant_count": n,
            "variants": variant_metas,
            "matrix": matrix_entries,
            "centroid_top_terms": centroid_top_terms,
            "summary": {
                "avg_cosine_similarity": round(avg_sim, 4),
                "min_cosine_similarity": round(min(sim_values), 4) if sim_values else 0.0,
                "max_cosine_similarity": round(max(sim_values), 4) if sim_values else 0.0,
                "most_similar_pair": most_similar,
                "most_divergent_pair": most_divergent,
            },
        }
