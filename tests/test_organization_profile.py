import json
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from backend.main import load_organization_profile


class TestOrganizationProfile(unittest.TestCase):

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()

        self.profile_path = (
            Path(self.temp_directory.name)
            / "test_organization.json"
        )

        self.valid_profile = {
            "organization_id": "KCG-TEST-001",
            "organization_name": "Sample Bank",
            "organization_type": "Fictional Test Organization",
            "official_domain": "samplebank.example",

            "verification": {
                "status": "TEST_ONLY",
                "domain_verified": False
            },

            "testing_configuration": {
                "testing_mode": "LOCAL_SCENARIOS",
                "external_website_scanning_enabled": False
            }
        }

    def tearDown(self):
        self.temp_directory.cleanup()

    def save_profile(self, profile):
        self.profile_path.write_text(
            json.dumps(profile),
            encoding="utf-8"
        )

    def load_profile(self, profile):
        self.save_profile(profile)

        with patch(
            "backend.main.PROFILE_PATH",
            self.profile_path
        ):
            return load_organization_profile()

    def test_valid_profile_loads(self):

        result = self.load_profile(self.valid_profile)

        self.assertEqual(
            result["organization_name"],
            "Sample Bank"
        )

        self.assertEqual(
            result["official_domain"],
            "samplebank.example"
        )

    def test_profile_validation(self):

        result = self.load_profile(self.valid_profile)

        self.assertEqual(
            result["organization_id"],
            "KCG-TEST-001"
        )

        self.assertEqual(
            result["verification"]["status"],
            "TEST_ONLY"
        )

        self.assertFalse(
            result["verification"]["domain_verified"]
        )

        self.assertEqual(
            result["testing_configuration"]["testing_mode"],
            "LOCAL_SCENARIOS"
        )

    def test_wrong_verification_status(self):

        profile = self.valid_profile.copy()

        profile["verification"] = {
            "status": "UNVERIFIED"
        }

        with self.assertRaises(ValueError):
            self.load_profile(profile)

    def test_wrong_testing_mode(self):

        profile = self.valid_profile.copy()

        profile["testing_configuration"] = {
            "testing_mode": "PRODUCTION",
            "external_website_scanning_enabled": False
        }

        with self.assertRaises(ValueError):
            self.load_profile(profile)

    def test_external_scanning_rejected(self):

        profile = self.valid_profile.copy()

        profile["testing_configuration"][
            "external_website_scanning_enabled"
        ] = True

        with self.assertRaises(ValueError):
            self.load_profile(profile)


if __name__ == "__main__":
    unittest.main()