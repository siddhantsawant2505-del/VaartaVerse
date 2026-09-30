"""Evaluation metric formulas verified against hand-computed values."""

from app.core.evaluation import (
    average_precision,
    dcg_at_k,
    f1,
    ndcg_at_k,
    precision,
    precision_at_k,
    recall,
)


class TestSetMetrics:
    def test_precision_recall(self):
        retrieved = ["A", "B", "C", "D"]
        relevant = {"B", "D", "E"}
        assert precision(retrieved, relevant) == 0.5
        assert recall(retrieved, relevant) == 2 / 3

    def test_f1_hand_computed(self):
        # P=0.5, R=2/3 → F1 = 2*(0.5*2/3)/(0.5+2/3) = (2/3)/(7/6) = 4/7
        assert abs(f1(0.5, 2 / 3) - 4 / 7) < 1e-9

    def test_f1_zero_when_both_zero(self):
        assert f1(0.0, 0.0) == 0.0

    def test_empty_retrieved(self):
        assert precision([], {"A"}) == 0.0
        assert recall([], {"A"}) == 0.0

    def test_empty_relevant(self):
        assert precision(["A"], set()) == 0.0
        assert recall(["A"], set()) == 0.0


class TestRankedMetrics:
    def test_precision_at_k(self):
        retrieved = ["A", "B", "C", "D", "E"]
        relevant = {"B", "D"}
        assert precision_at_k(retrieved, relevant, 1) == 0.0
        assert precision_at_k(retrieved, relevant, 2) == 0.5
        assert precision_at_k(retrieved, relevant, 5) == 0.4

    def test_average_precision_hand_computed(self):
        # retrieved [A, B, C, D], relevant {B, D}
        # P@2=1/2, P@4=2/4 → AP = (1/2)(1/2 + 1/2) = 0.5
        assert abs(average_precision(["A", "B", "C", "D"], {"B", "D"}) - 0.5) < 1e-9

    def test_average_precision_perfect(self):
        assert abs(average_precision(["X", "Y"], {"X", "Y"}) - 1.0) < 1e-9

    def test_dcg_hand_computed(self):
        # rel grades: A=3, B=2 → DCG@2 = (2^3-1)/log2(2) + (2^2-1)/log2(3)
        expected = 7.0 / 1.0 + 3.0 / math_log2(3)
        assert abs(dcg_at_k(["A", "B"], {"A": 3, "B": 2}, 2) - expected) < 1e-9

    def test_ndcg_perfect_ordering(self):
        grades = {"A": 3, "B": 2, "C": 1}
        assert abs(ndcg_at_k(["A", "B", "C"], grades, 3) - 1.0) < 1e-9

    def test_ndcg_worse_ordering_below_one(self):
        grades = {"A": 3, "B": 2}
        assert ndcg_at_k(["B", "A"], grades, 2) < 1.0


def math_log2(x):
    import math
    return math.log2(x)
