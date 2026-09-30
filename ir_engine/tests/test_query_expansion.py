"""WordNet synonym expansion: module behavior, VSM integration, parser wiring."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.query_expansion import expand_terms, wordnet_available  # noqa: E402
from app.core.vsm_engine import VSMEngine  # noqa: E402
from app.core.inverted_index import InvertedIndex  # noqa: E402
from app.core.nl_parser import NLQueryParser  # noqa: E402

pytestmark = pytest.mark.skipif(
    not wordnet_available(), reason="WordNet corpora unavailable"
)


class TestExpandTerms:
    def test_adjective_resolved_via_adjective_pos(self):
        # "clever" has no noun synsets; must resolve via adjective synsets
        out = expand_terms(["clever"])
        assert out.get("clever"), "clever should expand via adjective synsets"

    def test_multiword_lemmas_excluded(self):
        out = expand_terms(["trick"])
        for syns in out.values():
            for s in syns:
                assert " " not in s

    def test_vocabulary_filter(self):
        out = expand_terms(["well"], vocabulary=set())  # empty vocab filters everything
        assert out == {}

    def test_oov_term_expands_to_nothing(self):
        assert expand_terms(["xyzzyplugh"]) == {}

    def test_original_term_never_in_synonyms(self):
        out = expand_terms(["jackal", "sleep"])
        for term, syns in out.items():
            assert term not in syns

    def test_query_terms_not_reintroduced(self):
        # if 'slumber' is a synonym of 'sleep' and also an explicit query term,
        # it must not be duplicated as an expansion
        out = expand_terms(["sleep", "slumber"])
        for term, syns in out.items():
            others = {t for t in ("sleep", "slumber") if t != term}
            assert not (set(syns) & others)


class TestVSMIntegration:
    def test_expansion_adds_matches(self):
        idx = InvertedIndex()
        # 'cunning' appears only in W; query uses its synonym 'clever'
        idx.add_document("W", "W", "wily", "a cunning old fox", "T", "", "", "", "", "")
        idx.add_document("V", "V", "plain", "nothing relevant at all", "T", "", "", "", "", "")
        vsm = VSMEngine(idx)

        base = {r["doc_id"] for r in vsm.search("clever")}
        expanded = vsm.search("clever", expansion_weights={"cunning": 0.3})
        got = {r["doc_id"] for r in expanded}

        assert "W" not in base
        assert "W" in got, "synonym expansion should retrieve the 'cunning' doc"

    def test_expansion_weighted_below_original(self):
        idx = InvertedIndex()
        idx.add_document("A", "A", "clever", "clever plans only", "T", "", "", "", "", "")
        idx.add_document("B", "B", "tricky", "a cunning trickster", "T", "", "", "", "", "")
        idx.add_document("C", "C", "neither", "totally different words", "T", "", "", "", "", "")
        vsm = VSMEngine(idx)

        r = vsm.search("clever", expansion_weights={"cunning": 0.3}, top_k=3)
        scores = {x["doc_id"]: x["score"] for x in r}
        assert scores["A"] > scores["B"], "original term doc must outrank synonym-only doc"

    def test_expansion_cannot_override_original_term(self):
        # 'cunning' as an explicit query term keeps its full tf-idf weight,
        # not the expansion weight
        idx = InvertedIndex()
        idx.add_document("A", "A", "cunning", "the cunning plan", "T", "", "", "", "", "")
        vsm = VSMEngine(idx)
        full = vsm.search("cunning")[0]["score"]
        forced = vsm.search(
            "cunning", expansion_weights={"cunning": 0.3}
        )[0]["score"]
        assert full == forced, "explicit term weight must win over expansion weight"

    def test_expansion_reported_per_doc(self):
        idx = InvertedIndex()
        idx.add_document("W", "W", "wily", "a cunning old fox", "T", "", "", "", "", "")
        idx.add_document("V", "V", "clever", "clever ideas", "T", "", "", "", "", "")
        vsm = VSMEngine(idx)
        r = {x["doc_id"]: x for x in vsm.search("clever", expansion_weights={"cunning": 0.3})}
        assert r["W"]["expansions_matched"] == ["cunning"]
        assert r["V"]["expansions_matched"] == []


class TestParserWiring:
    def test_expansion_off_by_default(self):
        parsed = NLQueryParser().parse("clever jackal")
        assert parsed["expansions"] == {}
        assert parsed["expanded_terms"] == []

    def test_expansion_toggle_populates_payload(self):
        parsed = NLQueryParser().parse("clever jackal", expand_synonyms=True)
        assert "clever" in parsed["expansions"]

    def test_expansion_not_applied_in_boolean_mode(self):
        parsed = NLQueryParser().parse("lion AND jackal", expand_synonyms=True)
        assert parsed["mode"] == "boolean"
        assert parsed["expansions"] == {}
