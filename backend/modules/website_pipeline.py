import json
from datetime import datetime, timezone
from pathlib import Path

from backend.modules.website_analyzer import analyze_html_file

from backend.modules.rule_based_analyzer import analyze_indicators

from backend.modules.evidence_collector import (
    collect_website_evidence,
    collect_httpx_evidence
)

from backend.modules.httpx_collector import collect_httpx_info
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

REPORTS_DIR = PROJECT_ROOT / "reports"

EXPECTED_BRAND = "Sample Bank"


# =====================================
# MODULE 2 PIPELINE
# =====================================

def analyze_website(
    filename: str,
    include_httpx: bool = False
) -> dict:

    # Only allow the two prepared local test files.
    allowed_files = {
        "legitimate_bank.html",
        "suspicious_bank.html"
    }

    if filename not in allowed_files:
        raise ValueError("Unsupported local test file.")

    generated_at = datetime.now(
        timezone.utc
    ).isoformat()

    file_path = WEBSITES_DIR / filename

    # Step 1: Extract website information
    print("\n[1/4] Extracting website information...")

    website_data = analyze_html_file(file_path)

    # Step 2: Analyze suspicious indicators
    print("[2/4] Analyzing website indicators...")

    analysis_result = analyze_indicators(
        website_data,
        EXPECTED_BRAND
    )

    # Step 3: Collect evidence
    print("[3/4] Collecting website evidence...")

    evidence = collect_website_evidence(
        analysis_result,
        generated_at
    )
        # Step 4: Collect local technical information

    httpx_info = None
    httpx_evidence = []

    if include_httpx:

        print(
            "[4/5] Collecting technical information with httpx..."
        )

        test_url = (
            f"http://127.0.0.1:8000/{filename}"
        )

        try:

            httpx_info = collect_httpx_info(test_url)

            httpx_evidence = collect_httpx_evidence(
             httpx_info,
             generated_at
            )   

        except (
            FileNotFoundError,
            ValueError,
            RuntimeError,
            OSError
        ) as error:

            httpx_info = {
                "source_tool": "ProjectDiscovery httpx",
                "status": "unavailable",
                "error": str(error)
            }

    else:

        print("[4/5] httpx collection skipped.")

    print("[5/5] Preparing JSON report...")
# Combine website and technical evidence
    evidence.extend(httpx_evidence)
    # Step 4: Prepare report
    print("[4/4] Preparing JSON report...")

    report = {

        "project": "Khmer CyberGuard",

        "module": "Module 2 - Website and Phishing Analysis",

        "generated_at_utc": generated_at,

        "run_mode": "LOCAL_FIXTURE_TESTING",

        "source_file": filename,

        "methodology": {

            "html_analyzer": "BeautifulSoup4",

            "detection_engine": "KCG Rule-Based Analyzer",

            "evidence_collector": "KCG Evidence Collector",

            "external_website_scanning_enabled": False,

            "third_party_scanning_enabled": False,
            "httpx_collector": "ProjectDiscovery httpx",
            "local_httpx_enabled": include_httpx,
           
        },

        "summary": {

            "website_title": analysis_result["website_title"],

            "expected_brand": EXPECTED_BRAND,

            "assessment": analysis_result["assessment"],

            "indicator_count": analysis_result["indicator_count"],

            "evidence_count": len(evidence)
        },

        "website_analysis": analysis_result,
        "httpx_technical_info": httpx_info,

        "evidence": evidence,

        "interpretation": (
            "Rule-based warning indicators require investigation. "
            "They do not prove that a website is phishing."
        )
    }

    return report


# =====================================
# SAVE REPORT
# =====================================

def save_report(report: dict) -> Path:

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = report["source_file"].replace(
        ".html",
        "_report.json"
    )

    report_path = (
        REPORTS_DIR / f"module2_{filename}"
    )

    report_path.write_text(
        json.dumps(
            report,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    return report_path


# =====================================
# DISPLAY RESULTS
# =====================================

def display_results(report: dict):

    print("\n================================")
    print("       KCG MODULE 2")
    print("       ANALYSIS RESULTS")
    print("================================")

    summary = report["summary"]

    print("Website:", summary["website_title"])

    print("Expected brand:", summary["expected_brand"])

    print("Assessment:", summary["assessment"])

    print("Indicators:", summary["indicator_count"])

    print("Evidence records:", summary["evidence_count"])


# =====================================
# MAIN PROGRAM
# =====================================

def main():

    test_files = [
        "legitimate_bank.html",
        "suspicious_bank.html"
    ]

    for filename in test_files:

        try:

            print("\nTesting:", filename)

            report = analyze_website(
                filename,
                include_httpx=True
            )

            display_results(report)

            report_path = save_report(report)

            print("\nReport saved:")
            print(report_path)

        except (FileNotFoundError, ValueError, OSError) as error:

            print("\nKCG Error:", error)


if __name__ == "__main__":
    main()