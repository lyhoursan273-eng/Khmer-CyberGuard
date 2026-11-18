import shutil
import subprocess
import sys
from pathlib import Path


def generate_variations(domain: str) -> list[str]:

    domain = domain.strip().lower()

    if not domain:
        raise ValueError("Domain cannot be empty.")

    # Find DNSTwist inside our virtual environment
    executable = (
        shutil.which("dnstwist")
        or str(Path(sys.executable).parent / "dnstwist.exe")
    )

    if not Path(executable).exists():
        raise RuntimeError("DNSTwist executable was not found.")

    # Run DNSTwist in list mode
    result = subprocess.run(
        [executable, "--format", "list", domain],
        capture_output=True,
        text=True,
        timeout=60
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "DNSTwist failed.")

    # Collect generated domain names
    candidates = [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    ]

    # Remove duplicates and the original domain
    unique_candidates = list(dict.fromkeys(candidates))

    return [
        candidate
        for candidate in unique_candidates
        if candidate.lower() != domain
    ]


# Test DNSTwist integration
if __name__ == "__main__":

    test_domain = "mekongfinance.example"

    variations = generate_variations(test_domain)

    print("=== KCG DNSTwist Integration ===")
    print("Official domain:", test_domain)
    print("Total variations:", len(variations))

    print("\nFirst 10 candidates:")

    for candidate in variations[:10]:
        print(candidate)