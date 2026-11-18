import json
import re
from pathlib import Path

from backend.modules.website_analyzer import analyze_html_file


# =====================================
# PROJECT SETTINGS
# =====================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

WEBSITES_DIR = (
    PROJECT_ROOT
    / "data"
    / "test_cases"
    / "websites"
)

EXPECTED_BRAND = "Sample Bank"


# =====================================
# TEXT NORMALIZATION
# =====================================

def normalize_text(text: str) -> str:

    return re.sub(
        r"[^a-z0-9]",
        "",
        text.lower()
    )


# =====================================
# RULE-BASED ANALYSIS
# =====================================

def analyze_indicators(
    website_data: dict,
    expected_brand: str
) -> dict:

    page_text = website_data.get(
        "page_text", ""
    ).lower()

    indicators = []

    # ---------------------------------
    # 1. Check urgent language
    # ---------------------------------

    urgent_keywords = [
        "urgent",
        "immediate",
        "account suspension",
        "failure to verify",
        "verify immediately"
    ]

    matched_urgent = [
        word for word in urgent_keywords
        if word in page_text
    ]

    if matched_urgent:

        indicators.append({
            "type": "urgent_language",
            "severity": "medium",
            "matched_terms": matched_urgent,
            "description": (
                "The website contains urgent or "
                "pressure-based language."
            )
        })

    # ---------------------------------
    # 2. Check password fields
    # ---------------------------------

    password_fields = [
        field
        for field in website_data.get(
            "input_fields", []
        )
        if field.get("type", "").lower() == "password"
    ]

    if password_fields:

        indicators.append({
            "type": "password_field_present",
            "severity": "contextual",
            "count": len(password_fields),
            "description": (
                "Password input fields were found. "
                "This can be normal on banking websites "
                "and requires further context."
            )
        })

    # ---------------------------------
    # 3. Check OTP requests
    # ---------------------------------

    otp_keywords = [
        "otp",
        "one-time verification code",
        "verification code"
    ]

    matched_otp = [
        word for word in otp_keywords
        if word in page_text
    ]

    if matched_otp:

        indicators.append({
            "type": "otp_language",
            "severity": "medium",
            "matched_terms": matched_otp,
            "description": (
                "The website contains language "
                "requesting verification codes."
            )
        })

    # ---------------------------------
    # 4. Check payment requests
    # ---------------------------------

    payment_keywords = [
        "payment is requested",
        "payment required",
        "pay now",
        "fee to restore",
        "payment notice"
    ]

    matched_payment = [
        word for word in payment_keywords
        if word in page_text
    ]

    if matched_payment:

        indicators.append({
            "type": "payment_request_language",
            "severity": "medium",
            "matched_terms": matched_payment,
            "description": (
                "The website contains payment-related "
                "request language."
            )
        })

    # ---------------------------------
    # 5. Check brand consistency
    # ---------------------------------

    for metadata in website_data.get(
        "metadata", []
    ):

       if (metadata.get("name") or "").lower() == "organization":

            observed_brand = metadata.get(
                "content", ""
            )

            if (
                observed_brand
                and normalize_text(observed_brand)
                != normalize_text(expected_brand)
            ):

                indicators.append({
                    "type": "brand_inconsistency",
                    "severity": "medium",
                    "expected_brand": expected_brand,
                    "observed_brand": observed_brand,
                    "description": (
                        "Organization metadata does not "
                        "match the expected brand."
                    )
                })

    # ---------------------------------
    # 6. Prepare assessment
    # ---------------------------------

    assessment = (
        "REVIEW_REQUIRED"
        if indicators
        else "NO_INDICATORS_DETECTED_BY_CURRENT_RULES"
    )

    return {

        "website_title": website_data.get(
            "website_title"
        ),

        "expected_brand": expected_brand,

        "indicator_count": len(indicators),

        "assessment": assessment,

        "indicators": indicators,

        "interpretation": (
            "These are rule-based warning indicators, "
            "not proof that a website is phishing."
        )
    }


# =====================================
# TEST BOTH WEBSITES
# =====================================

def main():

    test_files = [
        "legitimate_bank.html",
        "suspicious_bank.html"
    ]

    for filename in test_files:

        file_path = WEBSITES_DIR / filename

        try:

            website_data = analyze_html_file(
                file_path
            )

            result = analyze_indicators(
                website_data,
                EXPECTED_BRAND
            )

            print("\n================================")
            print("KCG MODULE 2")
            print("RULE-BASED ANALYSIS")
            print("================================")

            print("File:", filename)

            print(
                json.dumps(
                    result,
                    indent=4,
                    ensure_ascii=False
                )
            )

        except (FileNotFoundError, ValueError, OSError) as error:

            print("\nKCG Error:", error)


if __name__ == "__main__":
    main()