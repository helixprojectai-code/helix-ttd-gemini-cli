# SECURITY VERIFICATION 2026-03-09

Date: 2026-03-09

## Scope

Artifact Analysis verification for the live Cloud Run image serving Constitutional Guardian `v1.4.8`.

## Verified Image

- Image URI: `us-central1-docker.pkg.dev/helix-ai-deploy/helix-repo/constitutional-guardian@sha256:8220583ac2b69df727847d12f75d9dfcda2c26be3874e1ac4e56862699fc872b`
- Cloud Run revision: `constitutional-guardian-00367-4lj`
- Tags observed: commit-tagged Artifact Registry image plus `latest`

## Verification Result

- Artifact Analysis query time: `2026-03-09T19:22:26Z`
- Result: `clean`
- Vulnerability findings returned: `0`

## Verification Commands

```powershell
$IMAGE = "us-central1-docker.pkg.dev/helix-ai-deploy/helix-repo/constitutional-guardian@sha256:8220583ac2b69df727847d12f75d9dfcda2c26be3874e1ac4e56862699fc872b"

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

- Production monitoring and the incident board both report against this digest.
- Runtime transparency metadata was promoted with:
  - `SECURITY_ARTIFACT_ANALYSIS_STATUS=clean`
  - `SECURITY_ARTIFACT_ANALYSIS_TIMESTAMP=2026-03-09T19:22:26Z`
  - `SECURITY_ARTIFACT_IMAGE_URI=us-central1-docker.pkg.dev/helix-ai-deploy/helix-repo/constitutional-guardian@sha256:8220583ac2b69df727847d12f75d9dfcda2c26be3874e1ac4e56862699fc872b`
