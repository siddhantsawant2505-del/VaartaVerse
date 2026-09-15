"""
evaluation.py — VaartaVerse Classical IR Engine
================================================
IR Evaluation Harness — computes standard retrieval metrics against
human-curated qrels (relevance judgements).

Unranked metrics (set-based):
    Precision = |Retrieved ∩ Relevant| / |Retrieved|
    Recall    = |Retrieved ∩ Relevant| / |Relevant|
    F1        = 2 × (P × R) / (P + R)

Ranked metrics (order-sensitive):
    Precision@K     — precision in top K results
    Average Precision (AP) per query
    Mean Average Precision (MAP) — mean of AP across all queries
    nDCG@K          — Discounted Cumulative Gain, normalized by ideal DCG

Qrels schema (loaded from MongoDB or JSON file):
    {
        "query_id": "Q-01",
        "query_text": "jackal lion well trick",
        "judgments": [
            {"tale_id": "PAN-014", "relevance_score": 3},
            {"tale_id": "HIT-009", "relevance_score": 2},
            ...
        ]
    }
"""

import math
import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def precision_at_k(retrieved_ids: list[str], relevant_set: set[str], k: int) -> float:
    """P@K: fraction of top-k retrieved docs that are relevant."""
    top_k = retrieved_ids[:k]
    hits = sum(1 for doc_id in top_k if doc_id in relevant_set)
    return hits / k if k > 0 else 0.0


def recall(retrieved_ids: list[str], relevant_set: set[str]) -> float:
    """Recall: fraction of relevant docs that were retrieved."""
    if not relevant_set:
        return 0.0
    hits = sum(1 for doc_id in retrieved_ids if doc_id in relevant_set)
    return hits / len(relevant_set)


def precision(retrieved_ids: list[str], relevant_set: set[str]) -> float:
    """Precision: fraction of retrieved docs that are relevant."""
    if not retrieved_ids:
        return 0.0
    hits = sum(1 for doc_id in retrieved_ids if doc_id in relevant_set)
    return hits / len(retrieved_ids)


def f1(prec: float, rec: float) -> float:
    """Harmonic mean of precision and recall."""
    if prec + rec == 0:
        return 0.0
    return 2 * prec * rec / (prec + rec)


def average_precision(retrieved_ids: list[str], relevant_set: set[str]) -> float:
    """
    Average Precision (AP) for a single query.
    AP = (1/|relevant|) Σ_{k=1}^{n} P@k × rel(k)
    """
    if not relevant_set:
        return 0.0
    hits = 0
    running_precision_sum = 0.0
    for k, doc_id in enumerate(retrieved_ids, start=1):
        if doc_id in relevant_set:
            hits += 1
            running_precision_sum += hits / k
    return running_precision_sum / len(relevant_set)


def dcg_at_k(retrieved_ids: list[str], relevance_grades: dict[str, int], k: int) -> float:
    """
    DCG@K using graded relevance (0–3 scale).
    DCG@k = Σ_{i=1}^{k} (2^rel_i - 1) / log2(i + 1)
    """
    dcg = 0.0
    for i, doc_id in enumerate(retrieved_ids[:k], start=1):
        rel = relevance_grades.get(doc_id, 0)
        dcg += (2 ** rel - 1) / math.log2(i + 1)
    return dcg


def ndcg_at_k(retrieved_ids: list[str], relevance_grades: dict[str, int], k: int) -> float:
    """
    nDCG@K: DCG@K normalized by ideal DCG@K.
    ideal_dcg assumes docs ordered by descending relevance grade.
    """
    ideal_order = sorted(relevance_grades.values(), reverse=True)
    ideal_ids = [f"__ideal_{i}__" for i in range(len(ideal_order))]
    ideal_grades = {doc_id: grade for doc_id, grade in zip(ideal_ids, ideal_order)}
    idcg = dcg_at_k(ideal_ids, ideal_grades, k)
    if idcg == 0:
        return 0.0
    return dcg_at_k(retrieved_ids, relevance_grades, k) / idcg


