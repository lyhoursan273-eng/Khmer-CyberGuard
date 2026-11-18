import json
import re

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from backend.modules.domain_pipeline import validate_domain
from backend.modules.domain_comparison import normalize_domain


# ==========================================
# PROJECT CONFIGURATION
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_ORGANIZATIONS_DIR = (
    PROJECT_ROOT
    / "data"
    / "organizations"
    / "registered"
)


EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)


# ==========================================
# INPUT VALIDATION
# ==========================================

def validate_required_text(value: str, field_name: str) -> str:

    if not isinstance(value, str):
        raise ValueError(
            f"{field_name} must be text."
        )

    value = value.strip()

    if not value:
        raise ValueError(
            f"{field_name} cannot be empty."
        )

    if len(value) > 150:
        raise ValueError(
            f"{field_name} is too long."
        )

    return value


def validate_contact_email(email: str) -> str:

    email = validate_required_text(
        email,
        "Contact email"
    )

    if not EMAIL_PATTERN.fullmatch(email):
        raise ValueError(
            "Invalid contact email format."
        )

    return email.lower()


# ==========================================
# DUPLICATE DOMAIN CHECK
# ==========================================

def check_duplicate_domain(
    official_domain: str,
    organizations_dir: Path
) -> None:

    if not organizations_dir.exists():
        return

    for profile_path in organizations_dir.glob("*.json"):

        try:
            with profile_path.open(
                "r",
                encoding="utf-8"
            ) as file:

                profile = json.load(file)

        except (OSError, json.JSONDecodeError) as error:

            raise RuntimeError(
                f"Cannot read organization profile: {profile_path.name}"
            ) from error

        existing_domain = profile.get(
            "official_domain",
            ""
        )

        if not isinstance(existing_domain, str):
            continue

        if (
            normalize_domain(existing_domain).rstrip(".")
            == official_domain
        ):

            raise ValueError(
                "This official domain is already registered."
            )


# ==========================================
# ORGANIZATION REGISTRATION
# ==========================================

def register_organization(
    organization_name: str,
    organization_type: str,
    contact_email: str,
    official_domain: str,
    brand_name: str | None = None,
    khmer_brand_name: str | None = None,
    brand_keywords: list | None = None,
    storage_dir: str | Path | None = None
) -> dict:

    """
    Register a new organization in KCG.

    Registration does not establish domain ownership.
    Every new organization remains PENDING_VERIFICATION.
    """

    # 1. Validate organization information.

    organization_name = validate_required_text(
        organization_name,
        "Organization name"
    )

    organization_type = validate_required_text(
        organization_type,
        "Organization type"
    )

    contact_email = validate_contact_email(
        contact_email
    )

    # 2. Validate and normalize official domain.
    # DNS testing restrictions are not enabled here.

    official_domain = validate_domain(
        official_domain,
        dns_enabled=False
    )

    # 3. Validate optional brand information.

    brand_name = (
        validate_required_text(brand_name, "Brand name")
        if brand_name
        else organization_name
    )

    if khmer_brand_name is not None:
        khmer_brand_name = validate_required_text(
            khmer_brand_name,
            "Khmer brand name"
        )

    if brand_keywords is None:
        brand_keywords = [brand_name]

    if not isinstance(brand_keywords, list):
        raise ValueError(
            "Brand keywords must be a list."
        )

    cleaned_keywords = []

    for keyword in brand_keywords:

        keyword = validate_required_text(
            keyword,
            "Brand keyword"
        )

        if keyword not in cleaned_keywords:
            cleaned_keywords.append(keyword)

    # 4. Prepare storage directory.

    organizations_dir = Path(
        storage_dir
        if storage_dir is not None
        else DEFAULT_ORGANIZATIONS_DIR
    )

    organizations_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # 5. Prevent duplicate official-domain registration.

    check_duplicate_domain(
        official_domain,
        organizations_dir
    )

    # 6. Generate unique organization ID.

    organization_id = (
        f"KCG-ORG-{uuid4().hex[:12].upper()}"
    )

    # 7. Create organization profile.

    generated_at = datetime.now(
        timezone.utc
    ).isoformat()

    profile = {

        "organization_id": organization_id,

        "organization_name": organization_name,

        "organization_type": organization_type,

        "contact_email": contact_email,

        "official_domain": official_domain,

        "brand_information": {

            "english_name": brand_name,

            "khmer_name": khmer_brand_name,

            "brand_keywords": cleaned_keywords,

            "logo_file": None
        },

        "verification": {

            "status": "PENDING_VERIFICATION",

            "domain_verified": False,

            "email_verified": False,

            "admin_approved": False
        },

        "created_at_utc": generated_at
    }

    # 8. Save profile without overwriting existing files.

    profile_path = (
        organizations_dir
        / f"{organization_id}.json"
    )

    with profile_path.open(
        "x",
        encoding="utf-8"
    ) as file:

        json.dump(
            profile,
            file,
            indent=4,
            ensure_ascii=False
        )

    return profile