# GCP-Based AI Chatbot Agent - Project Architecture

## Overview

This project is a comprehensive AI-powered document analysis and question-answering system built with FastAPI, designed for deployment on Google Cloud Platform. The system can ingest documents (PDF, DOCX, TXT, HTML) and web content, store them in vector databases, and provide intelligent responses to user queries using Large Language Models.

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │   FastAPI App   │    │  Vector Store   │
│  (HTML/JS/CSS)  │◄──►│   (Backend)     │◄──►│ (Vertex AI/     │
│                 │    │                 │    │  Pinecone/      │
└─────────────────┘    └─────────────────┘    │  Weaviate)      │
                                │              └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   LLM Service   │
                       │ (OpenAI/Gemini) │
                       └─────────────────┘
```

## Directory Structure

```
ai-agent/
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application entry point
│   ├── api/                     # API services and business logic
│   │   ├── __init__.py
│   │   ├── document_processor.py # Document parsing and chunking
│   │   ├── url_crawler.py       # Web crawling functionality
│   │   ├── vector_store.py      # Vector database operations
│   │   └── llm_service.py       # LLM integration for Q&A
│   ├── utils/                   # Utility functions
│   │   ├── __init__.py
│   │   └── helpers.py           # Helper functions and utilities
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── base.html           # Base template with common layout
│   │   └── index.html          # Main application interface
│   └── static/                  # Static assets
│       ├── css/                # Stylesheets
│       │   ├── custom.css
│       │   └── styles.css
│       └── js/                 # JavaScript files
│           ├── app.js
│           └── main.js
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── test_helpers.py         # Unit tests for helper functions
│   └── test_app.py             # Integration tests for the app
├── metadata/                    # Document metadata storage
├── venv/                       # Python virtual environment
├── .env                        # Environment variables (not in repo)
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── .dockerignore              # Docker ignore rules
├── Dockerfile                 # Docker container configuration
├── docker-compose.yml         # Docker Compose configuration
├── requirements.txt           # Python dependencies
├── deploy.sh                  # Linux/Mac deployment script
├── deploy.ps1                 # Windows deployment script
├── run.sh                     # Linux/Mac run script
├── run.ps1                    # Windows run script
├── README.md                  # Project documentation
└── CONTRIBUTING.md            # Contribution guidelines
```

## Core Components

### 1. FastAPI Application (`app/main.py`)

**Purpose**: Main application entry point and API endpoint definitions

**Key Features**:
- RESTful API endpoints for document upload, URL crawling, and Q&A
- Background task processing for document ingestion
- Session management for user interactions
- Health check endpoint for monitoring

**Main Endpoints**:
- `GET /` - Main web interface
- `POST /upload-document` - Document upload and processing
- `POST /crawl-url` - URL crawling and content extraction
- `POST /ask` - Question answering
- `GET /status/{session_id}` - Processing status check
- `DELETE /clear/{session_id}` - Session cleanup
- `GET /health` - Health check

### 2. Document Processing Service (`app/api/document_processor.py`)

**Purpose**: Extract and chunk text content from various document formats

**Supported Formats**:
- PDF files (using PyMuPDF and pdfminer as fallback)
- Word documents (.docx)
- Plain text files (.txt)
- HTML files (.html, .htm)

**Key Features**:
- Intelligent text chunking with configurable size and overlap
- Metadata extraction (page numbers, titles, etc.)
- Error handling and fallback mechanisms
- Memory-efficient processing for large documents

**Configuration**:
- `CHUNK_SIZE`: 1000 tokens per chunk
- `CHUNK_OVERLAP`: 200 tokens overlap between chunks

### 3. URL Crawler Service (`app/api/url_crawler.py`)

**Purpose**: Extract content from web pages and follow links

**Key Features**:
- Depth-limited crawling to prevent infinite loops
- Domain restriction to stay within the same website
- Content extraction using trafilatura and BeautifulSoup
- Rate limiting and error handling
- Page title extraction and metadata preservation

**Configuration**:
- `MAX_CRAWL_DEPTH`: Maximum crawling depth (default: 3)
- `MAX_PAGES_PER_DOMAIN`: Maximum pages per domain (default: 50)

### 4. Vector Store Service (`app/api/vector_store.py`)

**Purpose**: Manage vector embeddings and similarity search

**Supported Vector Databases**:
- **Vertex AI Vector Search** (recommended for GCP)
- **Pinecone** (cloud-based vector database)
- **Weaviate** (open-source vector database)

**Key Features**:
- Embedding generation using OpenAI or Google models
- Vector storage with metadata
- Similarity search with session filtering
- Configurable embedding models

**Embedding Models**:
- OpenAI: `text-embedding-ada-002`
- Google: `models/embedding-001`

### 5. LLM Service (`app/api/llm_service.py`)

**Purpose**: Generate intelligent responses using Large Language Models

**Supported Models**:
- **OpenAI**: GPT-3.5-turbo, GPT-4
- **Google Gemini**: gemini-pro

**Key Features**:
- Context-aware response generation
- Source citation and attribution
- Conversation history management
- Temperature and token limit controls
- Fallback mechanisms for different providers

### 6. Utility Functions (`app/utils/helpers.py`)

**Purpose**: Common utility functions used across the application

**Key Functions**:
- Unique ID generation
- Filename sanitization
- File type validation
- URL validation
- Text truncation
- Metadata management
- Source formatting for display

### 7. Frontend Interface (`app/templates/` & `app/static/`)

**Purpose**: Web-based user interface for document upload and chat

**Key Features**:
- Responsive Bootstrap-based design
- Tabbed interface for document upload and URL crawling
- Real-time chat interface with message history
- File upload with drag-and-drop support
- Processing status indicators
- Source citation display
- Session management

**Technologies**:
- HTML5 with Jinja2 templating
- Bootstrap 5 for responsive design
- Vanilla JavaScript for interactivity
- Animate.css for animations
- Bootstrap Icons for UI elements

## Data Flow

### Document Processing Flow

1. **Upload/Crawl**: User uploads document or provides URL
2. **Processing**: Background task extracts and chunks content
3. **Embedding**: Text chunks converted to vector embeddings
4. **Storage**: Embeddings stored in vector database with metadata
5. **Status**: User notified of completion

### Question Answering Flow

1. **Query**: User submits question
2. **Embedding**: Question converted to vector embedding
3. **Search**: Similar chunks retrieved from vector database
4. **Context**: Relevant chunks assembled as context
5. **Generation**: LLM generates answer based on context
6. **Response**: Answer returned with source citations

## Configuration Management

### Environment Variables

The application uses environment variables for configuration:

```bash
# API Keys
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key

