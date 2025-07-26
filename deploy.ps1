# Deployment script for GCP-Based AI Chatbot Agent (PowerShell version)

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

# Check if GCP_PROJECT_ID is set
if (-not $env:GCP_PROJECT_ID) {
    Write-Error "Error: GCP_PROJECT_ID is not set in .env file"
    exit 1
}

# Set default location if not specified
if (-not $env:GCP_LOCATION) {
    $env:GCP_LOCATION = "us-central1"
}

# Build Docker image
Write-Host "Building Docker image..." -ForegroundColor Green
docker build -t gcr.io/$env:GCP_PROJECT_ID/ai-agent:latest .

# Configure Docker to use Google Cloud
Write-Host "Configuring Docker for Google Cloud..." -ForegroundColor Green
gcloud auth configure-docker

# Push image to Google Artifact Registry
Write-Host "Pushing image to Google Artifact Registry..." -ForegroundColor Green
docker push gcr.io/$env:GCP_PROJECT_ID/ai-agent:latest

# Deploy to Cloud Run
Write-Host "Deploying to Cloud Run..." -ForegroundColor Green
gcloud run deploy ai-agent `
  --image gcr.io/$env:GCP_PROJECT_ID/ai-agent:latest `
  --platform managed `
  --region $env:GCP_LOCATION `
  --allow-unauthenticated `
  --memory 2Gi `
  --port 8000

Write-Host "Deployment completed!" -ForegroundColor Green
Write-Host "Your application should be available at the URL provided above." -ForegroundColor Cyan
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Set up Google Agent Builder and connect it to your Cloud Run endpoint" -ForegroundColor Yellow
Write-Host "2. Configure the agent with appropriate intents and webhook" -ForegroundColor Yellow
Write-Host "3. Test the agent with your documents and queries" -ForegroundColor Yellow