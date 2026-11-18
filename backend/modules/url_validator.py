import re
from urllib.parse import urlsplit


# KCG currently accepts fictional .example domains for local testing.
DOMAIN_PATTERN = re.compile(
    r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+example$"
)


def validate_url(url: str) -> dict:
    """
    Validate a URL's format for KCG local testing.

    This function only parses the URL.
    It does not visit the website or perform network requests.
    """

    result = {
        "is_valid": False,
        "reason": "",
        "scheme": None,
        "hostname": None,
        "port": None,
        "path": None
    }

    # 1. Check input
    if not isinstance(url, str) or not url.strip():
        result["reason"] = "URL must be a non-empty string."
        return result

    if url != url.strip():
        result["reason"] = "URL must not contain surrounding whitespace."
        return result

    if any(character.isspace() for character in url):
        result["reason"] = "URL must not contain whitespace."
        return result

    # 2. Parse URL
    try:
        parsed = urlsplit(url)

        scheme = parsed.scheme.lower()
        hostname = parsed.hostname
        port = parsed.port

    except ValueError:
        result["reason"] = "URL format or port is invalid."
        return result

    # 3. Check protocol
    if scheme not in ("http", "https"):
        result["reason"] = "Only HTTP and HTTPS URLs are accepted."
        return result

    # 4. Check hostname
    if not hostname:
        result["reason"] = "URL must contain a hostname."
        return result

    # 5. Reject embedded credentials
    if parsed.username is not None or parsed.password is not None:
        result["reason"] = "URLs containing embedded credentials are rejected."
        return result

    # 6. Restrict testing to fictional domains
    if not DOMAIN_PATTERN.fullmatch(hostname.lower()):
        result["reason"] = (
            "Only fictional .example domains are accepted "
            "in the current testing mode."
        )
        return result

    # 7. URL is valid
    result.update({
        "is_valid": True,
        "reason": "URL is valid for KCG local testing.",
        "scheme": scheme,
        "hostname": hostname.lower(),
        "port": port,
        "path": parsed.path or "/"
    })

    return result