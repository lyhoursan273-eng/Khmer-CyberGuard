# Khmer CyberGuard (KCG)
# Khmer CyberGuard (KCG)

## 1. Project Overview

Khmer CyberGuard (KCG) is a cybersecurity project designed to help detect potential phishing websites, domain impersonation and online brand abuse targeting organizations in Cambodia, particularly Microfinance Institutions (MFIs).

The system aims to combine domain similarity detection, website analysis and threat intelligence to identify potential online threats and support investigation.

## 2. Development Progress

### Module 1 – Domain Similarity Detection

**Status: Initial Backend Prototype Completed**

Implemented components:

- **DNSTwist:** Generates possible lookalike domain variations.
- **Levenshtein Distance:** Calculates similarity between official domains and generated candidates.
- **Similarity Ranking:** Ranks candidates according to their text similarity.
- **DNS Enrichment:** Retrieves A, AAAA, MX and NS records.
- **Evidence Collection:** Generates unique evidence IDs and records detection information.
- **Organization Profiles:** Loads organization information from JSON profiles.
- **JSON Reporting:** Saves investigation results and evidence.

### Testing Results

The current Module 1 test suite has successfully passed **27 automated tests** in its latest recorded test run.

Testing covers domain comparison, similarity calculations, DNS enrichment, pipeline integration, evidence collection and organization profile validation.

### Testing Profiles

Two profiles are currently prepared:

1. **Sample Bank:** Fictional organization used for local testing.
2. **ABA Bank:** Public brand reference used for offline domain variation generation and similarity analysis only.

The ABA profile is not affiliated with or authorized by ABA Bank. Candidate DNS lookups and external website scanning remain disabled in this testing mode.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend development |
| DNSTwist | Domain variation generation |
| Levenshtein Algorithm | Domain similarity calculation |
| dnspython | DNS enrichment |
| JSON | Organization profiles and investigation reports |
| Git | Version control |
| GitHub | Source code management |

## 4. Project Structure

```text
KCG-Rebuild/
│
├── backend/
│   ├── main.py
│   ├── common/
│   └── modules/
│       ├── domain_comparison.py
│       ├── domain_pipeline.py
│       ├── dns_enrichment.py
│       ├── dnstwist_runner.py
│       ├── evidence_collector.py
│       └── levenshtein.py
│
├── data/
│   ├── organizations/
│   ├── test_cases/
│   └── threat_intel/
│
├── tests/
│   ├── test_module1.py
│   ├── test_dns_enrichment.py
│   ├── test_domain_pipeline.py
│   ├── test_evidence_collector.py
│   └── test_organization_profile.py
│
├── reports/
├── .gitignore
└── README.md
```

## 5. Upcoming Development

### Module 2 – Website & Phishing Analysis

Planned technologies:

- BeautifulSoup4
- Python Rule-Based Analyzer
- ProjectDiscovery httpx
- Pillow and ImageHash
- Optional urlscan.io integration

### Module 3 – Malicious URL & Threat Intelligence

Planned features:

- Threat intelligence integration
- URL reputation checking
- Threat evidence collection
- Risk assessment

### Frontend Development

The planned frontend will use:

- HTML
- CSS
- JavaScript

FastAPI will connect the frontend with the Python backend.

## 6. Development Roadmap

| Stage | Description | Status |
|---|---|---|
| Module 1 | Domain Similarity Detection | Initial prototype completed |
| Module 2 | Website & Phishing Analysis | Planned |
| Module 3 | Malicious URL Checking | Planned |
| System Integration | Connect all three modules | Planned |
| Frontend | HTML, CSS and JavaScript dashboard | Planned |
| Final Testing | Full system evaluation | Planned |

## 7. Version Control

Repository: Khmer-CyberGuard

Current development branch: `development`

The `main` branch is reserved for stable project versions.