import os
import logging
from typing import List, Dict, Any, Optional, Tuple
import json
import uuid
from dotenv import load_dotenv
import openai
from google.cloud import aiplatform
from google.oauth2 import service_account

# Try to import optional vector DB clients
try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

try:
    import weaviate
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False

load_dotenv()

logger = logging.getLogger(__name__)

# Get configuration from environment variables
VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "vertex_ai").lower()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")
GCP_SERVICE_ACCOUNT_FILE = os.getenv("GCP_SERVICE_ACCOUNT_FILE")

# Initialize clients based on configuration
def initialize_clients():
    """Initialize the necessary clients based on configuration"""
    global openai_client, vertex_ai_client, pinecone_client, weaviate_client
    
    # Initialize OpenAI client
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        openai.api_key = openai_api_key
    
    # Initialize Vertex AI client if using Vertex AI
    if VECTOR_DB_TYPE == "vertex_ai":
        if GCP_SERVICE_ACCOUNT_FILE and os.path.exists(GCP_SERVICE_ACCOUNT_FILE):
            credentials = service_account.Credentials.from_service_account_file(
                GCP_SERVICE_ACCOUNT_FILE
            )
            aiplatform.init(project=GCP_PROJECT_ID, location=GCP_LOCATION, credentials=credentials)
        else:
            aiplatform.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)
    
    # Initialize Pinecone client if using Pinecone
    if VECTOR_DB_TYPE == "pinecone" and PINECONE_AVAILABLE:
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")
        if pinecone_api_key and pinecone_environment:
            pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)
    
    # Initialize Weaviate client if using Weaviate
    if VECTOR_DB_TYPE == "weaviate" and WEAVIATE_AVAILABLE:
        weaviate_url = os.getenv("WEAVIATE_URL")
        weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
        if weaviate_url:
            auth_config = None
            if weaviate_api_key:
                auth_config = weaviate.auth.AuthApiKey(api_key=weaviate_api_key)
            weaviate_client = weaviate.Client(url=weaviate_url, auth_client_secret=auth_config)

# Initialize clients
initialize_clients()

async def generate_embeddings(text: str) -> List[float]:
    """Generate embeddings for a text using the configured embedding model
    
    Args:
        text: The text to generate embeddings for
        
    Returns:
        A list of floats representing the embedding vector
    """
    try:
        if EMBEDDING_MODEL.startswith("text-embedding"):
            # Using OpenAI embeddings
            response = openai.Embedding.create(
                input=text,
                model=EMBEDDING_MODEL
            )
            return response["data"][0]["embedding"]
        elif EMBEDDING_MODEL.startswith("models/embedding"):
            # Using Google Vertex AI embeddings
            model = aiplatform.TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)
            embeddings = model.get_embeddings([text])
            return embeddings[0].values
        else:
            raise ValueError(f"Unsupported embedding model: {EMBEDDING_MODEL}")
    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        raise

async def add_to_vector_store(chunks: List[Dict[str, Any]], session_id: str, source: str) -> None:
    """Add text chunks to the vector store
    
    Args:
        chunks: List of text chunks with metadata
        session_id: Session ID for grouping related chunks
        source: Source of the chunks (filename or URL)
    """
    try:
        for chunk in chunks:
            # Generate a unique ID for the chunk
            chunk_id = str(uuid.uuid4())
            
            # Add session_id to metadata
            chunk["metadata"]["session_id"] = session_id
            
            # Generate embeddings for the chunk
            embedding = await generate_embeddings(chunk["text"])
            
            # Store in the appropriate vector database
            if VECTOR_DB_TYPE == "vertex_ai":
                await store_in_vertex_ai(chunk_id, chunk["text"], embedding, chunk["metadata"])
            elif VECTOR_DB_TYPE == "pinecone" and PINECONE_AVAILABLE:
                await store_in_pinecone(chunk_id, embedding, chunk["text"], chunk["metadata"])
            elif VECTOR_DB_TYPE == "weaviate" and WEAVIATE_AVAILABLE:
                await store_in_weaviate(chunk_id, embedding, chunk["text"], chunk["metadata"])
            else:
                logger.warning(f"Unsupported vector database type: {VECTOR_DB_TYPE}")
    except Exception as e:
        logger.error(f"Error adding to vector store: {str(e)}")
        raise

async def store_in_vertex_ai(chunk_id: str, text: str, embedding: List[float], metadata: Dict[str, Any]) -> None:
    """Store a chunk in Vertex AI Vector Search"""
    try:
        # Get the index name from environment variables
        index_name = os.getenv("VECTOR_INDEX_NAME")
        if not index_name:
            raise ValueError("VECTOR_INDEX_NAME environment variable not set")
        
        # Get the index endpoint
        index_endpoint = aiplatform.MatchingEngineIndexEndpoint.list(
            filter=f'display_name="{index_name}"'
        )[0]
        
        # Convert metadata to strings
        string_metadata = {k: str(v) for k, v in metadata.items()}
        
        # Add the document to the index
        index_endpoint.upsert(
            embeddings=[[chunk_id, embedding, string_metadata]],
            deployed_index_id=index_name
        )
        
        logger.info(f"Stored chunk {chunk_id} in Vertex AI Vector Search")
    except Exception as e:
        logger.error(f"Error storing in Vertex AI: {str(e)}")
        raise

