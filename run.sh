#!/bin/bash
# Bash script to run the Google Chat Agent locally

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed or not in PATH. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "Found $PYTHON_VERSION"

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists, create from example if not
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "Creating .env file from .env.example..."
        cp .env.example .env
        echo "Please edit the .env file with your API keys and configuration."
    else
        echo "Warning: .env.example file not found. Please create a .env file manually."
    fi
fi

# Create metadata directory if it doesn't exist
if [ ! -d "metadata" ]; then
    echo "Creating metadata directory..."
    mkdir -p metadata
fi

# Run the application
echo "Starting the application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload