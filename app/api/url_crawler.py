import logging
import os
from typing import List, Dict, Any, Set
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import trafilatura
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Get crawler settings from environment variables
MAX_CRAWL_DEPTH = int(os.getenv("MAX_CRAWL_DEPTH", 3))
MAX_PAGES_PER_DOMAIN = int(os.getenv("MAX_PAGES_PER_DOMAIN", 50))

# Define chunk size (in tokens)
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

async def crawl_url(start_url: str, max_depth: int = MAX_CRAWL_DEPTH) -> List[Dict[str, Any]]:
    """Crawl a URL and its subpages to extract text content
    
    Args:
        start_url: The URL to start crawling from
        max_depth: Maximum crawl depth
        
    Returns:
        List of text chunks with metadata
    """
    try:
        # Validate URL
        if not start_url.startswith(("http://", "https://")):
            start_url = "https://" + start_url
        
        # Parse the domain to limit crawling to the same domain
        parsed_url = urlparse(start_url)
        base_domain = parsed_url.netloc
        
        # Initialize variables
        visited_urls: Set[str] = set()
        urls_to_visit: List[Dict[str, Any]] = [{"url": start_url, "depth": 0}]
        chunks: List[Dict[str, Any]] = []
        
        # Crawl until we've visited all URLs or reached the maximum number of pages
        while urls_to_visit and len(visited_urls) < MAX_PAGES_PER_DOMAIN:
            # Get the next URL to visit
            current = urls_to_visit.pop(0)
            current_url = current["url"]
            current_depth = current["depth"]
            
            # Skip if we've already visited this URL
            if current_url in visited_urls:
                continue
            
            logger.info(f"Crawling URL: {current_url} (depth: {current_depth})")
            
            try:
                # Mark as visited
                visited_urls.add(current_url)
                
                # Fetch the page
                response = requests.get(
                    current_url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    },
                    timeout=10
                )
                
                # Skip if not HTML
                content_type = response.headers.get("Content-Type", "")
                if "text/html" not in content_type.lower():
                    continue
                
                # Extract text using trafilatura (better content extraction)
                extracted_text = trafilatura.extract(
                    response.text,
                    include_links=True,
                    include_images=False,
                    include_tables=True,
                    output_format="text"
                )
                
                # If trafilatura fails, fall back to BeautifulSoup
                if not extracted_text:
                    soup = BeautifulSoup(response.text, "html.parser")
                    # Remove script and style elements
                    for script_or_style in soup(["script", "style"]):
                        script_or_style.extract()
                    extracted_text = soup.get_text()
                
                # Clean up whitespace
                lines = (line.strip() for line in extracted_text.splitlines())
                chunks_of_lines = (phrase.strip() for line in lines for phrase in line.split("  "))
                cleaned_text = "\n".join(chunk for chunk in chunks_of_lines if chunk)
                
                # Split into chunks
                words = cleaned_text.split()
                for i in range(0, len(words), CHUNK_SIZE - CHUNK_OVERLAP):
                    chunk_words = words[i:i + CHUNK_SIZE]
                    chunk_text = " ".join(chunk_words)
                    
                    chunks.append({
                        "text": chunk_text,
                        "metadata": {
                            "source": current_url,
                            "chunk_index": i // (CHUNK_SIZE - CHUNK_OVERLAP),
                            "title": get_page_title(response.text)
                        }
                    })
                
                # If we haven't reached the maximum depth, find links to crawl
                if current_depth < max_depth:
                    # Parse the page to find links
                    soup = BeautifulSoup(response.text, "html.parser")
                    links = soup.find_all("a", href=True)
                    
                    for link in links:
                        href = link["href"]
                        
                        # Skip empty links, anchors, and non-HTTP links
                        if not href or href.startswith("#") or href.startswith("javascript:"):
                            continue
                        
                        # Convert relative URLs to absolute URLs
                        absolute_url = urljoin(current_url, href)
                        
                        # Skip URLs from different domains
                        parsed_link = urlparse(absolute_url)
                        if parsed_link.netloc != base_domain:
                            continue
                        
                        # Skip if we've already visited or queued this URL
                        if absolute_url in visited_urls or any(item["url"] == absolute_url for item in urls_to_visit):
                            continue
                        
                        # Add to the queue
                        urls_to_visit.append({"url": absolute_url, "depth": current_depth + 1})
            
            except Exception as e:
                logger.error(f"Error crawling URL {current_url}: {str(e)}")
                continue
        
        logger.info(f"Crawling completed. Visited {len(visited_urls)} pages, extracted {len(chunks)} chunks.")
        return chunks
    
    except Exception as e:
        logger.error(f"Error in crawl_url: {str(e)}")
        raise

def get_page_title(html_content: str) -> str:
    """Extract the title from an HTML page"""
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.text.strip()
        else:
            return "Untitled Page"
    except Exception:
        return "Untitled Page"