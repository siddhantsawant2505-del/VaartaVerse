"""Inverted index: persistence roundtrip, fingerprint staleness, registry helper."""

import json

from app.core.inverted_index import InvertedIndex, corpus_fingerprint


class TestIndexBasics:
    def test_df_and_postings(self, tiny_index):
        assert tiny_index.get_df("jackal") == 2
        assert set(tiny_index.get_postings("jackal").keys()) == {"B", "D"}

    def test_zone_positions_recorded(self, tiny_index):
        entry = tiny_index.get_postings("tiger")["A"]
        assert len(entry.zones["title"]) == 1
        assert len(entry.zones["body"]) == 1

    def test_variants_by_tale_type(self, tiny_index):
        assert len(tiny_index.get_variants_by_tale_type("t")) == 4

    def test_all_tale_types_registry(self, tiny_index):
        reg = tiny_index.all_tale_types()
        assert reg == [{"tale_type": "T", "variant_count": 4}]


class TestFingerprint:
    def test_fingerprint_changes_with_content(self, tmp_path):
        f = tmp_path / "corpus.json"
        f.write_text(json.dumps([{"tale_id": "A", "raw_text": "x"}]), encoding="utf-8")
        fp1 = corpus_fingerprint(f)
        f.write_text(json.dumps([{"tale_id": "A", "raw_text": "y"}]), encoding="utf-8")
        fp2 = corpus_fingerprint(f)
        assert fp1 != fp2

    def test_fingerprint_stable_for_same_content(self, tmp_path):
        f = tmp_path / "corpus.json"
        f.write_text(json.dumps([{"tale_id": "A", "raw_text": "x"}]), encoding="utf-8")
        assert corpus_fingerprint(f) == corpus_fingerprint(f)

    def test_missing_corpus_returns_none(self, tmp_path):
        assert corpus_fingerprint(tmp_path / "nope.json") is None
