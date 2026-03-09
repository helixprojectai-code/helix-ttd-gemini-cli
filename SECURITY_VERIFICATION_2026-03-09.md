# SECURITY VERIFICATION 2026-03-09

Date: 2026-03-09

## Scope

Artifact Analysis verification for the live Cloud Run image serving Constitutional Guardian `v1.4.7`.

## Verified Image

- Image URI: `us-central1-docker.pkg.dev/helix-ai-deploy/helix-repo/constitutional-guardian@sha256:4a15dfd5bfd19798d1096f2278256acecd5128592c2406e13ab1a1742a6cf247`
- Cloud Run revision: `constitutional-guardian-00323-fn5`
- Tags observed: commit-tagged Artifact Registry image plus `latest`

## Verification Result

- Artifact Analysis query time: `2026-03-09T10:38:09Z`
- Result: `clean`
- Vulnerability findings returned: `0`

## Verification Commands

```powershell
$IMAGE = "us-central1-docker.pkg.dev/helix-ai-deploy/helix-repo/constitutional-guardian@sha256:4a15dfd5bfd19798d1096f2278256acecd5128592c2406e13ab1a1742a6cf247"

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

- Production monitoring now runs as a Cloud Run Job and reports `overall_status=pass` against this digest.
- Runtime transparency metadata was promoted with:
  - `SECURITY_ARTIFACT_ANALYSIS_STATUS=clean`
  - `SECURITY_ARTIFACT_ANALYSIS_TIMESTAMP=2026-03-09T10:38:09Z`
  - `SECURITY_ARTIFACT_IMAGE_URI=us-central1-docker.pkg.dev/helix-ai-deploy/helix-repo/constitutional-guardian@sha256:4a15dfd5bfd19798d1096f2278256acecd5128592c2406e13ab1a1742a6cf247`
