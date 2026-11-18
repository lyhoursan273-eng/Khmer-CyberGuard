import unittest
from unittest.mock import patch

import dns.resolver

from backend.modules.dns_enrichment import check_dns_records


class FakeRecord:
    def __init__(self, value):
        self.value = value

    def to_text(self):
        return self.value


class TestDNSEnrichment(unittest.TestCase):

    @patch("backend.modules.dns_enrichment.dns.resolver.Resolver")
    def test_all_dns_records_found(self, mock_resolver):

        resolver = mock_resolver.return_value

        resolver.resolve.side_effect = [
            [FakeRecord("192.0.2.10")],
            [FakeRecord("2001:db8::10")],
            [FakeRecord("10 mail.example.")],
            [FakeRecord("ns1.example.")]
        ]

        result = check_dns_records("samplebank.example")

        self.assertEqual(result["A"]["status"], "found")
        self.assertEqual(result["AAAA"]["status"], "found")
        self.assertEqual(result["MX"]["status"], "found")
        self.assertEqual(result["NS"]["status"], "found")

    @patch("backend.modules.dns_enrichment.dns.resolver.Resolver")
    def test_nxdomain(self, mock_resolver):

        resolver = mock_resolver.return_value
        resolver.resolve.side_effect = dns.resolver.NXDOMAIN

        result = check_dns_records("samplebank.example")

        for record_type in ["A", "AAAA", "MX", "NS"]:
            self.assertEqual(
                result[record_type]["status"],
                "nxdomain"
            )

    @patch("backend.modules.dns_enrichment.dns.resolver.Resolver")
    def test_null_mx(self, mock_resolver):

        resolver = mock_resolver.return_value

        resolver.resolve.side_effect = [
            [FakeRecord("192.0.2.10")],
            [FakeRecord("2001:db8::10")],
            [FakeRecord("0 .")],
            [FakeRecord("ns1.example.")]
        ]

        result = check_dns_records("samplebank.example")

        self.assertEqual(
            result["MX"]["status"],
            "null_mx"
        )

    def test_empty_domain_rejected(self):

        with self.assertRaises(ValueError):
            check_dns_records("")


if __name__ == "__main__":
    unittest.main()