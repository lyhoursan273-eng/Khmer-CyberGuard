import json
import re
from datetime import datetime, timezone
from pathlib import Path

from backend.modules.dnstwist_runner import generate_variations

from backend.modules.domain_comparison import (
    normalize_domain,
    compare_domains
)

from backend.modules.levenshtein import (
    levenshtein_distance,
    similarity_percentage
)

from backend.modules.dns_enrichment import check_dns_records

from backend.modules.evidence_collector import collect_evidence


# =====================================
# PROJECT SETTINGS
# =====================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORTS_DIR = PROJECT_ROOT / "reports"

MAX_DNS_LOOKUPS = 10

DNS_RECORD_TYPES = ["A", "AAAA", "MX", "NS"]


# =====================================
# DOMAIN VALIDATION
# =====================================

def validate_domain(domain: str, dns_enabled: bool = True) -> str:

    domain = normalize_domain(domain).rstrip(".")

    if not domain:
        raise ValueError("Domain cannot be empty.")

    if (
        "://" in domain
        or "/" in domain
        or " " in domain
        or len(domain) > 253
    ):
        raise ValueError("Invalid domain format.")

    labels = domain.split(".")

    label_pattern = re.compile(
        r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$"
    )

    if len(labels) < 2 or not all(
        label_pattern.fullmatch(label)
        for label in labels
    ):
        raise ValueError("Invalid domain format.")

    # DNS-enabled local testing is restricted to .example
    if dns_enabled and labels[-1] != "example":
        raise ValueError(
            "DNS-enabled testing requires a fictional .example domain."
        )

    return domain


# =====================================
# MODULE 1: DOMAIN ANALYSIS
# =====================================

def analyze_domain(
    official_domain: str,
    dns_enabled: bool = True
) -> dict:

    official = validate_domain(
        official_domain,
        dns_enabled
    )

    generated_at = datetime.now(
        timezone.utc
    ).isoformat()

    # Step 1: Generate variations
    print("\n[1/5] Generating domain variations...")

    candidates = generate_variations(official)

    print("Generated:", len(candidates))

    results = []

    # Step 2: Calculate similarity
    print("\n[2/5] Calculating similarity...")

    for candidate in candidates:

        candidate = normalize_domain(candidate)

        distance = levenshtein_distance(
            official,
            candidate
        )

        similarity = similarity_percentage(
            official,
            candidate
        )

        results.append({

            "domain": candidate,

            "discovery_source": "DNSTwist",

            "exact_match": compare_domains(
                official,
                candidate
            ),

            "edit_distance": distance,

            "similarity_percentage": similarity,

            "dns_lookup_status": "not_checked",

            "dns_records": {}
        })

    # Rank candidates
    results.sort(
        key=lambda item: (
            -item["similarity_percentage"],
            item["edit_distance"],
            item["domain"]
        )
    )

    # Step 3: DNS enrichment
    print("\n[3/5] DNS enrichment...")

    if dns_enabled:

        print("DNS lookup mode: ENABLED")

        for item in results[:MAX_DNS_LOOKUPS]:

            try:

                item["dns_records"] = check_dns_records(
                    item["domain"]
                )

                item["dns_lookup_status"] = "completed"

            except Exception as error:

                item["dns_lookup_status"] = "error"

                item["dns_error"] = str(error)

    else:

        print("DNS lookup mode: DISABLED")
        print("Public reference mode: Offline candidate analysis only.")

    # Count DNS results
    dns_completed = sum(
        item["dns_lookup_status"] == "completed"
        for item in results
    )

    dns_failed = sum(
        item["dns_lookup_status"] == "error"
        for item in results
    )

    dns_not_checked = sum(
        item["dns_lookup_status"] == "not_checked"
        for item in results
    )

    # Step 4: Evidence collection
    print("\n[4/5] Collecting evidence...")

    evidence_records = collect_evidence(
        official,
        results,
        generated_at
    )

    # Step 5: Prepare report
    print("\n[5/5] Preparing report...")

    run_mode = (
        "LOCAL_SCENARIOS"
        if dns_enabled
        else "PUBLIC_REFERENCE_ONLY"
    )

    report = {

        "project": "Khmer CyberGuard",

        "module": "Module 1 - Domain Similarity Detection",

        "generated_at_utc": generated_at,

        "official_domain": official,

        "run_mode": run_mode,

        "methodology": {

            "discovery_tool": "DNSTwist",

            "discovery_mode": "List mode",

            "similarity_algorithm": "Levenshtein Distance",

            "dns_tool": "dnspython",

            "dns_record_types": DNS_RECORD_TYPES,

            "dns_lookup_enabled": dns_enabled,

            "dns_lookup_limit": MAX_DNS_LOOKUPS,

            "website_scanning_enabled": False,

            "third_party_scanning_enabled": False,

            "evidence_tool": "KCG Evidence Collector",

            "interpretation": (
                "Similarity measures text similarity, "
                "not phishing probability."
            )
        },

        "summary": {

            "total_candidates": len(results),

            "dns_candidates_checked": dns_completed,

            "dns_candidates_failed": dns_failed,

            "dns_candidates_not_checked": dns_not_checked,

            "total_evidence_records": len(evidence_records)
        },

        "results": results,

        "evidence": evidence_records
    }

    return report


# =====================================
# SAVE JSON REPORT
# =====================================

def save_report(report: dict) -> Path:

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save a separate report for each reference domain
    domain_slug = re.sub(
        r"[^a-z0-9]+",
        "_",
        report["official_domain"]
    ).strip("_")

    report_file = (
        REPORTS_DIR / f"module1_{domain_slug}_report.json"
    )

    report_file.write_text(
        json.dumps(
            report,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    return report_file


# =====================================
# DISPLAY RESULTS
# =====================================

def display_results(report: dict):

    print("\n================================")
    print("       KCG MODULE 1 RESULTS")
    print("================================")

    print("Official domain:", report["official_domain"])

    print("Run mode:", report["run_mode"])

    print("\nSUMMARY")

    for key, value in report["summary"].items():
        print(f"{key}: {value}")

    print("\nTOP 10 DOMAIN CANDIDATES")

    for item in report["results"][:10]:

        print("\nDomain:", item["domain"])

        print(
            "Similarity:",
            item["similarity_percentage"],
            "%"
        )

        print(
            "Edit distance:",
            item["edit_distance"]
        )

        print(
            "DNS status:",
            item["dns_lookup_status"]
        )


# =====================================
# STANDALONE TEST
# =====================================

if __name__ == "__main__":

    print("=== KHMER CYBERGUARD MODULE 1 ===")

    domain = input(
        "\nEnter fictional .example domain: "
    ).strip()

    if not domain:
        domain = "samplebank.example"

    try:

        report = analyze_domain(
            domain,
            dns_enabled=True
        )

        display_results(report)

        report_path = save_report(report)

        print("\nReport saved successfully:")
        print(report_path)

    except (ValueError, RuntimeError, OSError) as error:

        print("\nKCG Error:", error)