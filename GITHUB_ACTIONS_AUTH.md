# GitHub Actions Authentication with Google Cloud

*Authentication methods for automated Cloud Run deployment*

---

## Overview

GitHub Actions needs permission to deploy to YOUR Google Cloud project. There are 2 ways to set this up:

| Method | Security | Complexity | Best For |
|--------|----------|------------|----------|
| **Workload Identity Federation** | ⭐⭐⭐ Excellent | Medium | Production, long-term |
| **Service Account Key** | ⭐⭐ Good | Simple | Hackathons, quick demos |

---

## Method 1: Workload Identity Federation (RECOMMENDED)

### How It Works
Instead of storing a password (key), GitHub proves its identity to GCP using OIDC tokens. No long-lived secrets stored in GitHub.

```
GitHub Actions → OIDC Token → GCP Identity Pool → Short-lived Access Token → Deploy to Cloud Run
```

### Setup Steps

#### Step 1: Create Workload Identity Pool (One-time)
```bash
# Run in your terminal with gcloud

export PROJECT_ID="helix-constitutional-guardian"
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

# Enable required APIs
gcloud services enable iamcredentials.googleapis.com --project=$PROJECT_ID

# Create Workload Identity Pool
gcloud iam workload-identity-pools create "github-pool" \
  --project=$PROJECT_ID \
  --location="global" \
  --display-name="GitHub Actions Pool"

# Create Provider for GitHub
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --project=$PROJECT_ID \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"
```

#### Step 2: Create Service Account
```bash
# Create service account for GitHub Actions
gcloud iam service-accounts create "github-deployer" \
  --project=$PROJECT_ID \
  --display-name="GitHub Actions Deployer"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Allow GitHub to impersonate this service account
gcloud iam service-accounts add-iam-policy-binding \
  "github-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --project=$PROJECT_ID \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/helixprojectai-code/helix-ttd-gemini-cli"
```

#### Step 3: Add GitHub Secret (One value only)
```bash
# Get the Workload Identity Provider resource name
export WORKLOAD_IDENTITY_PROVIDER="projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider"

echo "WORKLOAD_IDENTITY_PROVIDER: $WORKLOAD_IDENTITY_PROVIDER"
```

Go to GitHub → Settings → Secrets → Actions → New repository secret:
- **Name:** `WORKLOAD_IDENTITY_PROVIDER`
- **Value:** Paste the output from above

Also add:
- **Name:** `GCP_PROJECT_ID`
- **Value:** `helix-constitutional-guardian`

#### Step 4: GitHub Actions Workflow
```yaml
# .github/workflows/deploy-gcp.yml
name: Deploy to Cloud Run

on:
  push:
    branches: [ main ]

permissions:
  contents: read
  id-token: write  # Required for Workload Identity

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    # Authenticate to GCP using Workload Identity
    - id: auth
      uses: google-github-actions/auth@v2
      with:
        workload_identity_provider: ${{ secrets.WORKLOAD_IDENTITY_PROVIDER }}
        service_account: github-deployer@helix-constitutional-guardian.iam.gserviceaccount.com

    # Deploy to Cloud Run
    - name: Deploy
      uses: google-github-actions/deploy-cloudrun@v2
      with:
        service: constitutional-guardian
        region: us-central1
        source: .
```

---

## Method 2: Service Account Key (FASTER FOR HACKATHON)

### How It Works
Create a JSON key file, encode it, paste into GitHub Secrets. Less secure but much faster to set up.

### Setup Steps

#### Step 1: Create Service Account & Key
```bash
export PROJECT_ID="helix-constitutional-guardian"

# Create service account
gcloud iam service-accounts create "github-deployer" \
  --project=$PROJECT_ID \
  --display-name="GitHub Actions Deployer"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Create and download key
gcloud iam service-accounts keys create key.json \
  --iam-account=github-deployer@$PROJECT_ID.iam.gserviceaccount.com \
  --project=$PROJECT_ID

# Encode key for GitHub
cat key.json | base64

# DELETE the key file after copying
cat key.json | base64 | clip  # Windows
# cat key.json | base64 | pbcopy  # Mac
# cat key.json | base64 -w0 | xclip -selection clipboard  # Linux

rm key.json
```

#### Step 2: Add GitHub Secret
Go to GitHub → Settings → Secrets → Actions → New repository secret:
- **Name:** `GCP_SA_KEY`
- **Value:** Paste the base64-encoded key

#### Step 3: GitHub Actions Workflow
```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    # Authenticate using Service Account Key
    - name: Setup GCP Auth
      uses: google-github-actions/auth@v2
      with:
        credentials_json: ${{ secrets.GCP_SA_KEY }}

    # Setup Cloud SDK
    - name: Setup Cloud SDK
      uses: google-github-actions/setup-gcloud@v2

    # Build and deploy
    - name: Build and Deploy
      run: |
        gcloud builds submit --tag gcr.io/${{ secrets.GCP_PROJECT_ID }}/constitutional-guardian:$GITHUB_SHA
        gcloud run deploy constitutional-guardian \
          --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/constitutional-guardian:$GITHUB_SHA \
          --region us-central1 \
          --platform managed \
          --allow-unauthenticated \
          --memory 1Gi \
          --cpu 2 \
          --port 8180 \
          --set-env-vars "HELIX_NODE_ID=GCS-GUARDIAN,HELIX_ENV=production"
```

---

## Quick Comparison

| Feature | Workload Identity | Service Account Key |
|---------|-------------------|---------------------|
| Setup time | 15 minutes | 5 minutes |
| Security | No stored secrets | Key stored in GitHub |
| Key rotation | Automatic | Manual |
| Best for | Production systems | Hackathons, demos |
| GitHub secrets needed | 2 (short strings) | 1 (long base64) |

---

## Recommendation for Hackathon

**Use Method 2 (Service Account Key)** for fastest setup.

**Delete the key after March 14** when the hackathon ends.

---

## Verification

After setup, push any commit to main:
```bash
git commit --allow-empty -m "[FACT] Trigger deployment"
git push origin main
```

Watch deployment at:
- GitHub: Actions tab → Deploy to Cloud Run
- GCP: Cloud Build → History
- GCP: Cloud Run → constitutional-guardian

---

*For Gemini Live Agent Challenge deployment*
