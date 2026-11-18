import json
from datetime import datetime, timezone
from pathlib import Path

from backend.modules.threat_intel_checker import (
    check_threat_intelligence
)
from backend.modules.url_evidence import collect_url_evidence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = PROJECT_ROOT / "reports"


def analyze_url(url: str) -> dict:
    """
    Run the complete KCG Module 3 URL analysis workflow.

    Uses only the local synthetic threat-intelligence feed.
    No external websites or APIs are accessed.
    """

    generated_at = datetime.now(timezone.utc).isoformat()

    # Step 1: Check the URL against the synthetic feed.
    threat_result = check_threat_intelligence(url)

    # Step 2: Collect evidence from the result.
    evidence_records = collect_url_evidence(
        threat_result,
        generated_at
    )

    # Step 3: Prepare the summary.
    status = threat_result["status"]

    summary = {
        "analysis_status": status,
        "match_found": status == "MATCH_FOUND",
        "evidence_count": len(evidence_records)
    }

    # Step 4: Prepare the complete report.
    report = {
        "project": "Khmer CyberGuard (KCG)",
        "module": "Module 3 - Malicious URL Checking",
        "generated_at_utc": generated_at,
        "run_mode": "LOCAL_SYNTHETIC_FEED_TESTING",

        "methodology": {
            "url_validation": True,
            "url_normalization": True,
            "threat_intelligence_checking": True,
            "evidence_collection": True,
            "external_api_enabled": False,
            "external_website_scanning_enabled": False,
            "synthetic_feed_only": True
        },

        "input_url": url,
        "threat_intelligence": threat_result,
        "summary": summary,
        "evidence": evidence_records,

        "interpretation": threat_result["interpretation"]
    }

    return report


def save_report(report: dict) -> str:
    """
    Save the Module 3 report as a JSON file.
    """

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%dT%H%M%SZ")

    report_path = REPORTS_DIR / (
        f"module3_url_report_{timestamp}.json"
    )

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )

    return str(report_path)


def display_results(report: dict) -> None:
    """
    Display a readable summary of the URL analysis.
    """

    print("\n" + "=" * 60)
    print("       KHMER CYBERGUARD - MODULE 3")
    print("          MALICIOUS URL CHECKING")
    print("=" * 60)

    print(f"\nSubmitted URL: {report['input_url']}")

    print(
        "\nAnalysis Status: "
        + report["summary"]["analysis_status"]
    )

    print(
        "Evidence Records: "
        + str(report["summary"]["evidence_count"])
    )

    print("\nInterpretation:")
    print(report["interpretation"])

    if report["evidence"]:
        print("\nEvidence:")

        for record in report["evidence"]:
            print(f"  Evidence ID: {record['evidence_id']}")
            print(f"  Type: {record['evidence_type']}")
            print(f"  Severity: {record['severity']}")

    print("\n" + "=" * 60)


def main():
    # Fictional URL used for local testing.
    test_url = (
        "https://samplebank-login.example/verify-account"
    )

    report = analyze_url(test_url)

    display_results(report)

    report_path = save_report(report)

    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()