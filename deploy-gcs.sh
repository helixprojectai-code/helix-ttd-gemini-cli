#!/bin/bash
# [FACT] Deployment script for Constitutional Guardian to Google Cloud Run
# [HYPOTHESIS] Infrastructure-as-code improves reproducibility
# [ASSUMPTION] gcloud CLI is authenticated and project is set

set -e

echo "=== HELIX-TTD CONSTITUTIONAL GUARDIAN DEPLOYMENT ==="
echo "[FACT] Target: Google Cloud Run"
echo "[FACT] Region: us-central1"
echo ""

# [FACT] Configuration
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="constitutional-guardian"
REGION="us-central1"
IMAGE_TAG="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

echo "[INFO] Project: ${PROJECT_ID}"
echo "[INFO] Service: ${SERVICE_NAME}"
echo ""

# [FACT] Verify prerequisites
echo "=== VERIFYING PREREQUISITES ==="
if ! gcloud projects describe "$PROJECT_ID" &>/dev/null; then
    echo "[ERROR] Project ${PROJECT_ID} not found or not accessible"
    exit 1
fi

echo "[PASS] Project verified"

# [FACT] Enable required APIs
echo ""
echo "=== ENABLING GOOGLE CLOUD APIS ==="
gcloud services enable run.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable speech.googleapis.com --quiet
gcloud services enable aiplatform.googleapis.com --quiet
gcloud services enable pubsub.googleapis.com --quiet
gcloud services enable storage.googleapis.com --quiet

echo "[PASS] APIs enabled"

# [FACT] Build and push container
echo ""
echo "=== BUILDING CONTAINER ==="
gcloud builds submit --tag "${IMAGE_TAG}" --timeout=20m

echo "[PASS] Container built: ${IMAGE_TAG}"

# [FACT] Deploy to Cloud Run
echo ""
echo "=== DEPLOYING TO CLOUD RUN ==="
gcloud run deploy "${SERVICE_NAME}" \
    --image "${IMAGE_TAG}" \
    --region "${REGION}" \
    --platform managed \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 2 \
    --concurrency 100 \
    --max-instances 10 \
    --set-env-vars "HELIX_NODE_ID=GCS-GUARDIAN,HELIX_ENV=production" \
    --quiet

# [FACT] Get service URL
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
    --region "${REGION}" \
    --format 'value(status.url)')

echo ""
echo "=== DEPLOYMENT COMPLETE ==="
echo "[FACT] Service URL: ${SERVICE_URL}"
echo "[FACT] Health Check: ${SERVICE_URL}/health"
echo ""
echo "[INFO] To view logs:"
echo "  gcloud logging tail \"resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME}\""
echo ""
echo "🦉⚓🦉 The Constitutional Guardian is watching."
