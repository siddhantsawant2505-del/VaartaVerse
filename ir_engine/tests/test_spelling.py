"""Spelling correction: Levenshtein bound, policy, and edge cases."""

from app.core.spelling import correct_term, correct_terms, levenshtein_within


VOCAB = {
    "jackal", "lion", "tiger", "well", "deep", "king", "queen", "forest",
    "cunning", "clever", "trick", "treat", "bread", "beast", "serpent",
}


class TestLevenshteinBound:
    def test_equal(self):
        assert levenshtein_within("abc", "abc", 2) == 0

    def test_one_edit(self):
        assert levenshtein_within("jackel", "jackal", 2) == 1

    def test_two_edits(self):
        # adjacent transposition (en ↔ ne) costs 2 in plain Levenshtein
        assert levenshtein_within("quene", "queen", 2) == 2
        assert levenshtein_within("quene", "queen", 1) == 2

    def test_insertion_is_one_edit(self):
        assert levenshtein_within("kng", "king", 2) == 1

    def test_over_bound_short_circuits(self):
        assert levenshtein_within("abcdefgh", "xyz", 2) == 3

    def test_transposition_counts_as_two(self):
        # plain Levenshtein (no transposition op): ab <-> ba costs 2
        assert levenshtein_within("ab", "ba", 2) == 2


class TestCorrectTerm:
    def test_in_vocab_never_corrected(self):
        assert correct_term("jackal", VOCAB) is None

    def test_distance1_corrects_even_with_tie(self):
        # 'welp' → 'well' (1 sub); ties are allowed at distance 1
        assert correct_term("welp", VOCAB) == "well"

    def test_distance2_unique_corrects(self):
        # 'quene' → 'queen' is a 2-edit transposition with a unique neighbor
        assert correct_term("quene", VOCAB) == "queen"

    def test_distance2_tie_refuses(self):
        # 'brest' → 'bread' (2) and 'beast' (2): ambiguous → None
        assert correct_term("brest", VOCAB) is None

    def test_short_terms_never_corrected(self):
        assert correct_term("jo", VOCAB) is None

    def test_numbers_never_corrected(self):
        assert correct_term("42", VOCAB) is None

    def test_oov_far_word_returns_none(self):
        assert correct_term("zzzzzzzz", VOCAB) is None

    def test_max_distance_1_stricter(self):
        # 'quene' is distance 2 from 'queen' → not corrected when max_distance=1
        assert correct_term("quene", VOCAB, max_distance=1) is None
        assert correct_term("jackel", VOCAB, max_distance=1) == "jackal"


class TestCorrectTerms:
    def test_only_changed_terms_returned(self):
        out = correct_terms(["jackel", "jackal", "forst"], VOCAB)
        assert out == {"jackel": "jackal", "forst": "forest"}

    def test_dedupes(self):
        out = correct_terms(["jackel", "jackel"], VOCAB)
        assert out == {"jackel": "jackal"}

    def test_empty(self):
        assert correct_terms([], VOCAB) == {}
