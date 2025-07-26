import unittest
import requests
import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TestChatbotApp(unittest.TestCase):
    """Test cases for the AI Document QA Chatbot"""
    
    BASE_URL = "http://localhost:8000"
    
    @classmethod
    def setUpClass(cls):
        """Check if the application is running before running tests"""
        try:
            response = requests.get(f"{cls.BASE_URL}/health", timeout=5)
            if response.status_code != 200:
                print("\nERROR: Application is not running or health check failed.")
                print("Please start the application with 'uvicorn app.main:app --host 0.0.0.0 --port 8000' before running tests.")
                sys.exit(1)
        except requests.exceptions.ConnectionError:
            print("\nERROR: Could not connect to the application.")
            print("Please start the application with 'uvicorn app.main:app --host 0.0.0.0 --port 8000' before running tests.")
            sys.exit(1)
    
    def test_health_endpoint(self):
        """Test the health endpoint"""
        response = requests.get(f"{self.BASE_URL}/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
    
    def test_index_page(self):
        """Test the index page loads"""
        response = requests.get(self.BASE_URL)
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
    
    def test_session_creation(self):
        """Test creating a new session"""
        response = requests.get(f"{self.BASE_URL}/status/test_session")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
    
    def test_session_clearing(self):
        """Test clearing a session"""
        # First create a session
        requests.get(f"{self.BASE_URL}/status/test_clear_session")
        
        # Then clear it
        response = requests.delete(f"{self.BASE_URL}/clear/test_clear_session")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("cleared", data["message"])

if __name__ == "__main__":
    unittest.main()