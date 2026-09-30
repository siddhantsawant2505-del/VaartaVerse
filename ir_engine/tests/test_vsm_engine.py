"""VSM: idf smoothing, real zone weighting, cosine behavior, no fallbacks."""

import math

from app.core.inverted_index import InvertedIndex
from app.core.vsm_engine import VSMEngine


def make_vsm():
    idx = InvertedIndex()
    idx.add_document("X", "X", "jackal", "totally unrelated words here", "T", "", "", "", "", "")
    idx.add_document("Y", "Y", "unrelated", "the jackal appears in body text", "T", "", "", "", "", "")
    idx.add_document("Z", "Z", "nothing", "other filler content entirely", "T", "", "", "", "", "")
    return idx, VSMEngine(idx)


class TestZoneWeighting:
    def test_title_match_outranks_body_match(self):
        _, vsm = make_vsm()
        r = {x["doc_id"]: x["score"] for x in vsm.search("jackal")}
        assert r["X"] > r["Y"], f"title={r.get('X')} body={r.get('Y')}"

    def test_default_weights_are_multipliers(self):
        _, vsm = make_vsm()
        r = vsm.search("jackal", top_k=1)
        assert r[0]["zone_weights"] == {"title": 2.0, "body": 1.0}

    def test_zero_title_weight_flips_ranking(self):
        _, vsm = make_vsm()
        r = {x["doc_id"]: x["score"] for x in vsm.search("jackal", zone_weights={"title": 0.0, "body": 1.0})}
        assert r["Y"] > r["X"]


class TestIdf:
    def test_single_doc_corpus_still_returns_results(self):
        idx = InvertedIndex()
        idx.add_document("S", "S", "solitary", "one lone document", "T", "", "", "", "", "")
        vsm = VSMEngine(idx)
        r = vsm.search("solitary")
        assert len(r) == 1 and r[0]["score"] > 0

    def test_idf_always_positive(self):
        # df = N must not zero out the term (old formula collapsed to 0)
        idx = InvertedIndex()
        for d in ("P", "Q"):
            idx.add_document(d, d, f"{d} title", f"shared token {d}extra", "T", "", "", "", "", "")
        vsm = VSMEngine(idx)
        # 'token' is in every doc (df == N) but 'pextra'/'qextra' differ; query both
        r = vsm.search("token", top_k=5)
        assert len(r) == 2, "df==N term must still retrieve"
        assert all(x["score"] > 0 for x in r)


class TestEmptyBehavior:
    def test_stopword_only_query_returns_empty(self):
        _, vsm = make_vsm()
        assert vsm.search("the of and") == []

    def test_unknown_term_returns_empty(self):
        _, vsm = make_vsm()
        assert vsm.search("xyzzyplugh") == []

    def test_empty_index_returns_empty(self):
        vsm = VSMEngine(InvertedIndex())
        assert vsm.search("jackal") == []

    def test_no_silent_substring_fallback(self):
        # 'cat' must NOT fuzzy-match 'catalog'-like terms
        idx = InvertedIndex()
        idx.add_document("C1", "C1", "catalog", "a catalog of items", "T", "", "", "", "", "")
        vsm = VSMEngine(idx)
        assert vsm.search("cat") == []


class TestScores:
    def test_scores_descending_and_bounded(self):
        _, vsm = make_vsm()
        scores = [x["score"] for x in vsm.search("jackal unrelated", top_k=5)]
        assert scores == sorted(scores, reverse=True)
        assert all(0 <= s <= 1.0 + 1e-9 for s in scores)  # cosine ≤ 1

    def test_terms_matched_populated(self):
        _, vsm = make_vsm()
        r = vsm.search("jackal", top_k=1)
        assert r[0]["terms_matched"] == ["jackal"]
