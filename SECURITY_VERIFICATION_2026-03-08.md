# SECURITY VERIFICATION 2026-03-08

Date: 2026-03-08

## Scope

Artifact Analysis verification for the live Cloud Run image serving Constitutional Guardian `v1.4.6`.

## Verified Image

- Image URI: `gcr.io/helix-ai-deploy/constitutional-guardian@sha256:8abb896eb558ddc978c24af226bcc62d425f6e54f8513773b2ed62cbbe1726c7`
- Cloud Run revision: `constitutional-guardian-00239-2zn`
- Tags observed: `latest`, `manual`

## Verification Result

- Artifact Analysis query time: `2026-03-08T11:05:00Z`
- Result: `clean`
- Vulnerability findings returned: `0`

## Cleared CVEs

- `CVE-2026-23949`
- `CVE-2026-24049`
- `CVE-2025-8869`

## Verification Commands

```powershell
$IMAGE = "gcr.io/helix-ai-deploy/constitutional-guardian@sha256:8abb896eb558ddc978c24af226bcc62d425f6e54f8513773b2ed62cbbe1726c7"

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

- Cloud Run is currently deploying from `gcr.io/helix-ai-deploy/constitutional-guardian`, not from the Artifact Registry `helix-repo` image lineage.
- Security transparency surfaces should be populated with this verification using:
  - `SECURITY_ARTIFACT_ANALYSIS_STATUS=clean`
  - `SECURITY_ARTIFACT_ANALYSIS_TIMESTAMP=2026-03-08T11:05:00Z`
  - `SECURITY_ARTIFACT_IMAGE_URI=gcr.io/helix-ai-deploy/constitutional-guardian@sha256:8abb896eb558ddc978c24af226bcc62d425f6e54f8513773b2ed62cbbe1726c7`
