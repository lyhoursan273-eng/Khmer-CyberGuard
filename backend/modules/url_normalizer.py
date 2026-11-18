from urllib.parse import urlsplit, urlunsplit

from .url_validator import validate_url


def normalize_url(url: str) -> dict:
    """
    Normalize a URL after validating it for KCG local testing.

    This function does not visit the URL or make network requests.
    """

    validation = validate_url(url)

    if not validation["is_valid"]:
        return {
            "is_valid": False,
            "reason": validation["reason"],
            "normalized_url": None
        }

    parsed = urlsplit(url)

    scheme = parsed.scheme.lower()
    hostname = parsed.hostname.lower()
    port = parsed.port

    # Remove the default port for each protocol.
    if (scheme == "https" and port == 443) or (
        scheme == "http" and port == 80
    ):
        port = None

    # Rebuild the hostname and optional non-default port.
    if port is None:
        netloc = hostname
    else:
        netloc = f"{hostname}:{port}"

    # Keep the original path and query.
    # Remove the fragment because it is not sent to the server.
    path = parsed.path or "/"

    normalized_url = urlunsplit((
        scheme,
        netloc,
        path,
        parsed.query,
        ""
    ))

    return {
        "is_valid": True,
        "reason": "URL normalized successfully.",
        "normalized_url": normalized_url
    }