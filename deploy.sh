#!/bin/bash

# Deployment script for GCP-Based AI Chatbot Agent

# Load environment variables
set -a
source .env
set +a

# Check if GCP_PROJECT_ID is set
if [ -z "$GCP_PROJECT_ID" ]; then
    echo "Error: GCP_PROJECT_ID is not set in .env file"
    exit 1
fi

# Build Docker image
echo "Building Docker image..."
docker build -t gcr.io/$GCP_PROJECT_ID/ai-agent:latest .

# Configure Docker to use Google Cloud
echo "Configuring Docker for Google Cloud..."
gcloud auth configure-docker

# Push image to Google Artifact Registry
echo "Pushing image to Google Artifact Registry..."
docker push gcr.io/$GCP_PROJECT_ID/ai-agent:latest

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy ai-agent \
  --image gcr.io/$GCP_PROJECT_ID/ai-agent:latest \
  --platform managed \
  --region ${GCP_LOCATION:-us-central1} \
  --allow-unauthenticated \
  --memory 2Gi \
  --port 8000

echo "Deployment completed!"
echo "Your application should be available at the URL provided above."
echo "Next steps:"
echo "1. Set up Google Agent Builder and connect it to your Cloud Run endpoint"
echo "2. Configure the agent with appropriate intents and webhook"
echo "3. Test the agent with your documents and queries"