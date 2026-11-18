from uuid import uuid4

def collect_evidence(
    official_domain: str,
    results: list,
    generated_at: str
) -> list:

    evidence_records = []

    evidence_number = 1

    for item in results:

        # Record domain similarity evidence
        evidence = {
            "evidence_id": f"KCG-EV-{evidence_number:05d}",
            "evidence_type": "domain_similarity",
            "observed_at_utc": generated_at,
            "official_domain": official_domain,
            "candidate_domain": item["domain"],
            "source_tool": "DNSTwist + Python",
            "edit_distance": item["edit_distance"],
            "similarity_percentage": item[
                "similarity_percentage"
            ],
            "interpretation": (
                "Text similarity only. "
                "Not proof of phishing."
            )
        }

        evidence_records.append(evidence)

        evidence_number += 1

        # Record DNS evidence when a lookup was attempted
        if item["dns_lookup_status"] != "not_checked":

            dns_evidence = {
                "evidence_id": f"KCG-EV-{evidence_number:05d}",
                "evidence_type": "dns_lookup",
                "observed_at_utc": generated_at,
                "domain": item["domain"],
                "source_tool": "dnspython",
                "lookup_status": item["dns_lookup_status"],
                "dns_records": item.get("dns_records", {})
            }

            if "dns_error" in item:
                dns_evidence["error"] = item["dns_error"]

            evidence_records.append(dns_evidence)

            evidence_number += 1

    return evidence_records


# Test the evidence collector
if __name__ == "__main__":

    sample_results = [
        {
            "domain": "samplebank0.example",
            "edit_distance": 1,
            "similarity_percentage": 94.74,
            "dns_lookup_status": "completed",
            "dns_records": {
                "A": {
                    "status": "nxdomain",
                    "records": []
                }
            }
        }
    ]

    evidence = collect_evidence(
        "samplebank.example",
        sample_results,
        "2026-11-18T00:00:00+00:00"
    )

    for record in evidence:
        print(record)

# =====================================
# MODULE 2: WEBSITE EVIDENCE
# =====================================

def collect_website_evidence(
    website_result: dict,
    generated_at: str
) -> list:
    """
    Collect evidence from Module 2 website analysis.

    Records warning indicators without declaring
    a website malicious.
    """

    if not isinstance(website_result, dict):
        raise ValueError("Website result must be a dictionary.")

    indicators = website_result.get("indicators", [])

    if not isinstance(indicators, list):
        raise ValueError("Indicators must be a list.")

    evidence_records = []

    # Create a summary record when no indicators are found.
    if not indicators:

        return [{
            "evidence_id": (
                f"KCG-EV-M2-{uuid4().hex[:12].upper()}"
            ),

            "evidence_type": "website_analysis_summary",

            "observed_at_utc": generated_at,

            "website_title": website_result.get(
                "website_title"
            ),

            "expected_brand": website_result.get(
                "expected_brand"
            ),

            "assessment": website_result.get(
                "assessment"
            ),

            "indicator_count": 0,

            "source_tool": (
                "BeautifulSoup4 + KCG Rule-Based Analyzer"
            ),

            "interpretation": (
                "No indicators were detected by the current "
                "rules. This does not prove the website is safe."
            )
        }]

    # Collect each detected indicator.
    for indicator in indicators:

        if not isinstance(indicator, dict):
            raise ValueError(
                "Each website indicator must be a dictionary."
            )

        evidence = {

            "evidence_id": (
                f"KCG-EV-M2-{uuid4().hex[:12].upper()}"
            ),

            "evidence_type": "website_indicator",

            "observed_at_utc": generated_at,

            "website_title": website_result.get(
                "website_title"
            ),

            "expected_brand": website_result.get(
                "expected_brand"
            ),

            "assessment": website_result.get(
                "assessment"
            ),

            "indicator_type": indicator.get(
                "type", "unknown"
            ),

            "severity": indicator.get(
                "severity", "unknown"
            ),

            "indicator_details": indicator,

            "source_tool": (
                "BeautifulSoup4 + KCG Rule-Based Analyzer"
            ),

            "interpretation": (
                "This is a warning indicator for investigation, "
                "not proof of phishing."
            )
        }

        evidence_records.append(evidence)

    return evidence_records
# =====================================
# MODULE 2: HTTPX TECHNICAL EVIDENCE
# =====================================

def collect_httpx_evidence(
    httpx_result: dict,
    generated_at: str
) -> list:
    """
    Record technical website observations
    collected by ProjectDiscovery httpx.

    Technical observations are not proof of phishing.
    """

    if not isinstance(httpx_result, dict):
        raise ValueError(
            "HTTPX result must be a dictionary."
        )

    technical_details = httpx_result.get(
        "technical_details"
    )

    # Do not create evidence from failed or empty results.
    if not isinstance(technical_details, dict):
        return []

    if not technical_details:
        return []

    evidence = {

        "evidence_id": (
            f"KCG-EV-M2-{uuid4().hex[:12].upper()}"
        ),

        "evidence_type": "website_technical_observation",

        "observed_at_utc": httpx_result.get(
            "observed_at_utc",
            generated_at
        ),

        "requested_url": httpx_result.get(
            "requested_url"
        ),

        "source_tool": "ProjectDiscovery httpx",

        "severity": "informational",

        "technical_details": technical_details,

        "interpretation": (
            "These are technical website observations. "
            "HTTP status, server information and detected "
            "technologies do not prove that a website is malicious."
        )
    }

    return [evidence]