class EvaluationHarness:
    """
    Runs retrieval evaluation against a qrel ground truth set.

    TODO: Load qrels from MongoDB via PyMongo when corpus and judgements are ready.
          For now, uses a hardcoded stub qrel set for demonstration.
    """

    def __init__(self, boolean_engine, vsm_engine, rocchio):
        self._boolean = boolean_engine
        self._vsm = vsm_engine
        self._rocchio = rocchio
        self._qrels: list[dict] = self._load_stub_qrels()

    def _load_stub_qrels(self) -> list[dict]:
        """
        Stub qrel set for 5 demonstration queries.
        TODO: Replace with MongoDB pymongo.collection.find() call when data is loaded.
        """
        return [
            {
                "query_id": "Q-01",
                "query_text": "smart jackal tricked arrogant lion deep well",
                "judgments": [
                    {"tale_id": "PAN-014", "relevance_score": 3},
                    {"tale_id": "HIT-009", "relevance_score": 2},
                    {"tale_id": "JAT-210", "relevance_score": 2},
                    {"tale_id": "VIK-007", "relevance_score": 1},
                ],
            },
            {
                "query_id": "Q-02",
                "query_text": "monkey crocodile river heart tree Panchatantra",
                "judgments": [
                    {"tale_id": "PAN-002", "relevance_score": 3},
                    {"tale_id": "HIT-003", "relevance_score": 3},
                    {"tale_id": "JAT-008", "relevance_score": 2},
                    {"tale_id": "PAN-007", "relevance_score": 1},
                    {"tale_id": "JAT-112", "relevance_score": 1},
                ],
            },
            {
                "query_id": "Q-03",
                "query_text": "King Vikramaditya vampire Baital riddle ethical judgment",
                "judgments": [
                    {"tale_id": "VIK-001", "relevance_score": 3},
                    {"tale_id": "VIK-002", "relevance_score": 3},
                    {"tale_id": "VIK-003", "relevance_score": 2},
                    {"tale_id": "VIK-007", "relevance_score": 2},
                    {"tale_id": "VIK-009", "relevance_score": 1},
                    {"tale_id": "PAN-019", "relevance_score": 0},
                ],
            },
            {
                "query_id": "Q-04",
                "query_text": "Birbal khichdi fire warmth emperor Akbar patience wit",
                "judgments": [
                    {"tale_id": "BIR-004", "relevance_score": 3},
                    {"tale_id": "BIR-011", "relevance_score": 2},
                    {"tale_id": "BIR-002", "relevance_score": 1},
                ],
            },
            {
                "query_id": "Q-05",
                "query_text": "Tenali Raman garden thieves well heavy stones",
                "judgments": [
                    {"tale_id": "TEN-002", "relevance_score": 3},
                    {"tale_id": "TEN-006", "relevance_score": 2},
                    {"tale_id": "TEN-009", "relevance_score": 1},
                ],
            },
        ]

    def _retrieve(self, mode: str, query_text: str) -> list[str]:
        """Execute a query with a given retrieval mode, return ordered doc_ids."""
        if mode == "boolean":
            results = self._boolean.search(query_text)
            return [r.get("tale_id", r.get("doc_id", "")) for r in results if "error" not in r]
        elif mode == "vsm":
            results = self._vsm.search(query_text, top_k=20)
            return [r.get("tale_id", r.get("doc_id", "")) for r in results]
        elif mode == "vsm_rocchio":
            # PRF: use top-3 as pseudo-relevant, then rerank
            initial = self._vsm.search(query_text, top_k=5)
            pseudo_rel = [r.get("doc_id", "") for r in initial[:3]]
            results = self._rocchio.rerank(
                query=query_text,
                relevant_ids=pseudo_rel,
                non_relevant_ids=[],
                top_k=20,
            )
            return [r.get("tale_id", r.get("doc_id", "")) for r in results]
        return []

    def run(
        self,
        modes: list[str] = ("boolean", "vsm", "vsm_rocchio"),
        qrel_query_ids: Optional[list[str]] = None,
        k_values: list[int] = (5, 10),
    ) -> dict:
        """
        Run the full evaluation harness.

        Returns:
            {
                "summary": {mode: {MAP, nDCG@10, P@5, P@10, Recall, F1}},
                "per_query": [{query_id, query_text, mode: {AP, nDCG, P@k, ...}}],
            }
        """
        qrels = self._qrels
        if qrel_query_ids:
            qrels = [q for q in qrels if q["query_id"] in qrel_query_ids]

        summary: dict[str, dict] = {}
        per_query: list[dict] = []

        for mode in modes:
            ap_list: list[float] = []
            ndcg_list: list[float] = []
            p_k_lists: dict[int, list[float]] = {k: [] for k in k_values}
            recall_list: list[float] = []

            for qrel in qrels:
                q_text = qrel["query_text"]
                judgments = qrel["judgments"]
                relevant_set = {j["tale_id"] for j in judgments if j["relevance_score"] >= 1}
                relevance_grades = {j["tale_id"]: j["relevance_score"] for j in judgments}

                retrieved = self._retrieve(mode, q_text)

                ap = average_precision(retrieved, relevant_set)
                ap_list.append(ap)

                max_k = max(k_values)
                ndcg = ndcg_at_k(retrieved, relevance_grades, max_k)
                ndcg_list.append(ndcg)

                rec = recall(retrieved, relevant_set)
                recall_list.append(rec)

                entry: dict = {
                    "query_id": qrel["query_id"],
                    "query_text": q_text,
                    "mode": mode,
                    "ap": round(ap, 4),
                    f"ndcg@{max_k}": round(ndcg, 4),
                    "recall": round(rec, 4),
                }

                for k in k_values:
                    pk = precision_at_k(retrieved, relevant_set, k)
                    p_k_lists[k].append(pk)
                    entry[f"p@{k}"] = round(pk, 4)

                per_query.append(entry)

            avg_recall = sum(recall_list) / len(recall_list) if recall_list else 0.0
            avg_p5 = sum(p_k_lists[5]) / len(p_k_lists[5]) if 5 in p_k_lists and p_k_lists[5] else 0.0
            avg_map = sum(ap_list) / len(ap_list) if ap_list else 0.0
            avg_ndcg = sum(ndcg_list) / len(ndcg_list) if ndcg_list else 0.0

            summary[mode] = {
                "MAP": round(avg_map, 4),
                f"nDCG@{max(k_values)}": round(avg_ndcg, 4),
                "P@5": round(avg_p5, 4),
                "Recall": round(avg_recall, 4),
                "F1": round(f1(avg_p5, avg_recall), 4),
                "query_count": len(qrels),
            }

        return {"summary": summary, "per_query": per_query}
