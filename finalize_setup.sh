#!/bin/bash

# Configuration
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
REGION="us-central1"
JOB_NAME="video-processor-job"
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

echo "🔐 Configuring Secrets and Scheduler for Project: $PROJECT_ID"
echo "   Service Account: $SERVICE_ACCOUNT"

# List of secrets to configure
SECRETS=(
    "OPENAI_API_KEY"
    "ANTHROPIC_API_KEY"
    "GOOGLE_SHEET_ID"
    "GOOGLE_DRIVE_FOLDER_ID_UPLOAD"
    "GOOGLE_DRIVE_FOLDER_ID_FINAL"
    "GOOGLE_SERVICE_ACCOUNT_JSON"
)

# 1. Create Secrets and Grant Access & Update Job
SECRET_FLAGS=""

for SECRET_NAME in "${SECRETS[@]}"; do
    # Convert env var name to secret name (lowercase, hyphens)
    SECRET_ID=$(echo "$SECRET_NAME" | tr '_' '-' | tr '[:upper:]' '[:lower:]')
    
    echo ""
    echo "👉 Enter value for $SECRET_NAME (input hidden):"
    read -s SECRET_VALUE
    
    if [ -z "$SECRET_VALUE" ]; then
        echo "   Skipping $SECRET_NAME (empty)..."
        continue
    fi

    # Create secret version or secret if not exists
    echo "   Creating/Updating secret $SECRET_ID..."
    if ! gcloud secrets describe $SECRET_ID &>/dev/null; then
        gcloud secrets create $SECRET_ID --replication-policy="automatic"
    fi
    echo -n "$SECRET_VALUE" | gcloud secrets versions add $SECRET_ID --data-file=-

    # Grant access to Cloud Run Service Account
    echo "   Granting access to Service Account..."
    gcloud secrets add-iam-policy-binding $SECRET_ID \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/secretmanager.secretAccessor" > /dev/null

    # Build flag for Cloud Run update
    SECRET_FLAGS="$SECRET_FLAGS --set-secrets=$SECRET_NAME=$SECRET_ID:latest"
done

# 2. Update Cloud Run Job with Secrets
if [ -n "$SECRET_FLAGS" ]; then
    echo ""
    echo "🔄 Updating Cloud Run Job with secrets..."
    gcloud run jobs update $JOB_NAME --region $REGION $SECRET_FLAGS
else
    echo "⚠️  No secrets provided. Cloud Run Job might fail if it needs them."
fi


# 3. Configure Cloud Scheduler
SCHEDULER_JOB_NAME="video-processor-scheduler"
echo ""
echo "⏰ Configuring Cloud Scheduler ($SCHEDULER_JOB_NAME)..."

# Enable Cloud Scheduler API
gcloud services enable cloudscheduler.googleapis.com

# Create/Update Scheduler Job
# Note: Cloud Run Jobs trigger via API.
# We create a scheduler job that calls the Cloud Run Jobs Run API.
# Requires a service account with run.jobs.run permission. 
# We will use the Compute Engine default SA for simplicity here (or create one).

if gcloud scheduler jobs describe $SCHEDULER_JOB_NAME --location=$REGION &>/dev/null; then
    echo "   Scheduler job exists, updating..."
    gcloud scheduler jobs update http $SCHEDULER_JOB_NAME \
        --location=$REGION \
        --schedule="*/15 * * * *" \
        --uri="https://$REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/$JOB_NAME:run" \
        --http-method=POST \
        --oauth-service-account-email=$SERVICE_ACCOUNT \
        --oauth-token-scope="https://www.googleapis.com/auth/cloud-platform"
else
    echo "   Creating new scheduler job..."
    gcloud scheduler jobs create http $SCHEDULER_JOB_NAME \
        --location=$REGION \
        --schedule="*/15 * * * *" \
        --uri="https://$REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/$JOB_NAME:run" \
        --http-method=POST \
        --oauth-service-account-email=$SERVICE_ACCOUNT \
        --oauth-token-scope="https://www.googleapis.com/auth/cloud-platform"
fi

echo "✅ Configuration Complete!"
echo "   Test your job: gcloud run jobs execute $JOB_NAME --region $REGION"
