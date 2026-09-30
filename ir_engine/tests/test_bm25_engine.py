"""BM25: ranking sanity, length normalization, parametric behavior."""

from app.core.bm25_engine import BM25Engine


class TestBM25:
    def test_finds_relevant_docs(self, tiny_index):
        r = BM25Engine(tiny_index).search("jackal", top_k=5)
        assert {x["doc_id"] for x in r} == {"B", "D"}

    def test_title_boost_ranks_title_match_first(self, tiny_index):
        # 'jackal': B has it in title+body, D only in body → B first
        bm = BM25Engine(tiny_index)
        r = bm.search("jackal", top_k=2, title_boost=3.0)
        assert r[0]["doc_id"] == "B"

    def test_scores_positive_descending(self, tiny_index):
        r = BM25Engine(tiny_index).search("tiger jackal", top_k=5)
        scores = [x["score"] for x in r]
        assert scores == sorted(scores, reverse=True)
        assert all(s > 0 for s in scores)

    def test_stopword_only_query_empty(self, tiny_index):
        assert BM25Engine(tiny_index).search("the of") == []

    def test_empty_index(self):
        from app.core.inverted_index import InvertedIndex
        assert BM25Engine(InvertedIndex()).search("jackal") == []

    def test_param_overrides_respected(self, tiny_index):
        bm = BM25Engine(tiny_index, k1=1.2, b=0.75)
        r = bm.search("tiger", top_k=1)
        assert r[0]["bm25_params"]["k1"] == 1.2

    def test_terms_matched(self, tiny_index):
        r = BM25Engine(tiny_index).search("jackal tiger", top_k=5)
        b = next(x for x in r if x["doc_id"] == "B")
        assert set(b["terms_matched"]) == {"jackal", "tiger"}
