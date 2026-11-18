from datetime import datetime, timezone
from uuid import uuid4


def collect_url_evidence(
    threat_result: dict,
    generated_at: str | None = None
) -> list:
    """
    Create evidence records from Module 3 URL threat-intelligence results.

    Only completed MATCH_FOUND and NO_MATCH checks create records.
    All records are clearly marked as synthetic test evidence.
    """

    if not isinstance(threat_result, dict):
        return []

    status = threat_result.get("status")

    if status not in ("MATCH_FOUND", "NO_MATCH"):
        return []

    timestamp = generated_at or datetime.now(
        timezone.utc
    ).isoformat()

    evidence_id = f"KCG-EV-M3-{uuid4()}"

    common_fields = {
        "evidence_id": evidence_id,
        "collected_at_utc": timestamp,
        "source_tool": "KCG_SYNTHETIC_TEST_FEED",
        "severity": "informational",
        "checked_url": threat_result.get("checked_url"),
        "normalized_url": threat_result.get("normalized_url"),
        "feed_name": threat_result.get("feed_name"),
        "test_only": True
    }

    if status == "MATCH_FOUND":

        match = threat_result.get("match") or {}

        evidence = {
            **common_fields,
            "evidence_type": "url_threat_intelligence_match",
            "description": (
                "URL matched a synthetic phishing simulation record."
            ),
            "details": {
                "record_id": match.get("record_id"),
                "threat_type": match.get("threat_type"),
                "source": match.get("source"),
                "record_status": match.get("record_status")
            },
            "interpretation": (
                "This is synthetic testing evidence, "
                "not a confirmed real-world threat."
            )
        }

    else:

        evidence = {
            **common_fields,
            "evidence_type": "url_threat_intelligence_no_match",
            "description": (
                "No matching record was found in the synthetic feed."
            ),
            "details": None,
            "interpretation": (
                "NO_MATCH does not establish that the URL is safe."
            )
        }

    return [evidence]