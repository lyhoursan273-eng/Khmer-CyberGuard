import json
import unittest

from pathlib import Path
from unittest.mock import patch
import subprocess

from backend.modules.httpx_collector import (
    validate_test_url,
    collect_httpx_info
)


class TestKCGHttpxCollector(unittest.TestCase):

    def test_legitimate_local_url_accepted(self):

        url = "http://127.0.0.1:8000/legitimate_bank.html"

        validate_test_url(url)

    def test_suspicious_local_url_accepted(self):

        url = "http://127.0.0.1:8000/suspicious_bank.html"

        validate_test_url(url)

    def test_external_url_rejected(self):

        with self.assertRaises(ValueError):

            validate_test_url("https://example.com")

    def test_unapproved_path_rejected(self):

        with self.assertRaises(ValueError):

            validate_test_url(
                "http://127.0.0.1:8000/unknown.html"
            )

    def test_httpx_json_response_parsed(self):

        fake_response = {
            "url": "http://127.0.0.1:8000/suspicious_bank.html",
            "status_code": 200,
            "title": "Sample Bank - Urgent Account Verification",
            "webserver": "SimpleHTTP/0.6 Python/3.12.11",
            "content_type": "text/html",
            "failed": False
        }

        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=json.dumps(fake_response) + "\n",
            stderr=""
        )

        with patch(
            "backend.modules.httpx_collector.find_httpx",
            return_value=Path("httpx.exe")
        ), patch(
            "backend.modules.httpx_collector.subprocess.run",
            return_value=completed
        ):

            result = collect_httpx_info(
                "http://127.0.0.1:8000/suspicious_bank.html"
            )

        details = result["technical_details"]

        self.assertEqual(details["status_code"], 200)

        self.assertEqual(
            details["title"],
            "Sample Bank - Urgent Account Verification"
        )

        self.assertEqual(
            details["content_type"],
            "text/html"
        )

        self.assertEqual(
            result["source_tool"],
            "ProjectDiscovery httpx"
        )

    def test_empty_httpx_response_rejected(self):

        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="",
            stderr=""
        )

        with patch(
            "backend.modules.httpx_collector.find_httpx",
            return_value=Path("httpx.exe")
        ), patch(
            "backend.modules.httpx_collector.subprocess.run",
            return_value=completed
        ):

            with self.assertRaises(RuntimeError):

                collect_httpx_info(
                    "http://127.0.0.1:8000/legitimate_bank.html"
                )


if __name__ == "__main__":
    unittest.main()