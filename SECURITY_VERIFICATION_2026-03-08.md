# SECURITY VERIFICATION 2026-03-08

Date: 2026-03-08

## Scope

Artifact Analysis verification for the live Cloud Run image serving Constitutional Guardian `v1.4.6`.

## Verified Image

- Image URI: `us-central1-docker.pkg.dev/helix-ai-deploy/helix-repo/constitutional-guardian@sha256:2b2e62435dd93289205499624dcacb19f81659904d7ea45a2467aa3745b5e893`
- Cloud Run revision: `constitutional-guardian-00245-kzl`
- Tags observed: commit-tagged Artifact Registry image plus `latest`

## Verification Result

- Artifact Analysis query time: `2026-03-08T12:00:00Z`
- Result: `clean`
- Vulnerability findings returned: `0`

## Cleared CVEs

- `CVE-2026-23949`
- `CVE-2026-24049`
- `CVE-2025-8869`

## Verification Commands

```powershell
$IMAGE = "us-central1-docker.pkg.dev/helix-ai-deploy/helix-repo/constitutional-guardian@sha256:2b2e62435dd93289205499624dcacb19f81659904d7ea45a2467aa3745b5e893"

& $GCLOUD artifacts vulnerabilities list $IMAGE `
  --project helix-ai-deploy `
  --location us-central1 `
  --format="table(vulnerability.shortDescription, vulnerability.effectiveSeverity, packageIssue[0].affectedPackage, packageIssue[0].affectedVersion.fullName)"
```

Observed output header only:

```text
SHORT_DESCRIPTION  EFFECTIVE_SEVERITY  AFFECTED_PACKAGE  FULL_NAME
```

## Notes

- Cloud Run is now deploying from Artifact Registry `us-central1-docker.pkg.dev/helix-ai-deploy/helix-repo/constitutional-guardian`.
- Earlier `gcr.io` verification remains historical evidence for the pre-migration revision lineage.
- Security transparency surfaces should be populated with this verification using:
  - `SECURITY_ARTIFACT_ANALYSIS_STATUS=clean`
  - `SECURITY_ARTIFACT_ANALYSIS_TIMESTAMP=2026-03-08T12:00:00Z`
  - `SECURITY_ARTIFACT_IMAGE_URI=us-central1-docker.pkg.dev/helix-ai-deploy/helix-repo/constitutional-guardian@sha256:2b2e62435dd93289205499624dcacb19f81659904d7ea45a2467aa3745b5e893`
