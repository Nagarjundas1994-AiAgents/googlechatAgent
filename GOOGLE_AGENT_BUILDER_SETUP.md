# Google Agent Builder Setup Guide

This guide will walk you through deploying your AI Document QA Chatbot to Google Cloud Platform and integrating it with Google Agent Builder.

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud SDK** installed locally
3. **Docker** installed locally
4. **Python 3.9+** installed locally

## Step 1: Prepare Your Environment

1. **Clone and setup the project**:
   ```bash
   git clone <your-repo-url>
   cd ai-agent
   ```

2. **Create your environment file**:
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` file** with your configuration:
   ```bash
   # GCP Configuration
   GCP_PROJECT_ID=your-gcp-project-id
   GCP_LOCATION=us-central1
   
   # Vector Database Configuration
   VECTOR_DB_TYPE=vertex_ai
   VECTOR_INDEX_NAME=ai-agent-vector-index
   VECTOR_INDEX_ENDPOINT_NAME=ai-agent-vector-endpoint
   
   # Application Settings - Using Google Gemini 2.5 Flash
   EMBEDDING_MODEL=text-embedding-004
   LLM_MODEL=gemini-2.5-flash-002
   
   # Crawler Settings
   MAX_CRAWL_DEPTH=3
   MAX_PAGES_PER_DOMAIN=50
   
   # Application Settings
   DEBUG=False
   ```

## Step 2: Deploy to Google Cloud Platform

1. **Run the deployment script**:
   ```bash
   chmod +x deploy-gcp-prod.sh
   ./deploy-gcp-prod.sh
   ```

   This script will:
   - Enable required Google Cloud APIs
   - Create Artifact Registry repository
   - Build and push Docker image
   - Create service account with proper permissions
   - Set up Vertex AI Vector Search (basic setup)
   - Deploy to Cloud Run

2. **Note the Cloud Run URL** from the deployment output (e.g., `https://ai-agent-xxx-uc.a.run.app`)

## Step 3: Complete Vector Search Setup

1. **Go to Google Cloud Console** > Vertex AI > Vector Search

2. **Create a Vector Search Index** (if not created automatically):
   - Name: `ai-agent-vector-index`
   - Dimensions: `768` (for text-embedding-004)
   - Distance measure: `DOT_PRODUCT_DISTANCE`
   - Algorithm: `TREE_AH`

3. **Create an Index Endpoint**:
   - Name: `ai-agent-vector-endpoint`
   - Region: `us-central1` (or your chosen region)

4. **Deploy the index to the endpoint**:
   - Select your index
   - Deploy to the endpoint you created
   - Set minimum replica count to 1

## Step 4: Set Up Google Agent Builder

### 4.1 Create a New Agent

1. **Go to Google Cloud Console** > Agent Builder

2. **Click "Create Agent"**

3. **Choose "Chat" as the agent type**

4. **Configure basic settings**:
   - Agent name: `AI Document Assistant`
   - Description: `An AI assistant that can answer questions about uploaded documents`
   - Default language: `English`

### 4.2 Configure Webhook Integration

1. **In your agent settings**, go to **"Webhooks"**

2. **Add a new webhook**:
   - Name: `Document QA Webhook`
   - URL: `https://your-cloud-run-url/webhook`
   - Method: `POST`
   - Headers: `Content-Type: application/json`

3. **Enable webhook** for the Default Welcome Intent and Default Fallback Intent

### 4.3 Create Custom Intents

1. **Create "Document Upload" Intent**:
   - Training phrases:
     - "I want to upload a document"
     - "Can I add a new file?"
     - "How do I upload documents?"
   - Response: "You can upload documents by visiting our web interface at [your-cloud-run-url]. Supported formats include PDF, DOCX, TXT, and HTML files."

2. **Create "Document Question" Intent**:
   - Training phrases:
     - "What does the document say about..."
     - "Can you find information about..."
     - "Tell me about..."
     - "Explain..."
   - Enable webhook for this intent
   - Set webhook as fulfillment

3. **Create "URL Crawling" Intent**:
   - Training phrases:
     - "Can you crawl a website?"
     - "I want to add content from a URL"
     - "How do I add web content?"
   - Response: "You can add web content by using the URL crawling feature at [your-cloud-run-url]. Just provide the URL and set the crawl depth."

### 4.4 Configure Agent Responses

