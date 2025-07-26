# GCP-Based AI Chatbot Agent for Document and Web Content QA

## Overview
This project is an AI-powered chatbot that can process documents (PDF, DOCX, HTML) and web content, store the information in a vector database, and answer natural language queries based on the stored content. It's built with FastAPI, containerized with Docker, and deployed on Google Cloud Platform using Google Agent Builder.

## Features
- **Document Ingestion**: Upload and process PDF, DOCX, TXT, and HTML files
- **URL Crawling**: Extract content from websites by crawling URLs
- **Vector Embedding**: Convert text to embeddings using OpenAI or Google Gemini
- **Semantic Retrieval**: Find relevant information using vector similarity search
- **Question Answering**: Generate answers based on retrieved context using LLMs
- **Web Interface**: Simple chat interface for interacting with the system
- **GCP Integration**: Deployment to Google Cloud Run and integration with Google Agent Builder

## Tech Stack
- **Backend API**: FastAPI
- **Frontend UI**: FastAPI with Jinja2 templates
- **File Parsing**: PyMuPDF, python-docx, BeautifulSoup
- **URL Crawler**: requests, beautifulsoup4, trafilatura
- **Embedding Generator**: OpenAI or Google Gemini
- **Vector DB**: Vertex AI Vector Search, Pinecone, or Weaviate
- **Deployment**: Docker, Google Artifact Registry
- **Hosting & Agent**: Google Cloud Run + Google Agent Builder

## Project Structure
```
ai-agent/
├── app/
│   ├── main.py                # FastAPI application entry point
│   ├── api/                   # API endpoints and services
│   │   ├── document_processor.py  # Document parsing logic
│   │   ├── url_crawler.py     # URL crawling logic
│   │   ├── vector_store.py    # Vector database operations
│   │   └── llm_service.py     # LLM integration for QA
│   ├── utils/                 # Utility functions
│   │   └── helpers.py         # Helper functions
│   ├── templates/             # Jinja2 HTML templates
│   │   ├── base.html          # Base template
│   │   └── index.html         # Main page template
│   └── static/                # Static assets
│       ├── css/               # CSS stylesheets
│       └── js/                # JavaScript files
├── Dockerfile                 # Docker configuration
├── requirements.txt           # Python dependencies
├── .env.example              # Example environment variables
├── deploy.sh                  # Deployment script (Linux/Mac)
├── deploy.ps1                 # Deployment script (Windows)
└── README.md                  # Project documentation
```

## Setup and Installation

### Prerequisites
- Python 3.9+
- Docker
- Google Cloud SDK
- API keys for OpenAI or Google Gemini
- GCP project with necessary APIs enabled

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-agent
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create a .env file**
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file with your API keys and configuration.

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```
   The application will be available at http://localhost:8000

### Docker Development

1. **Build the Docker image**
   ```bash
   docker build -t ai-agent .
   ```

2. **Run the Docker container**
   ```bash
   docker run -p 8000:8000 --env-file .env ai-agent
   ```
   The application will be available at http://localhost:8000

## GCP Setup

### Enable Required APIs

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to "APIs & Services" > "Library"
4. Enable the following APIs:
   - Vertex AI API
   - Artifact Registry API
   - Cloud Run API
   - Secret Manager API
   - Google Agent Builder (Preview/Beta)

### Create Service Account

1. Navigate to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Name the service account (e.g., "ai-agent-sa")
4. Assign the following roles:
   - Storage Admin
   - Vertex AI User
   - Artifact Registry Writer
   - Cloud Run Admin
5. Create and download the JSON key file
6. Add the path to this file in your `.env` file as `GCP_SERVICE_ACCOUNT_FILE`

### Deployment to GCP

1. **Set up environment variables**
   Make sure your `.env` file is properly configured with your GCP project ID and other settings.

2. **Run the deployment script**
   - Linux/Mac:
     ```bash
     chmod +x deploy.sh
     ./deploy.sh
     ```
   - Windows:
     ```powershell
     .\deploy.ps1
     ```

3. **Set up Google Agent Builder**
   - Go to the [Google Agent Builder](https://console.cloud.google.com/agent-builder)
   - Create a new agent
   - Add your Cloud Run endpoint as a webhook
   - Define intents and slots as needed
   - Enable session memory and dynamic document context

## Usage

### Uploading Documents

1. Navigate to the application
2. Click on the "Upload Document" tab
3. Select a document (PDF, DOCX, TXT, HTML) and upload it
4. Wait for the processing to complete

### Crawling URLs

1. Navigate to the application
2. Click on the "Crawl URL" tab
3. Enter a URL and set the maximum crawl depth
4. Click "Crawl" and wait for the processing to complete

### Asking Questions

1. Navigate to the "Chat" tab
2. Type your question in the input field
3. Press Enter or click the send button
4. View the answer and the sources used to generate it

## Configuration Options

### Vector Database Options

The application supports three vector database options:

1. **Vertex AI Vector Search** (recommended for GCP deployment)
   ```
   VECTOR_DB_TYPE=vertex_ai
   VECTOR_INDEX_NAME=your_vector_index_name
   ```

2. **Pinecone**
   ```
   VECTOR_DB_TYPE=pinecone
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_ENVIRONMENT=your_pinecone_environment
   PINECONE_INDEX_NAME=your_pinecone_index_name
   ```

3. **Weaviate**
   ```
   VECTOR_DB_TYPE=weaviate
   WEAVIATE_URL=your_weaviate_url
   WEAVIATE_API_KEY=your_weaviate_api_key
   ```

### Embedding and LLM Options

The application supports both OpenAI and Google Gemini models:

1. **OpenAI**
   ```
   OPENAI_API_KEY=your_openai_api_key
   EMBEDDING_MODEL=text-embedding-ada-002
   LLM_MODEL=gpt-3.5-turbo
   ```

2. **Google Gemini**
   ```
   GOOGLE_API_KEY=your_google_api_key
   EMBEDDING_MODEL=models/embedding-001
   LLM_MODEL=gemini-pro
   ```

## Extending the Application

### Adding New Document Types

To add support for a new document type:

1. Add a new function in `app/api/document_processor.py`
2. Update the `process_document` function to handle the new file extension
3. Add the new extension to the `is_valid_file_type` function in `app/utils/helpers.py`

### Customizing the UI

The UI is built with Bootstrap and can be customized by:

1. Modifying the HTML templates in `app/templates/`
2. Updating the CSS in `app/static/css/styles.css`
3. Extending the JavaScript functionality in `app/static/js/app.js`

## Troubleshooting

### Common Issues

1. **API Key Issues**
   - Ensure your API keys are correctly set in the `.env` file
   - Check that the service account has the necessary permissions

2. **Vector Database Connection**
   - Verify that your vector database is properly configured and accessible
   - Check the logs for connection errors

3. **Document Processing Errors**
   - Ensure the document format is supported
   - Check for encoding issues in text files

4. **Deployment Issues**
   - Verify that all required GCP APIs are enabled
   - Check that the service account has the necessary roles
   - Ensure Docker is properly configured for Google Cloud

## License

MIT

## Acknowledgements

- OpenAI for their embedding and LLM APIs
- Google for Vertex AI and Agent Builder
- The FastAPI team for the excellent web framework
- All the open-source libraries used in this project