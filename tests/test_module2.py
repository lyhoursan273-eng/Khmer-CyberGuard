import unittest
from contextlib import redirect_stdout
from io import StringIO

from backend.modules.website_pipeline import analyze_website


class TestKCGModule2(unittest.TestCase):

    def run_pipeline_quietly(self, filename):

        with redirect_stdout(StringIO()):
            return analyze_website(filename)

    def test_legitimate_website(self):

        report = self.run_pipeline_quietly(
            "legitimate_bank.html"
        )

        summary = report["summary"]

        self.assertEqual(
            summary["indicator_count"], 0
        )

        self.assertEqual(
            summary["evidence_count"], 1
        )

        self.assertEqual(
            summary["assessment"],
            "NO_INDICATORS_DETECTED_BY_CURRENT_RULES"
        )

    def test_suspicious_website(self):

        report = self.run_pipeline_quietly(
            "suspicious_bank.html"
        )

        summary = report["summary"]

        self.assertEqual(
            summary["indicator_count"], 5
        )

        self.assertEqual(
            summary["evidence_count"], 5
        )

        self.assertEqual(
            summary["assessment"],
            "REVIEW_REQUIRED"
        )

    def test_evidence_ids_are_unique(self):

        report = self.run_pipeline_quietly(
            "suspicious_bank.html"
        )

        evidence_ids = [
            item["evidence_id"]
            for item in report["evidence"]
        ]

        self.assertEqual(
            len(evidence_ids),
            len(set(evidence_ids))
        )

    def test_external_scanning_disabled(self):

        report = self.run_pipeline_quietly(
            "suspicious_bank.html"
        )

        methodology = report["methodology"]

        self.assertFalse(
            methodology["external_website_scanning_enabled"]
        )

        self.assertFalse(
            methodology["third_party_scanning_enabled"]
        )

    def test_unsupported_file_rejected(self):

        with self.assertRaises(ValueError):

            analyze_website("unknown_website.html")


if __name__ == "__main__":
    unittest.main()