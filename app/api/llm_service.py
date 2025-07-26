import os
import logging
from typing import List, Dict, Any, Tuple
import json
from dotenv import load_dotenv
import openai
from google.cloud import aiplatform
from google.oauth2 import service_account

load_dotenv()

logger = logging.getLogger(__name__)

# Get configuration from environment variables
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")
GCP_SERVICE_ACCOUNT_FILE = os.getenv("GCP_SERVICE_ACCOUNT_FILE")

# Initialize clients based on configuration
def initialize_clients():
    """Initialize the necessary clients based on configuration"""
    global openai_client, vertex_ai_client
    
    # Initialize OpenAI client
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        openai.api_key = openai_api_key
    
    # Initialize Vertex AI client
    if LLM_MODEL.startswith("gemini"):
        if GCP_SERVICE_ACCOUNT_FILE and os.path.exists(GCP_SERVICE_ACCOUNT_FILE):
            credentials = service_account.Credentials.from_service_account_file(
                GCP_SERVICE_ACCOUNT_FILE
            )
            aiplatform.init(project=GCP_PROJECT_ID, location=GCP_LOCATION, credentials=credentials)
        else:
            aiplatform.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)

# Initialize clients
initialize_clients()

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
        
        # Generate the answer using the appropriate LLM
        if LLM_MODEL.startswith("gpt"):
            return await generate_with_openai(messages, sources)
        elif LLM_MODEL.startswith("gemini"):
            return await generate_with_gemini(messages, sources)
        else:
            raise ValueError(f"Unsupported LLM model: {LLM_MODEL}")
    except Exception as e:
        logger.error(f"Error generating answer: {str(e)}")
        raise

async def generate_with_openai(messages: List[Dict[str, str]], sources: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
    """Generate an answer using OpenAI's API"""
    try:
        response = openai.ChatCompletion.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content
        return answer, sources
    except Exception as e:
        logger.error(f"Error generating with OpenAI: {str(e)}")
        raise

async def generate_with_gemini(messages: List[Dict[str, str]], sources: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
    """Generate an answer using Google's Gemini API"""
    try:
        # Convert messages to Gemini format
        gemini_messages = []
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                # Gemini doesn't have a system role, so we'll add it as a user message
                gemini_messages.append({"role": "user", "parts": [{"text": content}]})
                gemini_messages.append({"role": "model", "parts": [{"text": "I understand. I'll follow these instructions."}]})
            elif role == "user":
                gemini_messages.append({"role": "user", "parts": [{"text": content}]})
            elif role == "assistant":
                gemini_messages.append({"role": "model", "parts": [{"text": content}]})
        
        # Initialize the Gemini model
        model = aiplatform.GenerativeModel(LLM_MODEL)
        
        # Generate the response
        response = model.generate_content(
            gemini_messages,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 1000,
                "top_p": 0.95,
                "top_k": 40
            }
        )
        
        answer = response.text
        return answer, sources
    except Exception as e:
        logger.error(f"Error generating with Gemini: {str(e)}")
        raise