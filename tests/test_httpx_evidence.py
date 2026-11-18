import unittest

from backend.modules.evidence_collector import (
    collect_httpx_evidence
)


class TestHttpxEvidence(unittest.TestCase):

    def setUp(self):

        self.httpx_result = {
            "source_tool": "ProjectDiscovery httpx",
            "observed_at_utc": "2026-11-18T10:00:00Z",
            "requested_url": (
                "http://127.0.0.1:8000/suspicious_bank.html"
            ),
            "technical_details": {
                "status_code": 200,
                "title": "Sample Bank - Urgent Account Verification",
                "content_type": "text/html"
            }
        }

        self.generated_at = "2026-11-18T10:00:00Z"

    def test_httpx_evidence_created(self):

        evidence = collect_httpx_evidence(
            self.httpx_result,
            self.generated_at
        )

        self.assertEqual(len(evidence), 1)

        self.assertEqual(
            evidence[0]["evidence_type"],
            "website_technical_observation"
        )

    def test_httpx_source_tool(self):

        evidence = collect_httpx_evidence(
            self.httpx_result,
            self.generated_at
        )

        self.assertEqual(
            evidence[0]["source_tool"],
            "ProjectDiscovery httpx"
        )

    def test_httpx_severity_is_informational(self):

        evidence = collect_httpx_evidence(
            self.httpx_result,
            self.generated_at
        )

        self.assertEqual(
            evidence[0]["severity"],
            "informational"
        )

    def test_empty_technical_details(self):

        result = {
            "technical_details": {}
        }

        evidence = collect_httpx_evidence(
            result,
            self.generated_at
        )

        self.assertEqual(evidence, [])

    def test_evidence_ids_are_unique(self):

        first = collect_httpx_evidence(
            self.httpx_result,
            self.generated_at
        )

        second = collect_httpx_evidence(
            self.httpx_result,
            self.generated_at
        )

        self.assertNotEqual(
            first[0]["evidence_id"],
            second[0]["evidence_id"]
        )


if __name__ == "__main__":
    unittest.main()