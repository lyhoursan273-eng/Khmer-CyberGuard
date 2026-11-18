import json
from pathlib import Path

from bs4 import BeautifulSoup


# =====================================
# PROJECT SETTINGS
# =====================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

WEBSITES_DIR = (
    PROJECT_ROOT
    / "data"
    / "test_cases"
    / "websites"
)


# =====================================
# TEXT CLEANING
# =====================================

def clean_text(element) -> str:
    """Extract readable text from an HTML element."""

    return " ".join(
        element.get_text(" ", strip=True).split()
    )


# =====================================
# WEBSITE HTML ANALYZER
# =====================================

def analyze_html_file(file_path: Path) -> dict:
    """
    Analyze a locally saved HTML file.

    This function does not visit external websites.
    It does not submit forms or collect form values.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"HTML file not found: {file_path}"
        )

    if file_path.suffix.lower() not in {".html", ".htm"}:
        raise ValueError(
            "Only HTML files are supported."
        )

    html_content = file_path.read_text(
        encoding="utf-8",
        errors="replace"
    )

    soup = BeautifulSoup(
        html_content,
        "html.parser"
    )

    # 1. Extract website title
    title_element = soup.find("title")

    title = (
        clean_text(title_element)
        if title_element
        else None
    )

    # 2. Extract metadata
    metadata = []

    for tag in soup.find_all("meta"):

        metadata.append({
            "name": tag.get("name"),
            "property": tag.get("property"),
            "content": tag.get("content")
        })

    # 3. Extract page headings
    headings = []

    for tag in soup.find_all(
        ["h1", "h2", "h3", "h4"]
    ):

        headings.append({
            "tag": tag.name,
            "text": clean_text(tag)
        })

    # 4. Extract paragraphs
    paragraphs = [
        clean_text(tag)
        for tag in soup.find_all("p")
        if clean_text(tag)
    ]

    # 5. Extract navigation and other links
    links = []

    for tag in soup.find_all("a"):

        links.append({
            "text": clean_text(tag),
            "href": tag.get("href")
        })

    # 6. Extract input field information
    # We intentionally do not collect field values.

    input_fields = []

    for tag in soup.find_all("input"):

        input_fields.append({

            "type": tag.get("type", "text"),

            "name": tag.get("name"),

            "placeholder": tag.get("placeholder"),

            "disabled": tag.has_attr("disabled")
        })

    # 7. Count forms and buttons
    form_count = len(
        soup.find_all("form")
    )

    button_count = len(
        soup.find_all("button")
    )

    # 8. Extract complete visible page text
    page_text = (
        clean_text(soup.body)
        if soup.body
        else clean_text(soup)
    )

    # 9. Prepare the analysis result
    result = {

        "file_name": file_path.name,

        "website_title": title,

        "metadata": metadata,

        "headings": headings,

        "paragraphs": paragraphs,

        "links": links,

        "input_fields": input_fields,

        "form_count": form_count,

        "button_count": button_count,

        "page_text": page_text
    }

    return result


# =====================================
# TEST BOTH FICTIONAL WEBSITES
# =====================================

def main():

    test_files = [
        WEBSITES_DIR / "legitimate_bank.html",
        WEBSITES_DIR / "suspicious_bank.html"
    ]

    for file_path in test_files:

        try:

            result = analyze_html_file(file_path)

            print("\n================================")
            print("KCG MODULE 2")
            print("WEBSITE HTML ANALYSIS")
            print("================================")

            print(
                json.dumps(
                    result,
                    indent=4,
                    ensure_ascii=False
                )
            )

        except (FileNotFoundError, ValueError, OSError) as error:

            print("\nKCG Error:", error)


if __name__ == "__main__":
    main()