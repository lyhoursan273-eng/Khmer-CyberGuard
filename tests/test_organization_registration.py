import json
import tempfile
import unittest

from pathlib import Path

from backend.modules.onboarding.organization_registration import (
    register_organization
)


class TestOrganizationRegistration(unittest.TestCase):

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.storage_dir = Path(self.temp_directory.name)

        self.organization_data = {
            "organization_name": "Example Finance",
            "organization_type": "Microfinance Institution",
            "contact_email": "security@example.com",
            "official_domain": "example.com",
            "brand_name": "Example Finance",
            "khmer_brand_name": "អង្គភាពគំរូ"
        }

    def tearDown(self):
        self.temp_directory.cleanup()

    def register_sample(self, **overrides):
        data = self.organization_data.copy()
        data.update(overrides)

        return register_organization(
            **data,
            storage_dir=self.storage_dir
        )

    def test_successful_registration(self):
        profile = self.register_sample()

        self.assertEqual(
            profile["organization_name"],
            "Example Finance"
        )

        self.assertEqual(
            profile["official_domain"],
            "example.com"
        )

    def test_initial_status_is_pending(self):
        profile = self.register_sample()

        self.assertEqual(
            profile["verification"]["status"],
            "PENDING_VERIFICATION"
        )

        self.assertFalse(
            profile["verification"]["domain_verified"]
        )

    def test_organization_profile_is_saved(self):
        profile = self.register_sample()

        profile_path = (
            self.storage_dir
            / f"{profile['organization_id']}.json"
        )

        self.assertTrue(profile_path.exists())

        saved_profile = json.loads(
            profile_path.read_text(encoding="utf-8")
        )

        self.assertEqual(
            saved_profile["organization_id"],
            profile["organization_id"]
        )

    def test_real_domain_format_is_accepted(self):
        profile = self.register_sample(
            official_domain="EXAMPLE.COM"
        )

        self.assertEqual(
            profile["official_domain"],
            "example.com"
        )

    def test_invalid_domain_is_rejected(self):
        with self.assertRaises(ValueError):
            self.register_sample(
                official_domain="https://example.com"
            )

    def test_invalid_email_is_rejected(self):
        with self.assertRaises(ValueError):
            self.register_sample(
                contact_email="invalid-email"
            )

    def test_empty_organization_name_is_rejected(self):
        with self.assertRaises(ValueError):
            self.register_sample(
                organization_name=" "
            )

    def test_duplicate_domain_is_rejected(self):
        self.register_sample()

        with self.assertRaises(ValueError):
            self.register_sample(
                organization_name="Another Finance"
            )

    def test_organization_ids_are_unique(self):
        first = self.register_sample()

        second = self.register_sample(
            organization_name="Another Finance",
            official_domain="another-example.com"
        )

        self.assertNotEqual(
            first["organization_id"],
            second["organization_id"]
        )


if __name__ == "__main__":
    unittest.main()