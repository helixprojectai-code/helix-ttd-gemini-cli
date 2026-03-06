# Release Notes v1.4.0 — "Lattice"

**Release Date:** March 6, 2026  
**PyPI:** https://pypi.org/project/helix-ttd-gemini/1.4.0/  
**Install:** `pip install helix-ttd-gemini`

---

## 🎯 Overview

The "Lattice" release marks the first **PyPI distribution** of the Helix-TTD Gemini Node — a constitutional AI governance implementation for the Gemini Live API.

---

## ✨ New Features

### PyPI Distribution
- **Package:** `helix-ttd-gemini` now available on PyPI
- **Install:** `pip install helix-ttd-gemini`
- **Trusted Publishing:** Uses OIDC for secure, tokenless authentication

### Constitutional Framework
- **4 Immutable Invariants:** Epistemic Integrity, Non-Agency, Custodial Sovereignty, Predictive Humility
- **Drift Detection:** Real-time constitutional compliance validation
- **Cryptographic Receipts:** Non-repudiable audit trails with DBC signatures

### Federation Support
- **3-Node Federation:** KIMI, GEMS, DEEPSEEK nodes operational
- **Cross-Node Verification:** Quorum attestation (2-of-3)
- **Receipt Migration:** v1.0.0 → v1.1.0 schema

### Cloud Deployment
- **Google Cloud Run:** Live deployment `constitutional-guardian-b25t5w6zva-uc.a.run.app`
- **Docker Support:** Production-ready containerization
- **GCS Credits:** $2,000 unlocked (Google for Startups)

---

## 📊 Statistics

| Metric | Value |
|--------|-------|
| **Tests Passing** | 140/140 (100%) |
| **Coverage** | 79.5% |
| **Git Clones (14 days)** | 3,571 |
| **Unique Cloners** | 471 |
| **Cloud Credits Remaining** | ~$1,970 |

---

## 🔧 Installation

```bash
# Install from PyPI
pip install helix-ttd-gemini

# Verify installation
python -c "import helix_code; print(helix_code.__version__)"
# Output: 1.4.0
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│  helix-ttd-gemini (PyPI Package)        │
├─────────────────────────────────────────┤
│  helix_code/                            │
│  ├── gemini_text_client.py    (6.9 KB)  │
│  ├── gemini_live_bridge.py    (9.9 KB)  │
│  ├── constitutional_compliance.py       │
│  ├── drift_telemetry.py                 │
│  └── ...                                │
│  helix_ttd_claw/                        │
│  └── audit/identity_signer.py           │
└─────────────────────────────────────────┘
```

---

## 🚀 Quick Start

```python
from helix_code.gemini_text_client import GeminiTextClient
from helix_code.constitutional_compliance import ConstitutionalCompliance

# Initialize client
client = GeminiTextClient(api_key="your-key")

# Check availability
assert client.is_available(), "API key required"

# Generate constitutional response
result = await client.generate_response(
    "What is the sky's color?",
    system_instruction="Always use [FACT], [HYPOTHESIS], or [ASSUMPTION] labels."
)

# Validate compliance
guardian = ConstitutionalCompliance()
validation = client.validate_constitutional_response(result["text"], guardian)
```

---

## 📝 Changelog

### Added
- PyPI distribution via Trusted Publishing (OIDC)
- GitHub Actions release workflow (`.github/workflows/release.yml`)
- Package markers (`__init__.py` files)
- Version metadata in `helix_code.__version__`
- CI badges in README

### Changed
- Package name: `helix-ttd` → `helix-ttd-gemini`
- Version alignment: `1.0.0` → `1.4.0`
- Entry point fix: `helix_code.helix_cli:main`

### Fixed
- Environment-dependent tests with `monkeypatch`
- Missing `model` field in `/api/gemini-status` endpoint
- Package discovery for setuptools

---

## 🔐 Security

- **Trusted Publishing:** OIDC-based authentication (no long-lived API tokens)
- **DBC Encryption:** Fernet key management via `HELIX_DBC_ENC_KEY`
- **Non-root Container:** User `helix` (UID 1000) in Docker

---

## 🙏 Acknowledgments

- **Bob:** B+ arrangement secured for Audit Anchor constitutional oversight
- **Google for Startups:** $2,000 cloud credits
- **Federation Nodes:** KIMI, GEMS, DEEPSEEK operational

---

## 🦉 The Two Owls Are Watching

**⚓ GLORY TO THE LATTICE. ⚓**

---

*For migration guides and breaking changes, see MIGRATION.md*
