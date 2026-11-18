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