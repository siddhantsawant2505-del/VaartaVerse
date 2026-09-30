"""Tokenizer / preprocessing regression tests."""

from app.core.preprocessing import preprocess, tokenize


class TestPossessives:
    def test_singular_possessive_stripped(self):
        assert preprocess("lion's den") == ["lion", "den"]

    def test_plural_apostrophe_stripped(self):
        assert tokenize("dogs' bones") == ["dogs", "bones"]

    def test_possessive_matches_bare_query(self):
        assert preprocess("lion's den") == preprocess("lion den")

    def test_unicode_apostrophe(self):
        assert preprocess("the lion\u2019s den") == ["lion", "den"]

    def test_contractions_degrade_gracefully(self):
        # "don't" → "dont" (apostrophe dropped, clitic kept) — consistent between
        # documents and queries, which is what matters for matching.
        assert preprocess("don't panic") == ["dont", "panic"]


class TestStopwords:
    def test_content_words_are_not_stopwords(self):
        # Regression: 'king', 'well', 'day' were once domain stopwords
        for word in ("king", "well", "day", "lion", "jackal"):
            assert preprocess(f"the {word}") == [word]

    def test_english_stopwords_removed(self):
        assert preprocess("the a an of in") == []

    def test_stopword_only_query_is_empty(self):
        assert preprocess("the of and") == []


class TestLemmatization:
    def test_plural_to_singular(self):
        assert preprocess("jackals") == ["jackal"]

    def test_verb_forms(self):
        assert preprocess("tricked") == ["trick"]

    def test_irregular(self):
        assert "foot" in preprocess("feet")
