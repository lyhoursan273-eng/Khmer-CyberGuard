import unittest

from backend.modules.evidence_collector import collect_evidence


class TestEvidenceCollector(unittest.TestCase):

    def setUp(self):

        self.official_domain = "samplebank.example"
        self.generated_at = "2026-11-18T00:00:00+00:00"

    def test_domain_similarity_evidence(self):

        results = [
            {
                "domain": "samplebank0.example",
                "edit_distance": 1,
                "similarity_percentage": 94.74,
                "dns_lookup_status": "not_checked",
                "dns_records": {}
            }
        ]

        evidence = collect_evidence(
            self.official_domain,
            results,
            self.generated_at
        )

        self.assertEqual(len(evidence), 1)

        self.assertEqual(
            evidence[0]["evidence_id"],
            "KCG-EV-00001"
        )

        self.assertEqual(
            evidence[0]["evidence_type"],
            "domain_similarity"
        )

    def test_dns_evidence_is_collected(self):

        results = [
            {
                "domain": "samplebank0.example",
                "edit_distance": 1,
                "similarity_percentage": 94.74,
                "dns_lookup_status": "completed",
                "dns_records": {
                    "A": {
                        "status": "nxdomain",
                        "records": []
                    }
                }
            }
        ]

        evidence = collect_evidence(
            self.official_domain,
            results,
            self.generated_at
        )

        self.assertEqual(len(evidence), 2)

        self.assertEqual(
            evidence[1]["evidence_type"],
            "dns_lookup"
        )

        self.assertEqual(
            evidence[1]["source_tool"],
            "dnspython"
        )

    def test_dns_evidence_skipped_when_not_checked(self):

        results = [
            {
                "domain": "samplebank1.example",
                "edit_distance": 1,
                "similarity_percentage": 94.74,
                "dns_lookup_status": "not_checked",
                "dns_records": {}
            }
        ]

        evidence = collect_evidence(
            self.official_domain,
            results,
            self.generated_at
        )

        self.assertEqual(len(evidence), 1)

    def test_evidence_ids_are_unique(self):

        results = [
            {
                "domain": "samplebank0.example",
                "edit_distance": 1,
                "similarity_percentage": 94.74,
                "dns_lookup_status": "completed",
                "dns_records": {}
            },
            {
                "domain": "samplebank1.example",
                "edit_distance": 1,
                "similarity_percentage": 94.74,
                "dns_lookup_status": "completed",
                "dns_records": {}
            }
        ]

        evidence = collect_evidence(
            self.official_domain,
            results,
            self.generated_at
        )

        evidence_ids = [
            item["evidence_id"]
            for item in evidence
        ]

        self.assertEqual(len(evidence_ids), 4)
        self.assertEqual(len(set(evidence_ids)), 4)


if __name__ == "__main__":
    unittest.main()