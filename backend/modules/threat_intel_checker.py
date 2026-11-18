import json
from pathlib import Path

from backend.modules.url_normalizer import normalize_url


# Locate the KCG project directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Use our local synthetic threat-intelligence feed.
DEFAULT_FEED_PATH = (
    PROJECT_ROOT
    / "data"
    / "threat_intel"
    / "sample_threat_records.json"
)


def check_threat_intelligence(url: str) -> dict:
    """
    Compare a validated and normalized URL against
    KCG's local synthetic threat-intelligence feed.

    No external API or network requests are used.
    """

    result = {
        "status": "CHECK_FAILED",
        "checked_url": url,
        "normalized_url": None,
        "feed_name": None,
        "match": None,
        "interpretation": ""
    }

    # 1. Validate and normalize the submitted URL.
    normalization = normalize_url(url)

    if not normalization["is_valid"]:
        result["interpretation"] = (
            "URL validation failed: "
            + normalization["reason"]
        )
        return result

    normalized_url = normalization["normalized_url"]
    result["normalized_url"] = normalized_url

    # 2. Load the local feed.
    try:
        with DEFAULT_FEED_PATH.open("r", encoding="utf-8") as file:
            feed = json.load(file)

    except (OSError, json.JSONDecodeError) as error:
        result["interpretation"] = (
            f"Unable to load threat-intelligence feed: {error}"
        )
        return result

    # 3. Verify that this is our synthetic testing feed.
    metadata = feed.get("feed_metadata")

    if not isinstance(metadata, dict):
        result["interpretation"] = (
            "Invalid feed: metadata is missing."
        )
        return result

    if (
        metadata.get("feed_type") != "SYNTHETIC_TEST_FIXTURE"
        or metadata.get("is_real_threat_intelligence") is not False
    ):
        result["interpretation"] = (
            "Feed rejected: it is not the approved synthetic test feed."
        )
        return result

    records = feed.get("records")

    if not isinstance(records, list):
        result["interpretation"] = (
            "Invalid feed: records must be a list."
        )
        return result

    result["feed_name"] = metadata.get("feed_name")

    # 4. Compare the normalized URL with test records.
    for record in records:

        if not isinstance(record, dict):
            continue

        # Only accept records explicitly marked as test fixtures.
        if (
            record.get("test_only") is not True
            or record.get("source") != "KCG_SYNTHETIC_FIXTURE"
        ):
            continue

        if record.get("normalized_url") == normalized_url:

            result.update({
                "status": "MATCH_FOUND",
                "match": {
                    "record_id": record.get("record_id"),
                    "threat_type": record.get("threat_type"),
                    "source": record.get("source"),
                    "record_status": record.get("status")
                },
                "interpretation": (
                    "The URL matches a synthetic phishing simulation "
                    "record. This is a test result, not a real-world "
                    "threat verdict."
                )
            })

            return result

    # 5. No matching record was found.
    result.update({
        "status": "NO_MATCH",
        "interpretation": (
            "No matching record was found in the current synthetic "
            "feed. This does not establish that the URL is safe."
        )
    })

    return result