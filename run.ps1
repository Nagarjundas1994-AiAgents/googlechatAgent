# PowerShell script to run the Google Chat Agent locally

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Found $pythonVersion"
} catch {
    Write-Host "Python is not installed or not in PATH. Please install Python 3.8 or higher."
    exit 1
}

# Check if virtual environment exists, create if not
if (-not (Test-Path -Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists, create from example if not
if (-not (Test-Path -Path ".env")) {
    if (Test-Path -Path ".env.example") {
        Write-Host "Creating .env file from .env.example..."
        Copy-Item -Path ".env.example" -Destination ".env"
        Write-Host "Please edit the .env file with your API keys and configuration."
    } else {
        Write-Host "Warning: .env.example file not found. Please create a .env file manually."
    }
}

# Create metadata directory if it doesn't exist
if (-not (Test-Path -Path "metadata")) {
    Write-Host "Creating metadata directory..."
    New-Item -Path "metadata" -ItemType Directory
}

# Run the application
Write-Host "Starting the application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload