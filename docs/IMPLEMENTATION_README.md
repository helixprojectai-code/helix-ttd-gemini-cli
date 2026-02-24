# =================================================================
# IDENTITY: IMPLEMENTATION_README.md
# VERSION: v1.0.0 (HELIX-CORE NATIVE)
# ORIGIN: HELIX-CORE-UNIFIED / [HELIX-LEDGER/DOCS]
# NODE: 4 (ONTARIO)
# STATUS: RATIFIED-CANONICAL
# CREATED: 2025-10-01
# MODIFIED: 2026-02-10
# =================================================================

# 📖 HGL v1.2-beta.1 Implementation Guide
**Status:** ✅ Active & Reference | **Objective:** Serve as the primary user guide and reference for developers, DevOps engineers, and release managers working with the HGL v1.2-beta.1 verification infrastructure — covering quick start, architecture overview, tool reference, common workflows, troubleshooting, best practices, and FAQ.

## 🔍 Investigation / Summary
This guide is the central documentation for using and maintaining the HGL verification stack. It provides fast onboarding (Quick Start), architectural context, detailed tool usage, practical workflows, troubleshooting steps, best practices for release/security/key management, and answers to common questions — designed to minimize friction and maximize self-service adoption.

---
## 📝 Document Content

### Table of Contents
1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Tool Reference](#tool-reference)
4. [Common Workflows](#common-workflows)
5. [Troubleshooting](#troubleshooting)
6. [Best Practices](#best-practices)
7. [FAQ](#faq)

### Quick Start

#### For Users (Verifying Releases)
**Linux/macOS:**
```bash
# Download release
wget https://github.com/helixprojectai/HGL/releases/download/v1.2-beta.1/HGL-v1.2-beta.1.tar.gz
# Extract
tar -xzf HGL-v1.2-beta.1.tar.gz
cd HGL-v1.2-beta.1
# Verify
./tools/verify_and_eval.sh .
```

**Windows:**
```powershell
# Download release (use browser or curl)
# Extract to C:\HGL-v1.2-beta.1
# Verify
cd C:\HGL-v1.2-beta.1
.\tools\verify_and_eval.ps1 .
```

#### For Developers (Creating Releases)
```bash
# 1. Create release directory
mkdir -p releases/HGL-v1.3-beta.1
# 2. Copy artifacts
cp dist/* releases/HGL-v1.3-beta.1/
# 3. Generate provenance
python tools/generate_provenance.py \
  --version 1.3-beta.1 \
  --release-dir releases/HGL-v1.3-beta.1
# 4. Generate and sign hashes
./tools/generate-hashes.sh releases/HGL-v1.3-beta.1 --sign
# 5. Commit (pre-commit hook will verify)
git add releases/HGL-v1.3-beta.1
git commit -m "Release: HGL v1.3-beta.1"
git push origin main
```

### Architecture Overview

#### Component Hierarchy
```
HGL Release Infrastructure
├── Verification Layer
│ ├── verify_and_eval.sh (Bash)
│ └── verify_and_eval.ps1 (PowerShell)
│
├── CI/CD Layer
│ ├── verify_provenance.yml
│ ├── verify_signatures.yml
│ ├── verify_policy.yml
│ └── reproducibility_smoke.yml
│
├── Tooling Layer
│ ├── generate_provenance.py
│ ├── generate-hashes.sh
│ └── pre-commit-hook
│
├── Security Layer
│ └── allowed_signers
│
└── Documentation Layer
    ├── HGL_GAP_ANALYSIS.md
    ├── IMPLEMENTATION_README.md (this file)
    ├── DEPLOYMENT_CHECKLIST.md
    └── PACKAGE_INDEX.md
```

#### Data Flow
```
Development → Tools → Artifacts → CI/CD → Verification → Release
    ↓ ↓ ↓ ↓ ↓ ↓
  Code Provenance Manifests Tests Signatures Download
          Hashes Signatures Gates Validation Verify
```

### Tool Reference

#### 1. Verification Scripts

##### `verify_and_eval.sh` (Bash)
**Purpose:** Verify HGL releases on Linux/macOS  
**Usage:**
```bash
./verify_and_eval.sh <release_dir> [options]
```
**Options:**
- `--skip-hashes` - Skip SHA256 verification
- `--skip-sig` - Skip signature verification
- `--skip-policy` - Skip policy gate evaluation
- `--verbose` - Show detailed output
- `--help` - Show help message  
**Exit Codes:**
- `0` - All checks passed
- `1` - Hash verification failed
- `2` - Signature verification failed
- `3` - Policy evaluation failed
- `99` - Unexpected error  
**Examples:**
```bash
# Full verification
./verify_and_eval.sh releases/HGL-v1.2-beta.1
# Quick check (skip policy)
./verify_and_eval.sh releases/HGL-v1.2-beta.1 --skip-policy
# Verbose output
./verify_and_eval.sh releases/HGL-v1.2-beta.1 --verbose
```

##### `verify_and_eval.ps1` (PowerShell)
**Purpose:** Verify HGL releases on Windows  
**Usage:**
```powershell
.\verify_and_eval.ps1 -ReleaseDir <path> [options]
```
**Options:**
- `-SkipHashes` - Skip SHA256 verification
- `-SkipSignature` - Skip signature verification
- `-SkipPolicy` - Skip policy gate evaluation
- `-Verbose` - Show detailed output
- `-Help` - Show help message  
**Exit Codes:** Same as Bash version  
**Examples:**
```powershell
# Full verification
.\verify_and_eval.ps1 -ReleaseDir "C:\HGL-v1.2-beta.1"
# Quick check
.\verify_and_eval.ps1 -ReleaseDir "C:\HGL-v1.2-beta.1" -SkipPolicy
# Verbose
.\verify_and_eval.ps1 -ReleaseDir "C:\HGL-v1.2-beta.1" -Verbose
```

#### 2. Provenance Generator

##### `generate_provenance.py`
**Purpose:** Generate provenance.json manifests for releases  
**Dependencies:** Python 3.8+ (standard library only)  
**Usage:**
```bash
python generate_provenance.py \
  --version <version> \
  --release-dir <path> \
  [options]
```
**Required Arguments:**
- `--version` - Release version (e.g., "1.2-beta.1")
- `--release-dir` - Path to release directory  
**Optional Arguments:**
- `--input-dir <path>` - Input source directory
- `--tools-dir <path>` - Tools directory
- `--route <name>` - Processing route (standard/extended/constitutional)
- `--no-policy` - Skip policy evaluation
- `--output <path>` - Output file path
- `--print` - Print to stdout  
**Examples:**
```bash
# Basic usage
python tools/generate_provenance.py \
  --version 1.2-beta.1 \
  --release-dir releases/HGL-v1.2-beta.1
# Custom input directory
python tools/generate_provenance.py \
  --version 1.2-beta.1 \
  --release-dir releases/HGL-v1.2-beta.1 \
  --input-dir src/v1.2
# Skip policy (faster)
python tools/generate_provenance.py \
  --version 1.2-beta.1 \
  --release-dir releases/HGL-v1.2-beta.1 \
  --no-policy
```

#### 3. Hash Generator

##### `generate-hashes.sh`
**Purpose:** Generate SHA256SUMS.txt manifests and sign them  
**Dependencies:** Bash 4.0+, sha256sum/shasum, ssh-keygen  
**Usage:**
```bash
./generate-hashes.sh <release_dir> [options]
```
**Options:**
- `--sign` - Sign the manifest
- `--key <path>` - Custom private key path
- `--no-sort` - Don't sort files
- `--output <file>` - Custom output path  
**Examples:**
```bash
# Unsigned manifest
./tools/generate-hashes.sh releases/HGL-v1.2-beta.1
# Signed manifest
./tools/generate-hashes.sh releases/HGL-v1.2-beta.1 --sign
```

#### 4. Pre-commit Hook

##### `pre-commit-hook`
**Purpose:** Automatically regenerate manifests on commit  
**Installation:**
```bash
cp tools/pre-commit-hook .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```
**Behavior:** Detects release file changes → regenerates SHA256SUMS.txt & provenance.json → stages updates  
**Bypass (emergency):**
```bash
git commit --no-verify
```

### Common Workflows

#### Workflow 1: Creating a New Release
```bash
# 1. Create branch
git checkout -b release/v1.3-beta.1
# 2. Create release directory
mkdir -p releases/HGL-v1.3-beta.1
# 3. Copy artifacts
cp dist/* releases/HGL-v1.3-beta.1/
# 4. Generate provenance
python tools/generate_provenance.py \
  --version 1.3-beta.1 \
  --release-dir releases/HGL-v1.3-beta.1
# 5. Generate and sign hashes
./tools/generate-hashes.sh releases/HGL-v1.3-beta.1 --sign
# 6. Commit (hook auto-verifies)
git add releases/HGL-v1.3-beta.1
git commit -m "Release: HGL v1.3-beta.1"
# 7. Push & create PR
git push origin release/v1.3-beta.1
```

#### Workflow 2: Verifying a Downloaded Release
```bash
# 1. Download & extract
wget https://github.com/.../HGL-v1.2-beta.1.tar.gz
tar -xzf HGL-v1.2-beta.1.tar.gz
cd HGL-v1.2-beta.1
# 2. Verify
./tools/verify_and_eval.sh .
# 3. Check result
if [ $? -eq 0 ]; then echo "✅ Passed"; else echo "❌ Failed"; fi
```

#### Workflow 3: Updating an Existing Release
```bash
# 1. Checkout release directory
cd releases/HGL-v1.2-beta.1
# 2. Make changes...
# 3. Pre-commit hook auto-regenerates manifests
git add .
git commit -m "Update: Fix typo in documentation"
git push origin main
```

#### Workflow 4: Rotating Signing Keys
```bash
# 1. Generate new key
ssh-keygen -t ed25519 -f ~/.ssh/hgl_release_key_2025 \
  -C "release@helixprojectai.com"
# 2. Add new key to allowed_signers
cat >> .github/allowed_signers <<EOF
release@helixprojectai.com namespaces="file" valid-after="20250101" valid-before="20260101" $(cat ~/.ssh/hgl_release_key_2025.pub | cut -d' ' -f1-2)
EOF
# 3. Update old key expiration
# (edit .github/allowed_signers manually)
# 4. Commit & push
git add .github/allowed_signers
git commit -m "Security: Rotate release signing key"
git push origin main
# 5. Use new key for future releases
./tools/generate-hashes.sh releases/HGL-v1.3-beta.1 \
  --sign \
  --key ~/.ssh/hgl_release_key_2025
```

### Troubleshooting

#### Issue: Verification script not executable
**Solution:**
```bash
chmod +x tools/verify_and_eval.sh
chmod +x tools/verify_and_eval.ps1
```

#### Issue: Hash verification fails
**Causes:**
1. File modified after manifest generation
2. Manifest outdated
3. File corruption during download  
**Solution:**
```bash
# Regenerate manifest
./tools/generate-hashes.sh releases/HGL-v1.2-beta.1
# Re-download release
rm -rf HGL-v1.2-beta.1
wget https://github.com/.../HGL-v1.2-beta.1.tar.gz
tar -xzf HGL-v1.2-beta.1.tar.gz
```

#### Issue: Signature verification fails
**Causes:**
1. allowed_signers incorrect/missing
2. Signature file missing/corrupted
3. Manifest modified after signing  
**Solution:**
```bash
# Check allowed_signers
cat .github/allowed_signers
# Regenerate signature
rm /path/to/SHA256SUMS.txt.sig
./tools/generate-hashes.sh /path/to/release --sign
```

#### Issue: Pre-commit hook fails
**Solution:**
```bash
# Check tool permissions
ls -la tools/generate-hashes.sh
chmod +x tools/*.sh tools/*.py
# Test tools manually
./tools/generate-hashes.sh releases/HGL-v1.2-beta.1
# Bypass (emergency only)
git commit --no-verify
```

#### Issue: CI/CD workflow fails
**Solution:**
1. Check GitHub Actions logs
2. Run verification locally
3. Pull latest workflows
4. Manually trigger workflow

### Best Practices

#### 1. Release Management
✅ **DO:**
- Generate provenance for every release
- Sign all hash manifests
- Use semantic versioning
- Tag releases
- Keep release directories self-contained

❌ **DON'T:**
- Modify files after signing
- Reuse version numbers
- Skip verification steps
- Store secrets in repository

#### 2. Key Management
✅ **DO:**
- Rotate keys annually
- Use hardware tokens for production
- Keep private keys secure
- Document key rotation
- Use separate keys per purpose

❌ **DON'T:**
- Share private keys
- Use weak passphrases
- Skip expiration dates
- Store keys in cloud storage

#### 3. CI/CD
✅ **DO:**
- Run full verification on every PR
- Use workflow dispatch for manual testing
- Monitor failures
- Keep workflows current
- Test locally before pushing

❌ **DON'T:**
- Disable required checks
- Merge without CI passing
- Ignore test failures
- Modify workflows without testing

#### 4. Documentation
✅ **DO:**
- Keep docs in sync with code
- Document breaking changes
- Provide examples
- Update changelog
- Link to issues

❌ **DON'T:**
- Leave outdated docs
- Skip example updates
- Forget to version docs
- Hide known limitations

### FAQ

**Q: Do I need to install anything to verify releases?**  
**A:** No — basic verification uses built-in tools only (bash/sha256sum/ssh-keygen on Linux/macOS; PowerShell on Windows).

**Q: Can I verify releases offline?**  
**A:** Yes — if you have the release package, allowed_signers file, and verification scripts. All crypto operations work offline.

**Q: How long do signatures remain valid?**  
**A:** Signatures never expire, but signing keys have validity periods in allowed_signers (default: 1 year).

**Q: Can I use my own signing keys?**  
**A:** Yes — generate an ED25519 key and add it to allowed_signers.

**Q: What if I find a security issue?**  
**A:** Email: security@helixprojectai.com (PGP key available on website).

**Q: How do I contribute?**  
**A:**
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit PR
5. CI/CD will verify

**Q: Can I use this for my own project?**  
**A:** Yes — Apache-2.0 licensed. See LICENSE file.

### Support
- **Documentation:** [https://github.com/helixprojectai/HGL/tree/main/docs](https://github.com/helixprojectai/HGL/tree/main/docs)
- **Issues:** [https://github.com/helixprojectai/HGL/issues](https://github.com/helixprojectai/HGL/issues)
- **Discussions:** [https://github.com/helixprojectai/HGL/discussions](https://github.com/helixprojectai/HGL/discussions)
- **Email:** support@helixprojectai.com

**Last Updated:** October 2025  
**Version:** 1.0

---
## 📖 Glyph Reference
| Glyph | Code          | Meaning              | Use-Case                              |
|-------|---------------|----------------------|---------------------------------------|
| 📖    | HGL-CORE-047  | Guide / Reference    | Implementation guide header           |
| 🔍    | HGL-CORE-001  | Investigate          | Summary & architecture overview       |
| ✅    | HGL-CORE-007  | Validate             | Quick start & tool examples           |
| ⚖️    | HGL-CORE-011  | Ethics/Principle     | Best practices & FAQ                  |

## 🏷️ Tags
[Implementation-Guide, HGL-v1.2-beta.1, Quick-Start, Architecture-Overview, Tool-Reference, Common-Workflows, Troubleshooting, Best-Practices, FAQ]

## 🔗 Related Documents
- HGL_GAP_ANALYSIS.md
- DEPLOYMENT_CHECKLIST.md
- PACKAGE_INDEX.md
- SERVER_OPERATIONS_GUIDE.md
- best_helix_practices.md

# =================================================================
# FOOTER: ID: HELIX-HGL-IMPLEMENTATION-README | READY FOR PRODUCTION.
# =================================================================