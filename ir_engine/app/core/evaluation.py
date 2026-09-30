"""
evaluation.py — VaartaVerse Classical IR Engine
================================================
IR Evaluation Harness — computes standard retrieval metrics against qrels
(relevance judgements).

Unranked metrics (set-based):
    Precision = |Retrieved ∩ Relevant| / |Retrieved|
    Recall    = |Retrieved ∩ Relevant| / |Relevant|
    F1        = 2 × (P × R) / (P + R)      (computed per query, then averaged)

Ranked metrics (order-sensitive):
    Precision@K     — precision in top K results
    Average Precision (AP) per query
    Mean Average Precision (MAP) — mean of AP across all queries
    nDCG@K          — Discounted Cumulative Gain, normalized by ideal DCG

Qrels schema (injected via constructor or loaded from JSON):
    {
        "query_id": "Q-01",
        "query_text": "jackal lion well trick",
        "judgments": [
            {"tale_id": "PAN-014", "relevance_score": 3},
            ...
        ]
    }

Judgments referencing tale_ids absent from the index are dropped (and counted)
so metrics are not silently deflated by phantom qrels.

Modes: "boolean" (tf-idf-ranked boolean), "vsm", "bm25", "vsm_rocchio" (PRF).

NOTE ON SCALE: the bundled stub qrels are author-judged over a small corpus —
treat absolute numbers as illustrative, not as a benchmark. Inject your own
qrels for meaningful measurement.
"""

import json
import math
import os
from pathlib import Path
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


def load_qrels_from_json(path: str | Path) -> list[dict]:
    """Load a qrels JSON file (list of {query_id, query_text, judgments})."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    qrels = raw if isinstance(raw, list) else raw.get("qrels", [raw])
    return qrels


class EvaluationHarness:
    """
    Runs retrieval evaluation against a qrel ground truth set.

    Qrels are injected via the `qrels` constructor argument (or loaded from a
    JSON path at run time). If none are supplied, a small author-judged stub
    set is used for demonstration only.
    """

    def __init__(
        self,
        boolean_engine,
        vsm_engine,
        bm25_engine,
        rocchio,
        qrels: Optional[list[dict]] = None,
    ):
        self._boolean = boolean_engine
        self._vsm = vsm_engine
        self._bm25 = bm25_engine
        self._rocchio = rocchio
        self._qrels: list[dict] = qrels if qrels is not None else self._load_stub_qrels()

    def _load_stub_qrels(self) -> list[dict]:
        """
        Author-judged stub qrel set for 5 demonstration queries.
        Replace with real, independently-judged qrels for meaningful metrics.
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

    # ------------------------------------------------------------------
    # Retrieval dispatch
    # ------------------------------------------------------------------

    def _retrieve(self, mode: str, query_text: str) -> list[str]:
        """Execute a query with a given retrieval mode, return ordered doc_ids."""
        if mode == "boolean":
            results = self._boolean.search(query_text)
            return [r.get("tale_id", r.get("doc_id", "")) for r in results if "error" not in r]
        elif mode == "vsm":
            results = self._vsm.search(query_text, top_k=20)
            return [r.get("tale_id", r.get("doc_id", "")) for r in results]
        elif mode == "bm25":
            results = self._bm25.search(query_text, top_k=20)
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

    # ------------------------------------------------------------------
    # Main runner
    # ------------------------------------------------------------------

    def run(
        self,
        modes: list[str] = ("boolean", "vsm", "bm25", "vsm_rocchio"),
        qrel_query_ids: Optional[list[str]] = None,
        k_values: list[int] = (5, 10),
        qrels_path: Optional[str] = None,
    ) -> dict:
        """
        Run the full evaluation harness.

        Args:
            modes:          Retrieval modes to compare.
            qrel_query_ids: Restrict to specific query ids (None = all).
            k_values:       K values for P@K (and max K for nDCG).
            qrels_path:     Optional path to a qrels JSON file (overrides injected qrels).

        Returns:
            {
              "summary": {mode: {MAP, nDCG@K, P@K, Recall, F1, query_count}},
              "per_query": [...],
              "qrels_filtered": {dropped_judgments, notes},
            }
        """
        qrels = load_qrels_from_json(qrels_path) if qrels_path else self._qrels
        if qrel_query_ids:
            qrels = [q for q in qrels if q["query_id"] in qrel_query_ids]

        corpus_ids = self._vsm._index.get_all_doc_ids() if self._vsm._index.doc_count() else set()

        # Drop judgments for tale_ids absent from the corpus (phantom qrels)
        dropped = 0
        filtered_qrels = []
        for q in qrels:
            kept = [j for j in q["judgments"] if j["tale_id"] in corpus_ids]
            dropped += len(q["judgments"]) - len(kept)
            filtered_qrels.append({**q, "judgments": kept})

        summary: dict[str, dict] = {}
        per_query: list[dict] = []

        for mode in modes:
            ap_list: list[float] = []
            ndcg_list: list[float] = []
            f1_list: list[float] = []
            p_k_lists: dict[int, list[float]] = {k: [] for k in k_values}
            recall_list: list[float] = []

            for qrel in filtered_qrels:
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
                prec = precision(retrieved, relevant_set)
                recall_list.append(rec)
                f1_list.append(f1(prec, rec))

                entry: dict = {
                    "query_id": qrel["query_id"],
                    "query_text": q_text,
                    "mode": mode,
                    "ap": round(ap, 4),
                    f"ndcg@{max_k}": round(ndcg, 4),
                    "recall": round(rec, 4),
                    "precision": round(prec, 4),
                    "f1": round(f1(prec, rec), 4),
                }

                for k in k_values:
                    pk = precision_at_k(retrieved, relevant_set, k)
                    p_k_lists[k].append(pk)
                    entry[f"p@{k}"] = round(pk, 4)

                per_query.append(entry)

            n = len(filtered_qrels)
            avg = lambda xs: sum(xs) / len(xs) if xs else 0.0
            summary[mode] = {
                "MAP": round(avg(ap_list), 4),
                f"nDCG@{max(k_values)}": round(avg(ndcg_list), 4),
                **{f"P@{k}": round(avg(p_k_lists[k]), 4) for k in k_values},
                "Recall": round(avg(recall_list), 4),
                "F1": round(avg(f1_list), 4),
                "query_count": n,
            }

        return {
            "summary": summary,
            "per_query": per_query,
            "qrels_filtered": {
                "dropped_judgments": dropped,
                "note": "Judgments referencing tale_ids missing from the corpus are excluded.",
            },
        }
