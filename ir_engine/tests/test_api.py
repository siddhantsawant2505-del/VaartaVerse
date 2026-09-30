"""API endpoint tests: 422 on parse errors, BM25/PRF modes, tale-types registry."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app, get_index  # noqa: E402


@pytest.fixture(scope="module")
def client():
    get_index()  # force index build/load once
    with TestClient(app) as c:
        yield c


class TestSearchEndpoints:
    def test_vsm_search(self, client):
        res = client.post("/search/vsm", json={"query": "jackal lion", "top_k": 5})
        assert res.status_code == 200
        body = res.json()
        assert body["mode"] == "vsm"
        assert body["count"] <= 5

    def test_bm25_search(self, client):
        res = client.post("/search/bm25", json={"query": "jackal lion", "top_k": 5})
        assert res.status_code == 200
        assert res.json()["mode"] == "bm25"

    def test_boolean_ok(self, client):
        res = client.post("/search/boolean", json={"query": "jackal OR lion"})
        assert res.status_code == 200
        body = res.json()
        assert body["mode"] == "boolean"
        assert all("error" not in r for r in body["results"])

    def test_boolean_parse_error_is_422(self, client):
        res = client.post("/search/boolean", json={"query": "jackal AND (tiger"})
        assert res.status_code == 422
        assert "boolean_parse_error" in str(res.json())

    def test_boolean_stopword_term_is_422(self, client):
        res = client.post("/search/boolean", json={"query": "the AND jackal"})
        assert res.status_code == 422

    def test_feedback(self, client):
        res = client.post(
            "/search/feedback",
            json={"query": "jackal well", "relevant_ids": ["PAN-014"], "non_relevant_ids": []},
        )
        assert res.status_code == 200
        assert res.json()["mode"] == "vsm_rocchio"

    def test_prf(self, client):
        res = client.post("/search/prf", json={"query": "jackal well", "top_k": 5})
        assert res.status_code == 200
        body = res.json()
        assert body["mode"] == "vsm_prf"
        assert body["count"] <= 5

    def test_vsm_no_correction_by_default(self, client):
        res = client.post("/search/vsm", json={"query": "jackel well", "top_k": 5})
        assert res.status_code == 200
        body = res.json()
        assert body["query_changed"] is False
        assert body["corrections"] == {}

    def test_vsm_auto_correct(self, client):
        res = client.post(
            "/search/vsm",
            json={"query": "jackel in the forst", "top_k": 5, "auto_correct": True},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["query_changed"] is True
        assert body["corrections"].get("jackel") == "jackal"
        assert body["corrections"].get("forst") == "forest"
        assert "jackal" in body["corrected_query"]
        assert body["count"] > 0, "corrected query should retrieve"

    def test_vsm_auto_correct_clean_query_unchanged(self, client):
        res = client.post(
            "/search/vsm",
            json={"query": "jackal well", "top_k": 5, "auto_correct": True},
        )
        body = res.json()
        assert body["query_changed"] is False
        assert body["corrections"] == {}

    def test_bm25_auto_correct(self, client):
        res = client.post(
            "/search/bm25",
            json={"query": "jackel", "top_k": 5, "auto_correct": True},
        )
        body = res.json()
        assert body["corrections"] == {"jackel": "jackal"}
        assert body["count"] > 0

    def test_nl_query_auto_correct(self, client):
        res = client.post(
            "/search/nl-query",
            json={"query": "jackel trick in the forst", "top_k": 5, "auto_correct": True},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["query_changed"] is True
        assert body["corrections"].get("forst") == "forest"
        assert body["parsed"]["normalized_query"].count("forest") >= 1

    def test_nl_query_synonym_expansion_off(self, client):
        res = client.post("/search/nl-query", json={"query": "clever jackal", "top_k": 5})
        assert res.status_code == 200
        body = res.json()
        assert body["synonyms_applied"] == []
        assert body["parsed"]["expansions"] == {}

    def test_nl_query_synonym_expansion_on(self, client):
        res = client.post(
            "/search/nl-query",
            json={"query": "wise king of the forest", "top_k": 5, "expand_synonyms": True},
        )
        assert res.status_code == 200
        body = res.json()
        # 'king' → queen, 'forest' → wood/woodland are in this corpus's vocabulary
        assert isinstance(body["synonyms_applied"], list)
        assert body["parsed"]["expansions"], "expected expansions for king/forest"
        for syn in body["synonyms_applied"]:
            assert " " not in syn
        # expansions must be in-vocabulary only
        vocab = set()
        from app.main import get_index
        vocab = get_index().vocabulary()
        assert set(body["synonyms_applied"]) <= vocab


class TestRegistryAndEval:
    def test_health(self, client):
        res = client.get("/health")
        assert res.status_code == 200
        body = res.json()
        assert body["corpus_size"] > 0
        assert "index_stale" in body

    def test_tale_types_registry(self, client):
        res = client.get("/tale-types")
        assert res.status_code == 200
        types = res.json()["tale_types"]
        assert types and all("tale_type" in t and "variant_count" in t for t in types)

    def test_divergence_known_type(self, client):
        types = client.get("/tale-types").json()["tale_types"]
        biggest = max(types, key=lambda t: t["variant_count"])["tale_type"]
        res = client.get(f"/tale-type/{biggest}/divergence")
        assert res.status_code == 200
        assert res.json()["variant_count"] >= 2

    def test_evaluate_runs_all_modes(self, client):
        res = client.post("/evaluate", json={})
        assert res.status_code == 200
        summary = res.json()["summary"]
        for mode in ("boolean", "vsm", "bm25", "vsm_rocchio"):
            assert mode in summary
            assert summary[mode]["query_count"] > 0
