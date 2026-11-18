import unittest
from unittest.mock import patch

from backend.modules.domain_pipeline import analyze_domain


class TestDomainPipeline(unittest.TestCase):

    @patch("backend.modules.domain_pipeline.check_dns_records")
    @patch("backend.modules.domain_pipeline.generate_variations")
    def test_pipeline_processes_candidates(
        self, mock_generate, mock_dns
    ):

        mock_generate.return_value = [
            "samplebank0.example",
            "samplebank1.example"
        ]

        mock_dns.return_value = {
            "A": {"status": "nxdomain", "records": []},
            "AAAA": {"status": "nxdomain", "records": []},
            "MX": {"status": "nxdomain", "records": []},
            "NS": {"status": "nxdomain", "records": []}
        }

        report = analyze_domain("samplebank.example")

        # Check candidate summary
        self.assertEqual(
            report["summary"]["total_candidates"], 2
        )

        self.assertEqual(
            report["summary"]["dns_candidates_checked"], 2
        )

        # Check evidence summary
        self.assertEqual(
            report["summary"]["total_evidence_records"], 4
        )

        # Check evidence records
        self.assertEqual(len(report["evidence"]), 4)

        evidence_types = [
            item["evidence_type"]
            for item in report["evidence"]
        ]

        self.assertEqual(
            evidence_types.count("domain_similarity"), 2
        )

        self.assertEqual(
            evidence_types.count("dns_lookup"), 2
        )

        # Check unique evidence IDs
        evidence_ids = [
            item["evidence_id"]
            for item in report["evidence"]
        ]

        self.assertEqual(
            len(evidence_ids),
            len(set(evidence_ids))
        )

        self.assertEqual(mock_dns.call_count, 2)

    def test_reject_non_example_domain(self):

        with patch(
            "backend.modules.domain_pipeline.generate_variations"
        ) as mock_generate:

            with self.assertRaises(ValueError):
                analyze_domain("samplebank.com")

            mock_generate.assert_not_called()

    def test_reject_empty_domain(self):

        with self.assertRaises(ValueError):
            analyze_domain("")

    @patch("backend.modules.domain_pipeline.check_dns_records")
    @patch("backend.modules.domain_pipeline.generate_variations")
    def test_dns_error_is_recorded(
        self, mock_generate, mock_dns
    ):

        mock_generate.return_value = [
            "samplebank0.example"
        ]

        mock_dns.side_effect = RuntimeError(
            "DNS service unavailable"
        )

        report = analyze_domain("samplebank.example")

        result = report["results"][0]

        self.assertEqual(
            result["dns_lookup_status"], "error"
        )

        self.assertIn("dns_error", result)

        # Confirm the DNS error is also saved as evidence
        dns_evidence = [
            item for item in report["evidence"]
            if item["evidence_type"] == "dns_lookup"
        ]

        self.assertEqual(len(dns_evidence), 1)

        self.assertEqual(
            dns_evidence[0]["lookup_status"], "error"
        )


if __name__ == "__main__":
    unittest.main()