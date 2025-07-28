#!/bin/bash

# Production deployment script for GCP-Based AI Chatbot Agent

set -e

echo "🚀 Starting production deployment to Google Cloud Platform..."

# Load environment variables
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
else
    echo "❌ Error: .env file not found. Please create one from .env.example"
    exit 1
fi

# Check if GCP_PROJECT_ID is set
if [ -z "$GCP_PROJECT_ID" ]; then
    echo "❌ Error: GCP_PROJECT_ID is not set in .env file"
    exit 1
fi

# Set default location if not specified
GCP_LOCATION=${GCP_LOCATION:-us-central1}

echo "📋 Configuration:"
echo "  Project ID: $GCP_PROJECT_ID"
echo "  Location: $GCP_LOCATION"
echo "  LLM Model: $LLM_MODEL"
echo "  Embedding Model: $EMBEDDING_MODEL"

# Authenticate with Google Cloud
echo "🔐 Authenticating with Google Cloud..."
gcloud auth login
gcloud config set project $GCP_PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required Google Cloud APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    aiplatform.googleapis.com \
    storage.googleapis.com \
    secretmanager.googleapis.com \
    artifactregistry.googleapis.com

# Create Artifact Registry repository
echo "📦 Creating Artifact Registry repository..."
gcloud artifacts repositories create ai-agent-repo \
    --repository-format=docker \
    --location=$GCP_LOCATION \
    --description="AI Agent Docker repository" || echo "Repository already exists"

# Configure Docker to use Google Cloud
echo "🐳 Configuring Docker for Google Cloud..."
gcloud auth configure-docker $GCP_LOCATION-docker.pkg.dev

# Build and push Docker image
echo "🏗️ Building Docker image..."
IMAGE_URI="$GCP_LOCATION-docker.pkg.dev/$GCP_PROJECT_ID/ai-agent-repo/ai-agent:latest"
docker build -t $IMAGE_URI .

echo "📤 Pushing image to Artifact Registry..."
docker push $IMAGE_URI

# Create service account for the application
echo "👤 Creating service account..."
gcloud iam service-accounts create ai-agent-sa \
    --display-name="AI Agent Service Account" \
    --description="Service account for AI Agent application" || echo "Service account already exists"

# Grant necessary permissions
echo "🔑 Granting permissions to service account..."
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:ai-agent-sa@$GCP_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:ai-agent-sa@$GCP_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:ai-agent-sa@$GCP_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Create Vector Search index (if it doesn't exist)
echo "🔍 Setting up Vertex AI Vector Search..."
python3 -c "
import os
from google.cloud import aiplatform
from google.oauth2 import service_account

project_id = '$GCP_PROJECT_ID'
location = '$GCP_LOCATION'

try:
    aiplatform.init(project=project_id, location=location)
    
    # Check if index exists
    try:
        indexes = aiplatform.MatchingEngineIndex.list()
        index_exists = any(index.display_name == '$VECTOR_INDEX_NAME' for index in indexes)
        
        if not index_exists:
            print('Creating Vector Search index...')
            index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
                display_name='$VECTOR_INDEX_NAME',
                contents_delta_uri='gs://$GCP_PROJECT_ID-vector-data',
                dimensions=768,  # text-embedding-004 dimensions
                approximate_neighbors_count=150,
                distance_measure_type='DOT_PRODUCT_DISTANCE',
                leaf_node_embedding_count=500,
                leaf_nodes_to_search_percent=7,
            )
            print(f'Index created: {index.resource_name}')
        else:
            print('Vector Search index already exists')
            
    except Exception as e:
        print(f'Note: Vector Search setup will be completed manually: {e}')
        
except Exception as e:
    print(f'Vertex AI initialization failed: {e}')
"

# Deploy to Cloud Run
echo "☁️ Deploying to Cloud Run..."
gcloud run deploy ai-agent \
    --image $IMAGE_URI \
    --platform managed \
    --region $GCP_LOCATION \
    --allow-unauthenticated \
    --service-account ai-agent-sa@$GCP_PROJECT_ID.iam.gserviceaccount.com \
    --memory 4Gi \
    --cpu 2 \
    --timeout 3600 \
    --concurrency 80 \
    --max-instances 10 \
    --port 8000 \
    --set-env-vars="GCP_PROJECT_ID=$GCP_PROJECT_ID,GCP_LOCATION=$GCP_LOCATION,VECTOR_DB_TYPE=vertex_ai,EMBEDDING_MODEL=$EMBEDDING_MODEL,LLM_MODEL=$LLM_MODEL,VECTOR_INDEX_NAME=$VECTOR_INDEX_NAME"

# Get the Cloud Run service URL
SERVICE_URL=$(gcloud run services describe ai-agent --region=$GCP_LOCATION --format="value(status.url)")

echo "✅ Deployment completed successfully!"
echo ""
echo "🌐 Your AI Agent is now deployed at: $SERVICE_URL"
echo ""
echo "📋 Next steps for Google Agent Builder integration:"
echo "1. Go to Google Cloud Console > Agent Builder"
echo "2. Create a new agent or use existing one"
echo "3. Set up webhook URL: $SERVICE_URL/webhook"
echo "4. Configure intents and training phrases"
echo "5. Test your agent"
echo ""
echo "🔧 Additional setup required:"
echo "1. Complete Vector Search index setup if needed"
echo "2. Upload initial documents through the web interface: $SERVICE_URL"
echo "3. Configure agent intents and responses"
echo ""
echo "📊 Monitor your deployment:"
echo "  - Cloud Run logs: gcloud logs tail ai-agent --region=$GCP_LOCATION"
echo "  - Cloud Run metrics: Google Cloud Console > Cloud Run > ai-agent"