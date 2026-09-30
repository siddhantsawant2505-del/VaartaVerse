"""Boolean engine: precedence, juxtaposition, NOT, ranking, parse errors."""

import pytest

from app.core.boolean_engine import BooleanEngine, BooleanParseError


def doc_ids(engine, query):
    return {r["doc_id"] for r in engine.search(query)}


@pytest.fixture()
def engine(tiny_index):
    return BooleanEngine(tiny_index)


class TestPrecedence:
    def test_and_binds_tighter_than_or(self, engine):
        # jackal AND tiger OR lion → (jackal AND tiger) OR lion = {B} ∪ {C} = {B, C}
        assert doc_ids(engine, "jackal AND tiger OR lion") == {"B", "C"}

    def test_not_and_or_full_mix(self, engine):
        # tiger OR lion AND NOT jackal → tiger OR (lion AND NOT-jackal) = {A,B} ∪ {C} = {A,B,C}
        assert doc_ids(engine, "tiger OR lion AND NOT jackal") == {"A", "B", "C"}

    def test_parentheses_override_precedence(self, engine):
        # (tiger OR lion) AND NOT jackal → {A,B,C} minus {B,D} = {A, C}
        assert doc_ids(engine, "(tiger OR lion) AND NOT jackal") == {"A", "C"}


class TestJuxtaposition:
    def test_implicit_and(self, engine):
        # no doc contains both jackal and lion
        assert doc_ids(engine, "jackal lion") == set()
        assert doc_ids(engine, "jackal AND lion") == set()

    def test_juxtaposed_not(self, engine):
        # "jackal NOT tiger" == "jackal AND NOT tiger" → {D}
        assert doc_ids(engine, "jackal NOT tiger") == {"D"}

    def test_trailing_not_after_and(self, engine):
        assert doc_ids(engine, "jackal AND NOT tiger") == {"D"}

    def test_unary_not(self, engine):
        assert doc_ids(engine, "NOT tiger") == {"C", "D"}

    def test_double_not(self, engine):
        assert doc_ids(engine, "NOT NOT tiger") == {"A", "B"}

    def test_juxtaposed_parens(self, engine):
        # (jackal)(lion) → jackal AND lion = ∅
        assert doc_ids(engine, "(jackal)(lion)") == set()
        # (jackal)(tiger) → {B}
        assert doc_ids(engine, "(jackal)(tiger)") == {"B"}


class TestParseErrors:
    def test_unclosed_paren_raises(self, engine):
        with pytest.raises(BooleanParseError):
            engine.search("jackal AND (tiger")

    def test_trailing_operator_raises(self, engine):
        with pytest.raises(BooleanParseError):
            engine.search("jackal AND")

    def test_leading_or_raises(self, engine):
        with pytest.raises(BooleanParseError):
            engine.search("OR jackal")

    def test_stopword_only_term_raises(self, engine):
        with pytest.raises(BooleanParseError):
            engine.search("the AND tiger")

    def test_error_message_has_content(self, engine):
        with pytest.raises(BooleanParseError) as ei:
            engine.search("jackal AND")
        assert "end of boolean expression" in str(ei.value)


class TestRanking:
    def test_results_carry_scores(self, engine):
        results = engine.search("tiger OR jackal")
        assert all("score" in r for r in results)
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_tf_idf_prefers_higher_tf(self):
        from app.core.inverted_index import InvertedIndex
        idx = InvertedIndex()
        idx.add_document("T1", "T1", "once", "tiger once", "T", "", "", "", "", "")
        idx.add_document("T3", "T3", "thrice", "tiger tiger tiger", "T", "", "", "", "", "")
        r = {x["doc_id"]: x["score"] for x in BooleanEngine(idx).search("tiger")}
        assert r["T3"] > r["T1"]


class TestFilters:
    def test_metadata_filters(self, engine):
        results = engine.search("tiger OR lion", filters={"region": "Nowhere"})
        assert results == []
