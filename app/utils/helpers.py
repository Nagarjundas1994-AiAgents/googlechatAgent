import os
import logging
import uuid
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_unique_id() -> str:
    """Generate a unique ID for documents, chunks, etc."""
    return str(uuid.uuid4())

def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to ensure it's safe for the filesystem"""
    # Replace potentially dangerous characters
    safe_filename = "".join([c for c in filename if c.isalnum() or c in "._- "])
    # Trim whitespace and ensure it's not empty
    safe_filename = safe_filename.strip()
    if not safe_filename:
        safe_filename = f"file_{generate_unique_id()[:8]}"
    return safe_filename

def get_file_extension(filename: str) -> str:
    """Get the file extension from a filename"""
    return os.path.splitext(filename)[1].lower()

def is_valid_file_type(filename: str) -> bool:
    """Check if a file type is supported"""
    valid_extensions = [".pdf", ".docx", ".txt", ".html", ".htm"]
    return get_file_extension(filename) in valid_extensions

def is_valid_url(url: str) -> bool:
    """Basic URL validation"""
    return url.startswith(("http://", "https://"))

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to a maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def format_sources_for_display(sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format source metadata for display in the UI"""
    formatted_sources = []
    
    for source in sources:
        formatted_source = {
            "source": source.get("source", "Unknown"),
            "text": truncate_text(source.get("text", ""), 200)
        }
        
        # Add page number if available
        if "page" in source:
            formatted_source["page"] = source["page"]
        
        # Add title if available
        if "title" in source:
            formatted_source["title"] = source["title"]
        
        formatted_sources.append(formatted_source)
    
    return formatted_sources

def save_upload_metadata(file_id: str, filename: str, session_id: str, metadata: Dict[str, Any]) -> None:
    """Save metadata about an uploaded file"""
    try:
        # Create metadata directory if it doesn't exist
        os.makedirs("metadata", exist_ok=True)
        
        # Prepare metadata
        file_metadata = {
            "file_id": file_id,
            "filename": filename,
            "session_id": session_id,
            "upload_time": datetime.now().isoformat(),
            **metadata
        }
        
        # Save metadata to a JSON file
        with open(f"metadata/{file_id}.json", "w") as f:
            json.dump(file_metadata, f, indent=2)
            
        logger.info(f"Saved metadata for file {filename} (ID: {file_id})")
    except Exception as e:
        logger.error(f"Error saving metadata for file {filename}: {str(e)}")

def load_upload_metadata(file_id: str) -> Optional[Dict[str, Any]]:
    """Load metadata about an uploaded file"""
    try:
        metadata_path = f"metadata/{file_id}.json"
        
        if not os.path.exists(metadata_path):
            logger.warning(f"Metadata file not found for file ID: {file_id}")
            return None
        
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
            
        return metadata
    except Exception as e:
        logger.error(f"Error loading metadata for file ID {file_id}: {str(e)}")
        return None