import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.modules.url_validator import validate_url
from backend.modules.url_normalizer import normalize_url
from backend.modules.threat_intel_checker import check_threat_intelligence
from backend.modules.url_evidence import collect_url_evidence
from backend.modules import url_pipeline


class TestURLValidator(unittest.TestCase):

    def test_valid_example_url(self):
        result = validate_url(
            "https://samplebank-login.example/verify-account"
        )
        self.assertTrue(result["is_valid"])

    def test_reject_unsupported_protocol(self):
        result = validate_url(
            "ftp://samplebank-login.example/file"
        )
        self.assertFalse(result["is_valid"])

    def test_reject_non_example_domain(self):
        result = validate_url(
            "https://google.com"
        )
        self.assertFalse(result["is_valid"])

    def test_reject_embedded_credentials(self):
        result = validate_url(
            "https://user:password@samplebank-login.example/"
        )
        self.assertFalse(result["is_valid"])

    def test_reject_empty_url(self):
        result = validate_url("")
        self.assertFalse(result["is_valid"])


class TestURLNormalizer(unittest.TestCase):

    def test_normalize_https_url(self):
        result = normalize_url(
            "HTTPS://SAMPLEBANK-LOGIN.EXAMPLE:443/verify-account#login"
        )

        self.assertTrue(result["is_valid"])
        self.assertEqual(
            result["normalized_url"],
            "https://samplebank-login.example/verify-account"
        )

    def test_preserve_query_parameters(self):
        result = normalize_url(
            "https://samplebank-login.example/account?source=test#section"
        )

        self.assertEqual(
            result["normalized_url"],
            "https://samplebank-login.example/account?source=test"
        )


class TestThreatIntelligenceChecker(unittest.TestCase):

    def test_detect_matching_record(self):
        result = check_threat_intelligence(
            "https://samplebank-login.example/verify-account"
        )

        self.assertEqual(result["status"], "MATCH_FOUND")
        self.assertEqual(
            result["match"]["record_id"],
            "KCG-TI-TEST-001"
        )

    def test_detect_second_matching_record(self):
        result = check_threat_intelligence(
            "https://samplebank-login.example/account-update"
        )

        self.assertEqual(result["status"], "MATCH_FOUND")
        self.assertEqual(
            result["match"]["record_id"],
            "KCG-TI-TEST-002"
        )

    def test_no_matching_record(self):
        result = check_threat_intelligence(
            "https://samplebank-login.example/contact"
        )

        self.assertEqual(result["status"], "NO_MATCH")

    def test_invalid_url_check(self):
        result = check_threat_intelligence("invalid-url")

        self.assertEqual(result["status"], "CHECK_FAILED")


class TestURLEvidence(unittest.TestCase):

    def setUp(self):
        self.match_result = check_threat_intelligence(
            "https://samplebank-login.example/verify-account"
        )

    def test_create_match_evidence(self):
        evidence = collect_url_evidence(self.match_result)

        self.assertEqual(len(evidence), 1)
        self.assertEqual(
            evidence[0]["evidence_type"],
            "url_threat_intelligence_match"
        )

    def test_evidence_is_marked_test_only(self):
        evidence = collect_url_evidence(self.match_result)

        self.assertTrue(evidence[0]["test_only"])

    def test_create_no_match_evidence(self):
        result = check_threat_intelligence(
            "https://samplebank-login.example/contact"
        )

        evidence = collect_url_evidence(result)

        self.assertEqual(len(evidence), 1)
        self.assertEqual(
            evidence[0]["evidence_type"],
            "url_threat_intelligence_no_match"
        )

    def test_failed_check_creates_no_evidence(self):
        result = check_threat_intelligence("invalid-url")

        evidence = collect_url_evidence(result)

        self.assertEqual(evidence, [])

    def test_evidence_ids_are_unique(self):
        first = collect_url_evidence(self.match_result)
        second = collect_url_evidence(self.match_result)

        self.assertNotEqual(
            first[0]["evidence_id"],
            second[0]["evidence_id"]
        )


class TestURLPipeline(unittest.TestCase):

    def test_pipeline_match_found(self):
        report = url_pipeline.analyze_url(
            "https://samplebank-login.example/verify-account"
        )

        self.assertEqual(
            report["summary"]["analysis_status"],
            "MATCH_FOUND"
        )

        self.assertEqual(
            report["summary"]["evidence_count"],
            1
        )

    def test_pipeline_no_match(self):
        report = url_pipeline.analyze_url(
            "https://samplebank-login.example/contact"
        )

        self.assertEqual(
            report["summary"]["analysis_status"],
            "NO_MATCH"
        )

    def test_save_json_report(self):
        report = url_pipeline.analyze_url(
            "https://samplebank-login.example/verify-account"
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            with patch.object(
                url_pipeline,
                "REPORTS_DIR",
                Path(temp_dir)
            ):
                report_path = url_pipeline.save_report(report)

            self.assertTrue(Path(report_path).exists())

            with open(report_path, "r", encoding="utf-8") as file:
                saved_report = json.load(file)

            self.assertEqual(
                saved_report["module"],
                "Module 3 - Malicious URL Checking"
            )


if __name__ == "__main__":
    unittest.main()