async def store_in_pinecone(chunk_id: str, embedding: List[float], text: str, metadata: Dict[str, Any]) -> None:
    """Store a chunk in Pinecone"""
    try:
        # Get the index name from environment variables
        index_name = os.getenv("PINECONE_INDEX_NAME")
        if not index_name:
            raise ValueError("PINECONE_INDEX_NAME environment variable not set")
        
        # Get the index
        index = pinecone.Index(index_name)
        
        # Add text to metadata
        metadata["text"] = text
        
        # Upsert the vector
        index.upsert([(chunk_id, embedding, metadata)])
        
        logger.info(f"Stored chunk {chunk_id} in Pinecone")
    except Exception as e:
        logger.error(f"Error storing in Pinecone: {str(e)}")
        raise

async def store_in_weaviate(chunk_id: str, embedding: List[float], text: str, metadata: Dict[str, Any]) -> None:
    """Store a chunk in Weaviate"""
    try:
        # Define the class name
        class_name = "Document"
        
        # Check if the class exists, create it if it doesn't
        if not weaviate_client.schema.exists(class_name):
            class_obj = {
                "class": class_name,
                "vectorizer": "none",  # We're providing our own vectors
                "properties": [
                    {"name": "text", "dataType": ["text"]},
                    {"name": "source", "dataType": ["string"]},
                    {"name": "session_id", "dataType": ["string"]},
                    # Add other metadata properties as needed
                ]
            }
            weaviate_client.schema.create_class(class_obj)
        
        # Prepare the data object
        data_object = {
            "text": text,
            **metadata
        }
        
        # Add the object with the vector
        weaviate_client.data_object.create(
            class_name=class_name,
            data_object=data_object,
            uuid=chunk_id,
            vector=embedding
        )
        
        logger.info(f"Stored chunk {chunk_id} in Weaviate")
    except Exception as e:
        logger.error(f"Error storing in Weaviate: {str(e)}")
        raise

async def query_vector_store(query: str, session_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Query the vector store for relevant chunks
    
    Args:
        query: The query to search for
        session_id: Session ID to filter results
        top_k: Number of results to return
        
    Returns:
        List of relevant text chunks with metadata
    """
    try:
        # Generate embeddings for the query
        query_embedding = await generate_embeddings(query)
        
        # Query the appropriate vector database
        if VECTOR_DB_TYPE == "vertex_ai":
            return await query_vertex_ai(query_embedding, session_id, top_k)
        elif VECTOR_DB_TYPE == "pinecone" and PINECONE_AVAILABLE:
            return await query_pinecone(query_embedding, session_id, top_k)
        elif VECTOR_DB_TYPE == "weaviate" and WEAVIATE_AVAILABLE:
            return await query_weaviate(query_embedding, session_id, top_k)
        else:
            logger.warning(f"Unsupported vector database type: {VECTOR_DB_TYPE}")
            return []
    except Exception as e:
        logger.error(f"Error querying vector store: {str(e)}")
        raise

async def query_vertex_ai(query_embedding: List[float], session_id: str, top_k: int) -> List[Dict[str, Any]]:
    """Query Vertex AI Vector Search"""
    try:
        # Get the index name from environment variables
        index_name = os.getenv("VECTOR_INDEX_NAME")
        if not index_name:
            raise ValueError("VECTOR_INDEX_NAME environment variable not set")
        
        # Get the index endpoint
        index_endpoint = aiplatform.MatchingEngineIndexEndpoint.list(
            filter=f'display_name="{index_name}"'
        )[0]
        
        # Query the index
        response = index_endpoint.find_neighbors(
            deployed_index_id=index_name,
            queries=[query_embedding],
            num_neighbors=top_k
        )
        
        # Process the results
        results = []
        for neighbor in response[0]:
            # Parse metadata
            metadata = neighbor.metadata
            
            # Skip if not from the current session
            if metadata.get("session_id") != session_id:
                continue
            
            # Add to results
            results.append({
                "text": metadata.get("text", ""),
                "metadata": metadata,
                "score": neighbor.distance
            })
        
        return results
    except Exception as e:
        logger.error(f"Error querying Vertex AI: {str(e)}")
        raise

async def query_pinecone(query_embedding: List[float], session_id: str, top_k: int) -> List[Dict[str, Any]]:
    """Query Pinecone"""
    try:
        # Get the index name from environment variables
        index_name = os.getenv("PINECONE_INDEX_NAME")
        if not index_name:
            raise ValueError("PINECONE_INDEX_NAME environment variable not set")
        
        # Get the index
        index = pinecone.Index(index_name)
        
        # Query the index
        response = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter={"session_id": {"$eq": session_id}}
        )
        
        # Process the results
        results = []
        for match in response["matches"]:
            metadata = match["metadata"]
            text = metadata.pop("text", "")
            
            results.append({
                "text": text,
                "metadata": metadata,
                "score": match["score"]
            })
        
        return results
    except Exception as e:
        logger.error(f"Error querying Pinecone: {str(e)}")
        raise

async def query_weaviate(query_embedding: List[float], session_id: str, top_k: int) -> List[Dict[str, Any]]:
    """Query Weaviate"""
    try:
        # Define the class name
        class_name = "Document"
        
        # Query the index
        response = weaviate_client.query.get(
            class_name=class_name,
            properties=["text", "source", "session_id", "_additional {certainty}"]
        ).with_near_vector({
            "vector": query_embedding
        }).with_where({
            "path": ["session_id"],
            "operator": "Equal",
            "valueString": session_id
        }).with_limit(top_k).do()
        
        # Process the results
        results = []
        for obj in response["data"]["Get"][class_name]:
            text = obj.pop("text", "")
            certainty = obj["_additional"]["certainty"]
            obj.pop("_additional")
            
            results.append({
                "text": text,
                "metadata": obj,
                "score": certainty
            })
        
        return results
    except Exception as e:
        logger.error(f"Error querying Weaviate: {str(e)}")
        raise