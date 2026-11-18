import json
import os
import shutil
import subprocess

from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlsplit


# =====================================
# PROJECT SETTINGS
# =====================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ALLOWED_HOST = "127.0.0.1"
ALLOWED_PORT = 8000

ALLOWED_PATHS = {
    "/legitimate_bank.html",
    "/suspicious_bank.html"
}


# =====================================
# FIND PROJECTDISCOVERY HTTPX
# =====================================

def find_httpx() -> Path:

    candidates = []

    go_bin = os.environ.get("GOBIN")

    if go_bin:
        candidates.append(
            Path(go_bin) / "httpx.exe"
        )

    else:
        gopath = os.environ.get(
            "GOPATH",
            str(Path.home() / "go")
        )

        for path in gopath.split(os.pathsep):

            candidates.append(
                Path(path) / "bin" / "httpx.exe"
            )

    for candidate in candidates:

        if candidate.is_file():
            return candidate

    path_executable = shutil.which("httpx")

    if path_executable:
        return Path(path_executable)

    raise FileNotFoundError(
        "ProjectDiscovery httpx was not found."
    )


# =====================================
# VALIDATE LOCAL TEST URL
# =====================================

def validate_test_url(url: str) -> None:

    parsed = urlsplit(url)

    if parsed.scheme != "http":
        raise ValueError(
            "Only HTTP is allowed for this local test."
        )

    if parsed.hostname != ALLOWED_HOST:
        raise ValueError(
            "Only the approved localhost address is allowed."
        )

    if parsed.port != ALLOWED_PORT:
        raise ValueError(
            "Unexpected testing port."
        )

    if parsed.username or parsed.password:
        raise ValueError(
            "URLs containing credentials are not allowed."
        )

    if parsed.path not in ALLOWED_PATHS:
        raise ValueError(
            "URL is not in the approved local test list."
        )

    if parsed.query or parsed.fragment:
        raise ValueError(
            "Query strings and fragments are not allowed."
        )


# =====================================
# HTTPX INFORMATION COLLECTOR
# =====================================

def collect_httpx_info(url: str) -> dict:

    validate_test_url(url)

    httpx_exe = find_httpx()

    command = [

        str(httpx_exe),

        "-u", url,

        "-allow", ALLOWED_HOST,

        "-title",

        "-status-code",

        "-server",

        "-json",

        "-silent"
    ]

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False
        )

    except subprocess.TimeoutExpired as error:

        raise RuntimeError(
            "httpx request timed out."
        ) from error

    if result.returncode != 0:

        raise RuntimeError(
            result.stderr.strip()
            or "httpx execution failed."
        )

    # Parse the JSONL output.
    records = []

    for line in result.stdout.splitlines():

        try:

            item = json.loads(line)

            if isinstance(item, dict):
                records.append(item)

        except json.JSONDecodeError:
            continue

    if not records:

        raise RuntimeError(
            "httpx did not return a valid JSON record."
        )

    raw = records[0]

    # Keep useful fields with their original names.
    fields = [

        "timestamp",
        "url",
        "input",
        "scheme",
        "host",
        "host_ip",
        "port",
        "path",
        "status_code",
        "title",
        "webserver",
        "content_type",
        "method",
        "time",
        "a",
        "tech",
        "words",
        "lines",
        "content_length",
        "failed"
    ]

    technical_details = {

        field: raw[field]

        for field in fields

        if field in raw
    }

    report = {

        "source_tool": "ProjectDiscovery httpx",

        "observed_at_utc": (
            datetime.now(timezone.utc).isoformat()
        ),

        "requested_url": url,

        "technical_details": technical_details
    }

    return report


# =====================================
# TEST BOTH LOCAL WEBSITES
# =====================================

def main():

    test_urls = [

        "http://127.0.0.1:8000/legitimate_bank.html",

        "http://127.0.0.1:8000/suspicious_bank.html"

    ]

    for url in test_urls:

        try:

            print("\n================================")
            print("KCG HTTPX INFORMATION")
            print("================================")

            report = collect_httpx_info(url)

            print(
                json.dumps(
                    report,
                    indent=4,
                    ensure_ascii=False
                )
            )

        except (
            FileNotFoundError,
            ValueError,
            RuntimeError,
            OSError
        ) as error:

            print("\nKCG Error:", error)


if __name__ == "__main__":
    main()