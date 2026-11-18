import unittest

from backend.modules.domain_comparison import (
    normalize_domain,
    compare_domains
)

from backend.modules.levenshtein import (
    levenshtein_distance,
    similarity_percentage
)

from backend.modules.domain_pipeline import analyze_domain


class TestKCGModule1(unittest.TestCase):

    # Domain normalization tests

    def test_normalize_domain(self):
        result = normalize_domain(" MekongFinance.EXAMPLE ")
        self.assertEqual(result, "mekongfinance.example")

    # Domain comparison tests

    def test_exact_domain_match(self):
        self.assertTrue(
            compare_domains(
                "mekongfinance.example",
                "mekongfinance.example"
            )
        )

    def test_different_domains(self):
        self.assertFalse(
            compare_domains(
                "mekongfinance.example",
                "mekong-finance.example"
            )
        )

    # Levenshtein tests

    def test_identical_strings(self):
        self.assertEqual(
            levenshtein_distance("cat", "cat"),
            0
        )

    def test_character_substitution(self):
        self.assertEqual(
            levenshtein_distance("cat", "cut"),
            1
        )

    def test_character_insertion(self):
        self.assertEqual(
            levenshtein_distance("cat", "cats"),
            1
        )

    # Similarity tests

    def test_identical_domain_similarity(self):
        self.assertEqual(
            similarity_percentage(
                "samplebank.example",
                "samplebank.example"
            ),
            100.0
        )

    def test_similar_domain_percentage(self):
        self.assertEqual(
            similarity_percentage(
                "mekongfinance.example",
                "mekong-finance.example"
            ),
            95.45
        )

    # Pipeline validation tests

    def test_reject_real_domain_in_test_mode(self):
        with self.assertRaises(ValueError):
            analyze_domain("samplebank.com")

    def test_reject_empty_domain(self):
        with self.assertRaises(ValueError):
            analyze_domain("")


if __name__ == "__main__":
    unittest.main()