# GCP Configuration
GCP_PROJECT_ID=your_gcp_project_id
GCP_LOCATION=us-central1
GCP_SERVICE_ACCOUNT_FILE=path_to_service_account_json

# Vector Database
VECTOR_DB_TYPE=vertex_ai|pinecone|weaviate
VECTOR_INDEX_NAME=your_index_name

# Models
EMBEDDING_MODEL=text-embedding-ada-002
LLM_MODEL=gpt-3.5-turbo

# Crawler Settings
MAX_CRAWL_DEPTH=3
MAX_PAGES_PER_DOMAIN=50
```

## Deployment Architecture

### Local Development

```
┌─────────────────┐
│   Developer     │
│   Machine       │
├─────────────────┤
│   Python 3.9+   │
│   Virtual Env   │
│   FastAPI       │
│   Uvicorn       │
└─────────────────┘
```

### Docker Deployment

```
┌─────────────────┐
│   Docker        │
│   Container     │
├─────────────────┤
│   Python 3.11   │
│   FastAPI App   │
│   Port 8000     │
└─────────────────┘
```

### Google Cloud Platform Deployment

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cloud Run     │    │   Artifact      │    │   Vertex AI     │
│   (Container)   │    │   Registry      │    │   Vector Search │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Google        │
                    │   Agent Builder │
                    └─────────────────┘
```

## Security Considerations

### API Security
- Environment variable management for sensitive data
- Input validation and sanitization
- File type restrictions for uploads
- URL validation for crawling
- Session isolation for multi-user support

### Data Privacy
- Temporary file cleanup after processing
- Session-based data isolation
- Configurable data retention policies
- Secure credential management

### Infrastructure Security
- GCP IAM roles and permissions
- Service account key management
- Network security groups
- HTTPS enforcement

## Performance Considerations

### Scalability
- Background task processing for long-running operations
- Chunked document processing for memory efficiency
- Configurable crawling limits
- Vector database optimization

### Caching
- Embedding caching to reduce API calls
- Session-based conversation history
- Metadata caching for quick access

### Resource Management
- Memory-efficient document processing
- Configurable chunk sizes
- Connection pooling for external services
- Graceful error handling and retries

## Testing Strategy

### Unit Tests (`tests/test_helpers.py`)
- Helper function validation
- File processing utilities
- Metadata management
- Input validation

### Integration Tests (`test_app.py`)
- API endpoint testing
- End-to-end workflow validation
- Health check verification
- Session management testing

### Test Coverage
- Document processing pipelines
- Vector store operations
- LLM service integration
- Error handling scenarios

## Monitoring and Observability

### Health Checks
- Application health endpoint
- Database connectivity checks
- External service availability
- Resource utilization monitoring

### Logging
- Structured logging with different levels
- Request/response logging
- Error tracking and alerting
- Performance metrics

### Metrics
- Document processing times
- Query response times
- Vector database performance
- LLM API usage and costs

## Future Enhancements

### Planned Features
- Multi-language document support
- Advanced document parsing (tables, images)
- Real-time collaboration features
- Advanced analytics and reporting
- Mobile application support

### Technical Improvements
- Kubernetes deployment support
- Advanced caching strategies
- Microservices architecture
- GraphQL API support
- Streaming responses for large documents

## Dependencies

### Core Dependencies
- **FastAPI**: Web framework and API development
- **Uvicorn**: ASGI server for FastAPI
- **Jinja2**: Template engine for HTML rendering
- **Python-multipart**: File upload handling

### Document Processing
- **PyMuPDF**: PDF text extraction
- **python-docx**: Word document processing
- **BeautifulSoup4**: HTML parsing
- **trafilatura**: Web content extraction

### AI/ML Dependencies
- **OpenAI**: GPT models and embeddings
- **google-cloud-aiplatform**: Google Vertex AI integration
- **pinecone-client**: Pinecone vector database
- **weaviate-client**: Weaviate vector database

### Utility Dependencies
- **requests**: HTTP client for web crawling
- **python-dotenv**: Environment variable management
- **pydantic**: Data validation and serialization
- **tqdm**: Progress bars for long operations

This architecture provides a robust, scalable foundation for an AI-powered document analysis and question-answering system, with flexibility for different deployment scenarios and vector database backends.