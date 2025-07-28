# Production Deployment Checklist

## Pre-Deployment Setup

### ✅ 1. Environment Configuration
- [ ] Copy `.env.example` to `.env`
- [ ] Set `GCP_PROJECT_ID` to your Google Cloud project ID
- [ ] Set `GCP_LOCATION` (default: `us-central1`)
- [ ] Verify `LLM_MODEL=gemini-2.5-flash-002`
- [ ] Verify `EMBEDDING_MODEL=text-embedding-004`
- [ ] Set `VECTOR_DB_TYPE=vertex_ai`
- [ ] Set `VECTOR_INDEX_NAME=ai-agent-vector-index`
- [ ] Set `VECTOR_INDEX_ENDPOINT_NAME=ai-agent-vector-endpoint`

### ✅ 2. Google Cloud Setup
- [ ] Create or select a Google Cloud project
- [ ] Enable billing for the project
- [ ] Install Google Cloud SDK locally
- [ ] Authenticate: `gcloud auth login`
- [ ] Set project: `gcloud config set project YOUR_PROJECT_ID`

### ✅ 3. Local Prerequisites
- [ ] Docker installed and running
- [ ] Python 3.9+ installed
- [ ] Git repository cloned locally

## Deployment Steps

### ✅ 4. Run Deployment Script

**For Linux/Mac:**
```bash
chmod +x deploy-gcp-prod.sh
./deploy-gcp-prod.sh
```

**For Windows:**
```powershell
.\deploy-gcp-prod.ps1
```

### ✅ 5. Verify Deployment
- [ ] Deployment script completed without errors
- [ ] Cloud Run service is running
- [ ] Health check endpoint responds: `https://your-service-url/health`
- [ ] Web interface loads: `https://your-service-url`

### ✅ 6. Vector Search Setup
- [ ] Run vector search setup: `python setup-vector-search.py`
- [ ] Verify index is created in Vertex AI console
- [ ] Verify endpoint is created and index is deployed
- [ ] Test document upload and processing

## Google Agent Builder Integration

### ✅ 7. Create Agent
- [ ] Go to Google Cloud Console > Agent Builder
- [ ] Create new Chat agent
- [ ] Set agent name: "AI Document Assistant"
- [ ] Configure default language

### ✅ 8. Configure Webhook
- [ ] Add webhook URL: `https://your-service-url/webhook`
- [ ] Set method to POST
- [ ] Add header: `Content-Type: application/json`
- [ ] Enable webhook for Default Welcome Intent
- [ ] Enable webhook for Default Fallback Intent

### ✅ 9. Create Custom Intents

**Document Upload Intent:**
- [ ] Training phrases: "upload document", "add file", "how to upload"
- [ ] Response: Direct users to web interface

**Document Question Intent:**
- [ ] Training phrases: "what does document say", "find information", "tell me about"
- [ ] Enable webhook fulfillment
- [ ] Test with sample questions

**URL Crawling Intent:**
- [ ] Training phrases: "crawl website", "add web content", "analyze URL"
- [ ] Response: Direct users to URL crawling feature

### ✅ 10. Configure Agent Responses
- [ ] Set welcome message with instructions
- [ ] Configure fallback responses
- [ ] Add suggestion chips for common actions
- [ ] Test conversation flow

## Testing and Validation

### ✅ 11. Functional Testing
- [ ] Upload test document via web interface
- [ ] Verify document processing completes
- [ ] Test questions about uploaded document
- [ ] Test URL crawling functionality
- [ ] Verify webhook responses in Agent Builder

### ✅ 12. Agent Builder Testing
- [ ] Test welcome intent
- [ ] Test document questions via agent
- [ ] Verify webhook integration works
- [ ] Test fallback responses
- [ ] Check conversation history

### ✅ 13. Performance Testing
- [ ] Test with large documents (>10MB)
- [ ] Test concurrent users
- [ ] Monitor Cloud Run metrics
- [ ] Check response times
- [ ] Verify auto-scaling works

