import unittest
import os
import tempfile
import json
from app.utils.helpers import (
    generate_unique_id,
    sanitize_filename,
    get_file_extension,
    is_valid_file_type,
    is_valid_url,
    truncate_text,
    format_sources_for_display,
    save_upload_metadata,
    load_upload_metadata
)

class TestHelpers(unittest.TestCase):
    """Test cases for helper functions"""
    
    def test_generate_unique_id(self):
        """Test that unique IDs are generated"""
        id1 = generate_unique_id()
        id2 = generate_unique_id()
        self.assertIsNotNone(id1)
        self.assertIsNotNone(id2)
        self.assertNotEqual(id1, id2)
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        # Test with valid filename
        self.assertEqual(sanitize_filename("test.pdf"), "test.pdf")
        
        # Test with dangerous characters
        self.assertEqual(sanitize_filename("test/file<>:*?\"|.pdf"), "testfile.pdf")
        
        # Test with empty filename
        sanitized = sanitize_filename("")
        self.assertTrue(sanitized.startswith("file_"))
    
    def test_get_file_extension(self):
        """Test getting file extension"""
        self.assertEqual(get_file_extension("test.pdf"), ".pdf")
        self.assertEqual(get_file_extension("test.PDF"), ".pdf")
        self.assertEqual(get_file_extension("test"), "")
    
    def test_is_valid_file_type(self):
        """Test file type validation"""
        self.assertTrue(is_valid_file_type("test.pdf"))
        self.assertTrue(is_valid_file_type("test.docx"))
        self.assertTrue(is_valid_file_type("test.txt"))
        self.assertTrue(is_valid_file_type("test.html"))
        self.assertFalse(is_valid_file_type("test.exe"))
        self.assertFalse(is_valid_file_type("test.zip"))
    
    def test_is_valid_url(self):
        """Test URL validation"""
        self.assertTrue(is_valid_url("https://example.com"))
        self.assertTrue(is_valid_url("http://example.com"))
        self.assertFalse(is_valid_url("example.com"))
        self.assertFalse(is_valid_url("ftp://example.com"))
    
    def test_truncate_text(self):
        """Test text truncation"""
        # Test with text shorter than max length
        self.assertEqual(truncate_text("Hello", 10), "Hello")
        
        # Test with text longer than max length
        self.assertEqual(truncate_text("Hello World", 5), "Hello...")
    
    def test_format_sources_for_display(self):
        """Test formatting sources for display"""
        sources = [
            {"source": "test.pdf", "text": "This is a test", "page": 1},
            {"source": "example.com", "text": "This is an example", "title": "Example"}
        ]
        
        formatted = format_sources_for_display(sources)
        
        self.assertEqual(len(formatted), 2)
        self.assertEqual(formatted[0]["source"], "test.pdf")
        self.assertEqual(formatted[0]["text"], "This is a test")
        self.assertEqual(formatted[0]["page"], 1)
        
        self.assertEqual(formatted[1]["source"], "example.com")
        self.assertEqual(formatted[1]["text"], "This is an example")
        self.assertEqual(formatted[1]["title"], "Example")
    
    def test_metadata_save_and_load(self):
        """Test saving and loading metadata"""
        # Create a temporary directory for metadata
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set the current directory to the temp directory
            original_dir = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create metadata directory
                os.makedirs("metadata", exist_ok=True)
                
                # Test data
                file_id = "test_id"
                filename = "test.pdf"
                session_id = "test_session"
                metadata = {"pages": 10, "author": "Test Author"}
                
                # Save metadata
                save_upload_metadata(file_id, filename, session_id, metadata)
                
                # Check if file was created
                metadata_path = f"metadata/{file_id}.json"
                self.assertTrue(os.path.exists(metadata_path))
                
                # Load metadata
                loaded_metadata = load_upload_metadata(file_id)
                
                # Verify loaded metadata
                self.assertEqual(loaded_metadata["file_id"], file_id)
                self.assertEqual(loaded_metadata["filename"], filename)
                self.assertEqual(loaded_metadata["session_id"], session_id)
                self.assertEqual(loaded_metadata["pages"], 10)
                self.assertEqual(loaded_metadata["author"], "Test Author")
                
                # Test loading non-existent metadata
                self.assertIsNone(load_upload_metadata("non_existent_id"))
            finally:
                # Restore original directory
                os.chdir(original_dir)

if __name__ == "__main__":
    unittest.main()