1. **Default Welcome Intent**:
   ```
   Hello! I'm your AI Document Assistant. I can help you:
   
   📄 Answer questions about your uploaded documents
   🌐 Analyze content from websites you provide
   🔍 Find specific information across your document collection
   
   To get started, upload documents or crawl URLs at [your-cloud-run-url], then ask me any questions!
   ```

2. **Default Fallback Intent**:
   ```
   I'm not sure I understand. I can help you with questions about your documents. 
   
   Try asking:
   - "What does the document say about [topic]?"
   - "Can you summarize [document name]?"
   - "Find information about [specific topic]"
   
   If you need to upload new documents, visit [your-cloud-run-url]
   ```

## Step 5: Test Your Agent

### 5.1 Upload Test Documents

1. **Visit your Cloud Run URL** in a browser
2. **Upload a test document** (PDF, DOCX, etc.)
3. **Wait for processing** to complete

### 5.2 Test in Agent Builder

1. **Go to the "Test" tab** in Agent Builder
2. **Try these test queries**:
   - "Hello" (should trigger welcome intent)
   - "What does the document say about [topic from your uploaded document]?"
   - "Can you summarize the main points?"
   - "How do I upload more documents?"

### 5.3 Test the Webhook Integration

1. **Check Cloud Run logs**:
   ```bash
   gcloud logs tail ai-agent --region=us-central1
   ```

2. **Verify webhook calls** are being received and processed

## Step 6: Advanced Configuration

### 6.1 Enable Rich Responses

In Agent Builder, you can configure rich responses:

1. **Add suggestion chips** for common questions
2. **Configure cards** for document summaries
3. **Add quick replies** for follow-up questions

### 6.2 Set Up Analytics

1. **Enable Dialogflow Analytics** in your agent settings
2. **Set up BigQuery export** for detailed analytics
3. **Configure custom metrics** for document processing

### 6.3 Production Optimizations

1. **Scale Cloud Run**:
   ```bash
   gcloud run services update ai-agent \
     --region=us-central1 \
     --memory=8Gi \
     --cpu=4 \
     --max-instances=50 \
     --concurrency=100
   ```

2. **Set up monitoring**:
   - Cloud Run metrics
   - Vertex AI usage metrics
   - Custom application metrics

3. **Configure caching** for frequently accessed documents

## Step 7: Integration Options

### 7.1 Web Integration

Add the agent to your website:
```html
<script src="https://www.gstatic.com/dialogflow-console/fast/messenger/bootstrap.js?v=1"></script>
<df-messenger
  intent="WELCOME"
  chat-title="AI Document Assistant"
  agent-id="your-agent-id"
  language-code="en">
</df-messenger>
```

### 7.2 Mobile Integration

Use the Dialogflow SDK for mobile apps:
- Android: Dialogflow Android SDK
- iOS: Dialogflow iOS SDK

### 7.3 API Integration

Direct API calls to your Cloud Run service:
```bash
curl -X POST "https://your-cloud-run-url/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What does the document say about AI?",
    "session_id": "user123"
  }'
```

## Troubleshooting

### Common Issues

1. **Webhook not responding**:
   - Check Cloud Run logs
   - Verify webhook URL is correct
   - Ensure service account has proper permissions

2. **Vector Search not working**:
   - Verify index is deployed to endpoint
   - Check index dimensions match embedding model
   - Ensure proper IAM permissions

3. **Document processing fails**:
   - Check file format is supported
   - Verify sufficient memory allocation
   - Check Cloud Run timeout settings

### Monitoring Commands

```bash
# Check Cloud Run status
gcloud run services describe ai-agent --region=us-central1

# View logs
gcloud logs tail ai-agent --region=us-central1

# Check service account permissions
gcloud projects get-iam-policy your-project-id

# Test webhook directly
curl -X POST "https://your-cloud-run-url/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello",
    "sessionInfo": {"session": "test-session"}
  }'
```

## Cost Optimization

1. **Set up budget alerts** in Google Cloud Console
2. **Monitor Vertex AI usage** (embeddings and LLM calls)
3. **Configure Cloud Run** with appropriate resource limits
4. **Use caching** to reduce API calls
5. **Set up auto-scaling** based on usage patterns

## Security Best Practices

1. **Use IAM roles** with least privilege principle
2. **Enable audit logging** for all services
3. **Set up VPC** for network isolation (optional)
4. **Use Secret Manager** for sensitive configuration
5. **Enable HTTPS** for all endpoints
6. **Implement rate limiting** to prevent abuse

Your AI Document Assistant is now ready for production use with Google Agent Builder integration!