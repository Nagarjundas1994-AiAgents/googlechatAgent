# Your AI Document Assistant - Deployed Application Guide

## 🚀 **Your Application is Live!**

**Application URL**: https://ai-agent-nzhkpa3xwa-uc.a.run.app/

## 🎯 **Quick Start Guide**

### **1. Access Your Application**
Visit: https://ai-agent-nzhkpa3xwa-uc.a.run.app/

### **2. Test Document Upload**
1. Click on "Upload Document" tab
2. Select a PDF, DOCX, TXT, or HTML file
3. Click "Process Document"
4. Wait for processing to complete
5. Ask questions about your document

### **3. Test URL Crawling**
1. Click on "Crawl Website" tab
2. Enter a website URL (e.g., https://example.com)
3. Select crawl depth (Level 2 recommended)
4. Click "Start Crawling"
5. Ask questions about the crawled content

## 🤖 **Google Agent Builder Integration**

### **Webhook URL for Agent Builder**
```
https://ai-agent-nzhkpa3xwa-uc.a.run.app/webhook
```

### **Setup Steps**
1. Go to [Google Cloud Console > Agent Builder](https://console.cloud.google.com/agent-builder)
2. Create a new Chat agent
3. Configure webhook:
   - **URL**: `https://ai-agent-nzhkpa3xwa-uc.a.run.app/webhook`
   - **Method**: POST
   - **Headers**: `Content-Type: application/json`
4. Enable webhook for intents
5. Test your agent

### **Sample Agent Intents**

#### **Document Questions Intent**
- **Training Phrases**:
  - "What does the document say about..."
  - "Can you find information about..."
  - "Tell me about..."
  - "Summarize the document"
  - "What are the main points?"

- **Webhook**: ✅ Enabled
- **Response**: Handled by webhook

#### **Upload Instructions Intent**
- **Training Phrases**:
  - "How do I upload a document?"
  - "Can I add a new file?"
  - "I want to upload a document"

- **Response**: 
  ```
  You can upload documents by visiting https://ai-agent-nzhkpa3xwa-uc.a.run.app/
  
  Supported formats:
  • PDF files
  • Word documents (.docx)
  • Text files (.txt)
  • HTML files
  
  Just click "Upload Document" and select your file!
  ```

#### **URL Crawling Intent**
- **Training Phrases**:
  - "Can you crawl a website?"
  - "I want to add content from a URL"
  - "How do I analyze a website?"

- **Response**:
  ```
  You can crawl websites by visiting https://ai-agent-nzhkpa3xwa-uc.a.run.app/
  
  Steps:
  1. Click "Crawl Website" tab
  2. Enter the website URL
  3. Choose crawl depth (Level 2 recommended)
  4. Click "Start Crawling"
  
  Then ask me questions about the content!
  ```

## 🧪 **Testing Your Application**

### **Health Check**
```bash
curl https://ai-agent-nzhkpa3xwa-uc.a.run.app/health
```

### **Test Webhook**
```bash
curl -X POST https://ai-agent-nzhkpa3xwa-uc.a.run.app/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, can you help me with my documents?",
    "sessionInfo": {"session": "test-session"}
  }'
```

### **Expected Response**
```json
{
  "fulfillmentResponse": {
    "messages": [
      {
        "text": {
          "text": ["I'd be happy to help you with your documents! Please upload a document or crawl a website first, then ask me any questions about the content."]
        }
      }
    ]
  }
}
```

## 📊 **Application Features**

### **✅ What's Working**
- ✅ Document upload and processing (PDF, DOCX, TXT, HTML)
- ✅ Website crawling with configurable depth
- ✅ AI-powered question answering using Gemini 2.5 Flash
- ✅ Vertex AI Vector Search for semantic retrieval
- ✅ Responsive web interface
- ✅ Google Agent Builder webhook integration
- ✅ Session management
- ✅ Source citations

### **🎨 UI Features**
- ✅ Modern, responsive design
- ✅ Mobile-friendly interface
- ✅ Animated chat input with glowing border
- ✅ Drag-and-drop file upload
- ✅ Real-time processing feedback
- ✅ Clean, professional appearance

## 🔧 **Configuration Details**

### **Current Setup**
- **Project ID**: pro-icon-465305-n3
- **Region**: us-central1
- **LLM Model**: gemini-2.5-flash-002
- **Embedding Model**: text-embedding-004
- **Vector Database**: Vertex AI Vector Search
- **Memory**: 4GB
- **CPU**: 2 cores
- **Max Instances**: 10

### **Vector Search Status**
- **Index**: Created ✅
- **Endpoint**: Created ✅
- **Deployment**: Ready for use ✅

## 🎯 **Next Steps**

1. **Test the application** with sample documents
2. **Set up Google Agent Builder** using the webhook URL
3. **Configure agent intents** for your specific use case
4. **Train the agent** with relevant phrases
5. **Deploy to production** agent environment

## 📞 **Support & Monitoring**

### **View Logs**
```bash
gcloud logs tail ai-agent --region=us-central1
```

### **Monitor Performance**
- Google Cloud Console > Cloud Run > ai-agent
- Check metrics, logs, and resource usage

### **Troubleshooting**
If you encounter issues:
1. Check the health endpoint
2. Review Cloud Run logs
3. Verify Vector Search deployment
4. Test webhook integration

---

**🎉 Your AI Document Assistant is ready for production use!**

Visit: https://ai-agent-nzhkpa3xwa-uc.a.run.app/