# Production deployment script for GCP-Based AI Chatbot Agent (PowerShell version)

# Load environment variables from .env file
$envFile = ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^([^#][^=]*)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}
else {
    Write-Error "❌ Error: .env file not found. Please create one from .env.example"
    exit 1
}

# Check if GCP_PROJECT_ID is set
if (-not $env:GCP_PROJECT_ID) {
    Write-Error "❌ Error: GCP_PROJECT_ID is not set in .env file"
    exit 1
}

# Set default location if not specified
if (-not $env:GCP_LOCATION) {
    $env:GCP_LOCATION = "us-central1"
}

Write-Host "Starting production deployment to Google Cloud Platform..." -ForegroundColor Green

Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Project ID: $env:GCP_PROJECT_ID" -ForegroundColor White
Write-Host "  Location: $env:GCP_LOCATION" -ForegroundColor White
Write-Host "  LLM Model: $env:LLM_MODEL" -ForegroundColor White
Write-Host "  Embedding Model: $env:EMBEDDING_MODEL" -ForegroundColor White

# Authenticate with Google Cloud
Write-Host "Authenticating with Google Cloud..." -ForegroundColor Green
gcloud auth login
gcloud config set project $env:GCP_PROJECT_ID

# Enable required APIs
Write-Host "Enabling required Google Cloud APIs..." -ForegroundColor Green
gcloud services enable cloudbuild.googleapis.com run.googleapis.com aiplatform.googleapis.com storage.googleapis.com secretmanager.googleapis.com artifactregistry.googleapis.com

# Create Artifact Registry repository
Write-Host "Creating Artifact Registry repository..." -ForegroundColor Green
$repoCreateResult = gcloud artifacts repositories create ai-agent-repo --repository-format=docker --location=$env:GCP_LOCATION --description="AI Agent Docker repository" 2>&1
if ($LASTEXITCODE -ne 0 -and $repoCreateResult -notmatch "already exists") {
    Write-Warning "Repository creation result: $repoCreateResult"
}

# Configure Docker to use Google Cloud
Write-Host "Configuring Docker for Google Cloud..." -ForegroundColor Green
gcloud auth configure-docker "$env:GCP_LOCATION-docker.pkg.dev"

# Build and push Docker image
Write-Host "Building Docker image..." -ForegroundColor Green
$imageUri = "$env:GCP_LOCATION-docker.pkg.dev/$env:GCP_PROJECT_ID/ai-agent-repo/ai-agent:latest"
docker build -t $imageUri .

Write-Host "Pushing image to Artifact Registry..." -ForegroundColor Green
docker push $imageUri

# Create service account for the application
Write-Host "Creating service account..." -ForegroundColor Green
$saCreateResult = gcloud iam service-accounts create ai-agent-sa --display-name="AI Agent Service Account" --description="Service account for AI Agent application" 2>&1
if ($LASTEXITCODE -ne 0 -and $saCreateResult -notmatch "already exists") {
    Write-Warning "Service account creation result: $saCreateResult"
}

# Grant necessary permissions
Write-Host "Granting permissions to service account..." -ForegroundColor Green
gcloud projects add-iam-policy-binding $env:GCP_PROJECT_ID --member="serviceAccount:ai-agent-sa@$env:GCP_PROJECT_ID.iam.gserviceaccount.com" --role="roles/aiplatform.user"
gcloud projects add-iam-policy-binding $env:GCP_PROJECT_ID --member="serviceAccount:ai-agent-sa@$env:GCP_PROJECT_ID.iam.gserviceaccount.com" --role="roles/storage.admin"
gcloud projects add-iam-policy-binding $env:GCP_PROJECT_ID --member="serviceAccount:ai-agent-sa@$env:GCP_PROJECT_ID.iam.gserviceaccount.com" --role="roles/secretmanager.secretAccessor"

# Deploy to Cloud Run
Write-Host "Deploying to Cloud Run..." -ForegroundColor Green
gcloud run deploy ai-agent `
    --image $imageUri `
    --platform managed `
    --region $env:GCP_LOCATION `
    --allow-unauthenticated `
    --service-account "ai-agent-sa@$env:GCP_PROJECT_ID.iam.gserviceaccount.com" `
    --memory 4Gi `
    --cpu 2 `
    --timeout 3600 `
    --concurrency 80 `
    --max-instances 10 `
    --port 8000 `
    --set-env-vars="GCP_PROJECT_ID=$env:GCP_PROJECT_ID,GCP_LOCATION=$env:GCP_LOCATION,VECTOR_DB_TYPE=vertex_ai,EMBEDDING_MODEL=$env:EMBEDDING_MODEL,LLM_MODEL=$env:LLM_MODEL,VECTOR_INDEX_NAME=$env:VECTOR_INDEX_NAME"

# Get the Cloud Run service URL
$serviceUrl = gcloud run services describe ai-agent --region=$env:GCP_LOCATION --format="value(status.url)"

Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Your AI Agent is now deployed at: https://ai-agent-nzhkpa3xwa-uc.a.run.app/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps for Google Agent Builder integration:" -ForegroundColor Yellow
Write-Host "1. Go to Google Cloud Console > Agent Builder" -ForegroundColor White
Write-Host "2. Create a new agent or use existing one" -ForegroundColor White
Write-Host "3. Set up webhook URL: https://ai-agent-nzhkpa3xwa-uc.a.run.app/webhook" -ForegroundColor White
Write-Host "4. Configure intents and training phrases" -ForegroundColor White
Write-Host "5. Test your agent" -ForegroundColor White
Write-Host ""
Write-Host "Additional setup required:" -ForegroundColor Yellow
Write-Host "1. Complete Vector Search index setup if needed" -ForegroundColor White
Write-Host "2. Upload initial documents through the web interface: https://ai-agent-nzhkpa3xwa-uc.a.run.app/" -ForegroundColor White
Write-Host "3. Configure agent intents and responses" -ForegroundColor White
Write-Host ""
Write-Host "Monitor your deployment:" -ForegroundColor Yellow
Write-Host "  - Cloud Run logs: gcloud logs tail ai-agent --region=$env:GCP_LOCATION" -ForegroundColor White
Write-Host "  - Cloud Run metrics: Google Cloud Console > Cloud Run > ai-agent" -ForegroundColor White