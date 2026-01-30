#!/bin/bash

# Configuration
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
REPO_NAME="video-processor-repo"
IMAGE_NAME="video-processor"
JOB_NAME="video-processor-job"

echo "🚀 Starting Deployment to Google Cloud Project: $PROJECT_ID"

# 1. Enable required services
echo "🔌 Enabling required APIs..."
gcloud services enable artifactregistry.googleapis.com run.googleapis.com secretmanager.googleapis.com cloudbuild.googleapis.com

# 2. Grant permissions (fix for PERMISSION_DENIED)
echo "🔑 Granting permissions..."
CURRENT_USER=$(gcloud config get-value account)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$CURRENT_USER" \
    --role="roles/cloudbuild.builds.editor" > /dev/null
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$CURRENT_USER" \
    --role="roles/storage.admin" > /dev/null
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$CURRENT_USER" \
    --role="roles/artifactregistry.admin" > /dev/null
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$CURRENT_USER" \
    --role="roles/run.admin" > /dev/null

# 3. Create Artifact Registry Repository (if not exists)
echo "📦 Checking Artifact Registry..."
if ! gcloud artifacts repositories describe $REPO_NAME --location=$REGION &>/dev/null; then
    echo "   Creating repository $REPO_NAME..."
    gcloud artifacts repositories create $REPO_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="Docker repository for Video Processor"
else
    echo "   Repository $REPO_NAME already exists."
fi

# 4. Build and Push Image using Cloud Build
echo "🔨 Building and Pushing Docker image..."
gcloud builds submit --region=$REGION --tag "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:latest" .

# 5. Create/Update Cloud Run Job
echo "🏃 Deploying Cloud Run Job..."
# Note: We are deploying with 2GB memory and 1 CPU as a start.
# Adjust --max-retries and --task-timeout as needed.
gcloud run jobs deploy $JOB_NAME \
    --image "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:latest" \
    --region $REGION \
    --memory 2Gi \
    --task-timeout 3600s \
    --max-retries 0

echo "✅ Deployment Complete!"
echo "To run the job manually: gcloud run jobs execute $JOB_NAME --region $REGION"
echo "Next steps: Configure Secrets and Cloud Scheduler."
