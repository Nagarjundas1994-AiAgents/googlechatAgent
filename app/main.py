from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional, List, Dict, Any
import os
import uvicorn
from dotenv import load_dotenv
import logging

# Import custom modules
from app.api.document_processor import process_document
from app.api.url_crawler import crawl_url
from app.api.vector_store import add_to_vector_store, query_vector_store
from app.api.llm_service import generate_answer

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Document QA Chatbot",
    description="An AI-powered chatbot for document and web content Q&A",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Store conversation history in memory (in production, use a database)
conversation_store = {}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload-document")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    session_id: str = Form(...)
):
    """Upload and process a document"""
    try:
        # Save the file temporarily
        file_location = f"temp_{file.filename}"
        with open(file_location, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        # Process the document in the background
        background_tasks.add_task(
            process_and_store_document,
            file_location,
            file.filename,
            session_id
        )
        
        return JSONResponse(
            content={
                "message": f"Document {file.filename} uploaded and being processed",
                "status": "processing"
            }
        )
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/crawl-url")
async def process_url(
    background_tasks: BackgroundTasks,
    url: str = Form(...),
    max_depth: int = Form(3),
    session_id: str = Form(...)
):
    """Crawl a URL and process its content"""
    try:
        # Crawl the URL in the background
        background_tasks.add_task(
            crawl_and_store_url,
            url,
            max_depth,
            session_id
        )
        
        return JSONResponse(
            content={
                "message": f"URL {url} is being crawled and processed",
                "status": "processing"
            }
        )
    except Exception as e:
        logger.error(f"Error processing URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(
    question: str = Form(...),
    session_id: str = Form(...)
):
    """Answer a question based on the processed documents"""
    try:
        # Get conversation history
        history = conversation_store.get(session_id, [])
        
        # Query the vector store for relevant context
        context_chunks = await query_vector_store(question, session_id)
        
        # Generate an answer using the LLM
        answer, sources = await generate_answer(question, context_chunks, history)
        
        # Update conversation history
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})
        conversation_store[session_id] = history
        
        return JSONResponse(
            content={
                "answer": answer,
                "sources": sources
            }
        )
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{session_id}")
async def get_processing_status(session_id: str):
    """Get the status of document/URL processing"""
    # This would typically check a database or queue for the status
    # For simplicity, we'll return a mock status
    return JSONResponse(
        content={
            "status": "completed",
            "documents_processed": 1,
            "urls_processed": 0
        }
    )

@app.delete("/clear/{session_id}")
async def clear_session(session_id: str):
    """Clear the conversation history and documents for a session"""
    if session_id in conversation_store:
        del conversation_store[session_id]
    
    # In a real implementation, you would also delete the vectors from the vector store
    # await delete_vectors_for_session(session_id)
    
    return JSONResponse(
        content={
            "message": f"Session {session_id} cleared"
        }
    )

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and monitoring"""
    return JSONResponse(
        content={
            "status": "healthy",
            "version": "1.0.0"
        }
    )

# Background processing functions
async def process_and_store_document(file_path: str, filename: str, session_id: str):
    """Process a document and store its content in the vector database"""
    try:
        # Process the document to extract text
        chunks = await process_document(file_path, filename)
        
        # Add chunks to vector store
        await add_to_vector_store(chunks, session_id, source=filename)
        
        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)
            
        logger.info(f"Document {filename} processed and stored successfully")
    except Exception as e:
        logger.error(f"Error processing document {filename}: {str(e)}")

async def crawl_and_store_url(url: str, max_depth: int, session_id: str):
    """Crawl a URL and store its content in the vector database"""
    try:
        # Crawl the URL to extract text
        chunks = await crawl_url(url, max_depth)
        
        # Add chunks to vector store
        await add_to_vector_store(chunks, session_id, source=url)
        
        logger.info(f"URL {url} crawled and stored successfully")
    except Exception as e:
        logger.error(f"Error crawling URL {url}: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)