## Production Configuration

### ✅ 14. Security Setup
- [ ] Verify service account permissions
- [ ] Check IAM roles are minimal
- [ ] Enable audit logging
- [ ] Configure HTTPS enforcement
- [ ] Set up rate limiting if needed

### ✅ 15. Monitoring Setup
- [ ] Configure Cloud Run monitoring
- [ ] Set up log aggregation
- [ ] Create alerting policies
- [ ] Monitor Vertex AI usage
- [ ] Set up cost alerts

### ✅ 16. Backup and Recovery
- [ ] Document configuration settings
- [ ] Export agent configuration
- [ ] Set up automated backups
- [ ] Test disaster recovery procedures

## Post-Deployment

### ✅ 17. Documentation
- [ ] Update deployment documentation
- [ ] Document API endpoints
- [ ] Create user guides
- [ ] Document troubleshooting steps

### ✅ 18. User Training
- [ ] Train users on document upload
- [ ] Explain supported file formats
- [ ] Show how to ask effective questions
- [ ] Demonstrate URL crawling features

### ✅ 19. Optimization
- [ ] Monitor usage patterns
- [ ] Optimize chunk sizes if needed
- [ ] Tune vector search parameters
- [ ] Adjust Cloud Run resources based on usage

## Troubleshooting Commands

### Check Deployment Status
```bash
# Check Cloud Run service
gcloud run services describe ai-agent --region=us-central1

# View logs
gcloud logs tail ai-agent --region=us-central1

# Check service account
gcloud iam service-accounts describe ai-agent-sa@PROJECT_ID.iam.gserviceaccount.com
```

### Test Endpoints
```bash
# Health check
curl https://ai-agent-nzhkpa3xwa-uc.a.run.app/health

# Test webhook
curl -X POST https://ai-agent-nzhkpa3xwa-uc.a.run.app/webhook \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "sessionInfo": {"session": "test"}}'

# Test document upload
curl -X POST https://ai-agent-nzhkpa3xwa-uc.a.run.app/upload-document \
  -F "file=@test.pdf" \
  -F "session_id=test123"
```

### Monitor Resources
```bash
# Check Vector Search
gcloud ai indexes list --region=us-central1

# Check endpoints
gcloud ai index-endpoints list --region=us-central1

# Monitor costs
gcloud billing budgets list
```

## Success Criteria

### ✅ Deployment Success
- [ ] All services running without errors
- [ ] Health checks passing
- [ ] Web interface accessible
- [ ] Document processing working
- [ ] Vector search operational

### ✅ Agent Integration Success
- [ ] Webhook responding correctly
- [ ] Agent answering questions accurately
- [ ] Conversation flow working
- [ ] Source citations included
- [ ] Error handling graceful

### ✅ Production Readiness
- [ ] Performance meets requirements
- [ ] Security measures in place
- [ ] Monitoring configured
- [ ] Documentation complete
- [ ] Users trained

## Rollback Plan

If deployment fails:

1. **Immediate Actions:**
   - [ ] Check Cloud Run logs for errors
   - [ ] Verify environment variables
   - [ ] Test health endpoint

2. **Rollback Steps:**
   - [ ] Revert to previous Cloud Run revision
   - [ ] Check Vector Search configuration
   - [ ] Verify service account permissions

3. **Recovery Actions:**
   - [ ] Fix identified issues
   - [ ] Re-run deployment script
   - [ ] Re-test all functionality

## Contact Information

- **Cloud Run Issues:** Check Google Cloud Console > Cloud Run
- **Vector Search Issues:** Check Vertex AI > Vector Search
- **Agent Builder Issues:** Check Agent Builder console
- **Billing Issues:** Check Google Cloud Billing

---

**Deployment Date:** ___________
**Deployed By:** ___________
**Service URL:** https://ai-agent-nzhkpa3xwa-uc.a.run.app/
**Agent ID:** ___________