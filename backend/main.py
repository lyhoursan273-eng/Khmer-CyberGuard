import json
from pathlib import Path

from backend.modules.domain_pipeline import (
    analyze_domain,
    display_results,
    save_report
)


# =====================================
# PROJECT SETTINGS
# =====================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROFILE_PATH = (
    PROJECT_ROOT
    / "data"
    / "organizations"
    / "test_organization.json"
)

ABA_PROFILE_PATH = (
    PROJECT_ROOT
    / "data"
    / "organizations"
    / "aba_public_reference.json"
)


# =====================================
# LOAD SAMPLE BANK PROFILE
# =====================================

def load_organization_profile():

    if not PROFILE_PATH.exists():
        raise FileNotFoundError(
            "Sample Bank profile was not found."
        )

    with PROFILE_PATH.open(
        "r",
        encoding="utf-8"
    ) as file:

        profile = json.load(file)

    if profile.get("verification", {}).get(
        "status"
    ) != "TEST_ONLY":

        raise ValueError(
            "Invalid Sample Bank testing profile."
        )

    if profile.get("testing_configuration", {}).get(
        "testing_mode"
    ) != "LOCAL_SCENARIOS":

        raise ValueError(
            "Incorrect Sample Bank testing mode."
        )

    if profile["testing_configuration"].get(
        "external_website_scanning_enabled"
    ):

        raise ValueError(
            "External scanning must remain disabled."
        )

    return profile


# =====================================
# LOAD ABA PUBLIC REFERENCE
# =====================================

def load_aba_reference_profile():

    if not ABA_PROFILE_PATH.exists():
        raise FileNotFoundError(
            "ABA public reference profile was not found."
        )

    with ABA_PROFILE_PATH.open(
        "r",
        encoding="utf-8"
    ) as file:

        profile = json.load(file)

    reference = profile.get(
        "reference_information", {}
    )

    verification = profile.get(
        "verification", {}
    )

    configuration = profile.get(
        "testing_configuration", {}
    )

    if reference.get(
        "reference_status"
    ) != "PUBLIC_REFERENCE_ONLY":

        raise ValueError(
            "Invalid public reference status."
        )

    if reference.get("authorization") is not False:
        raise ValueError(
            "This profile must not claim authorization."
        )

    if verification.get("status") != "NOT_VERIFIED":
        raise ValueError(
            "Public reference must remain unverified."
        )

    if configuration.get(
        "testing_mode"
    ) != "PUBLIC_REFERENCE_ONLY":

        raise ValueError(
            "Incorrect public reference testing mode."
        )

    if not configuration.get(
        "domain_variation_generation_enabled"
    ):

        raise ValueError(
            "Domain variation generation is disabled."
        )

    if not configuration.get(
        "similarity_analysis_enabled"
    ):

        raise ValueError(
            "Similarity analysis is disabled."
        )

    if configuration.get(
        "candidate_dns_lookups_enabled"
    ):

        raise ValueError(
            "Candidate DNS lookups must remain disabled."
        )

    if configuration.get(
        "external_website_scanning_enabled"
    ):

        raise ValueError(
            "External website scanning must remain disabled."
        )

    if configuration.get(
        "third_party_scanning_enabled"
    ):

        raise ValueError(
            "Third-party scanning must remain disabled."
        )

    return profile


# =====================================
# RUN KCG MODULE 1
# =====================================

def run_analysis(profile, dns_enabled):

    organization_name = profile[
        "organization_name"
    ]

    official_domain = profile[
        "official_domain"
    ]

    print("\n================================")
    print("       ORGANIZATION PROFILE")
    print("================================")

    print("Organization:", organization_name)

    print("Official domain:", official_domain)

    print("DNS enabled:", dns_enabled)

    print("\nStarting Module 1...")

    # Run domain analysis
    report = analyze_domain(
        official_domain,
        dns_enabled=dns_enabled
    )

    # Attach organization information
    report["organization_profile"] = {

        "organization_id": profile["organization_id"],

        "organization_name": organization_name,

        "organization_type": profile[
            "organization_type"
        ],

        "official_domain": official_domain,

        "verification_status": profile.get(
            "verification", {}
        ).get(
            "status",
            profile.get(
                "reference_information", {}
            ).get("reference_status")
        ),

        "domain_verified": profile.get(
            "verification", {}
        ).get("domain_verified", False),

        "testing_mode": profile[
            "testing_configuration"
        ]["testing_mode"],

        "authorization": profile.get(
            "reference_information", {}
        ).get("authorization", False)
    }

    # Display results
    display_results(report)

    # Save report
    report_path = save_report(report)

    print("\n================================")
    print("       REPORT SAVED")
    print("================================")

    print(report_path)


# =====================================
# MAIN PROGRAM
# =====================================

def main():

    print("================================")
    print("       KHMER CYBERGUARD")
    print("       MODULE 1")
    print("================================")

    print("\nSelect testing profile:")

    print("1. Sample Bank - Local Testing")

    print("2. ABA Bank - Public Reference Testing")

    choice = input("\nChoose 1 or 2: ").strip()

    try:

        if choice == "1":

            profile = load_organization_profile()

            run_analysis(
                profile,
                dns_enabled=True
            )

        elif choice == "2":

            profile = load_aba_reference_profile()

            run_analysis(
                profile,
                dns_enabled=False
            )

        else:

            print("\nInvalid selection.")

    except (
        FileNotFoundError,
        json.JSONDecodeError,
        KeyError,
        ValueError,
        RuntimeError,
        OSError
    ) as error:

        print("\nKCG Error:", error)

    except Exception as error:

        print("\nUnexpected KCG error:", error)


if __name__ == "__main__":
    main()