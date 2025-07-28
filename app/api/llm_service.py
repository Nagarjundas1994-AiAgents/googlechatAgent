import os
import logging
from typing import List, Dict, Any, Tuple
import json
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from google.oauth2 import service_account

load_dotenv()

logger = logging.getLogger(__name__)

# Get configuration from environment variables
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash-002")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")
GCP_SERVICE_ACCOUNT_FILE = os.getenv("GCP_SERVICE_ACCOUNT_FILE")

# Initialize Vertex AI
def initialize_vertex_ai():
    """Initialize Vertex AI client"""
    try:
        if GCP_SERVICE_ACCOUNT_FILE and os.path.exists(GCP_SERVICE_ACCOUNT_FILE):
            credentials = service_account.Credentials.from_service_account_file(
                GCP_SERVICE_ACCOUNT_FILE
            )
            vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION, credentials=credentials)
        else:
            # Use default credentials (for Cloud Run)
            vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)
        logger.info(f"Vertex AI initialized with project: {GCP_PROJECT_ID}, location: {GCP_LOCATION}")
    except Exception as e:
        logger.error(f"Failed to initialize Vertex AI: {str(e)}")
        raise

# Initialize Vertex AI
initialize_vertex_ai()

async def generate_answer(
    question: str,
    context_chunks: List[Dict[str, Any]],
    conversation_history: List[Dict[str, str]]
) -> Tuple[str, List[Dict[str, Any]]]:
    """Generate an answer to a question based on context chunks
    
    Args:
        question: The question to answer
        context_chunks: List of relevant text chunks with metadata
        conversation_history: Previous conversation history
        
    Returns:
        Tuple of (answer, sources)
    """
    try:
        # Prepare the context text
        context_text = "\n\n---\n\n".join([chunk["text"] for chunk in context_chunks])
        
        # Prepare the sources
        sources = []
        for chunk in context_chunks:
            source = {
                "text": chunk["text"][:200] + "...",  # Truncate for display
                "source": chunk["metadata"].get("source", "Unknown"),
                "page": chunk["metadata"].get("page", None),
                "title": chunk["metadata"].get("title", None)
            }
            sources.append(source)
        
        # Prepare the system message
        system_message = f"""
        You are a helpful AI assistant that answers questions based on the provided context.
        If the answer is not in the context, say "I don't have enough information to answer this question."
        Do not make up information that is not in the context.
        Always cite your sources by referring to the document or URL where the information came from.
        
        Context information is below:
        {context_text}
        """
        
        # Prepare the messages
        messages = [
            {"role": "system", "content": system_message}
        ]
        
        # Add conversation history (limited to last 5 exchanges)
        for message in conversation_history[-10:]:
            messages.append(message)
        
        # Add the current question
        messages.append({"role": "user", "content": question})
        
        # Generate the answer using Gemini 2.5 Flash
        return await generate_with_gemini(messages, sources)
    except Exception as e:
        logger.error(f"Error generating answer: {str(e)}")
        raise

async def generate_with_gemini(messages: List[Dict[str, str]], sources: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
    """Generate an answer using Google's Gemini 2.5 Flash"""
    try:
        # Initialize the Gemini model
        model = GenerativeModel(LLM_MODEL)
        
        # Prepare the conversation history
        conversation_text = ""
        system_prompt = ""
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                system_prompt = content
            elif role == "user":
                conversation_text += f"User: {content}\n"
            elif role == "assistant":
                conversation_text += f"Assistant: {content}\n"
        
        # Combine system prompt with conversation
        full_prompt = f"{system_prompt}\n\nConversation:\n{conversation_text}\nAssistant:"
        
        # Generate the response
        response = model.generate_content(
            full_prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 2048,
                "top_p": 0.95,
                "top_k": 40
            }
        )
        
        answer = response.text
        return answer, sources
    except Exception as e:
        logger.error(f"Error generating with Gemini: {str(e)}")
        raise