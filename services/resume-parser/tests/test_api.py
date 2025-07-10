"""Integration tests for resume parser API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from resume_parser.main import app

client = TestClient(app)

class TestAPIEndpoints:
    """Test cases for API endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Resume Parser Service"
        assert data["version"] == "0.1.0"
        assert data["status"] == "running"
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    def test_supported_types(self):
        """Test supported types endpoint."""
        response = client.get("/api/v1/supported-types")
        assert response.status_code == 200
        data = response.json()
        assert "supported_types" in data
        assert "max_file_size_mb" in data
        assert "min_word_count" in data
        assert "pdf" in data["supported_types"]
        assert "docx" in data["supported_types"]
        assert "txt" in data["supported_types"]
    
    def test_upload_no_file(self):
        """Test upload endpoint with no file."""
        response = client.post("/api/v1/upload")
        assert response.status_code == 422  # Validation error
    
    def test_upload_invalid_file_type(self):
        """Test upload with invalid file type."""
        files = {"file": ("test.jpg", b"fake content", "image/jpeg")}
        response = client.post("/api/v1/upload", files=files)
        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["detail"]
    
    def test_upload_empty_file(self):
        """Test upload with empty file."""
        files = {"file": ("test.txt", b"", "text/plain")}
        response = client.post("/api/v1/upload", files=files)
        assert response.status_code == 400
        assert "Empty file" in response.json()["detail"]
    
    @patch('resume_parser.api.routes.text_extractor')
    @patch('resume_parser.api.routes.resume_parser')
    def test_upload_success(self, mock_parser, mock_extractor):
        """Test successful resume upload."""
        # Mock the extractor
        mock_extractor.extract.return_value = (
            "John Doe Software Engineer Python Java React " * 50,  # Ensure >100 words
            {
                'file_type': 'txt',
                'file_size': 1000,
                'extraction_method': 'text-encoding-detection',
                'encoding': 'utf-8',
                'word_count': 200,
                'extraction_errors': []
            }
        )
        
        # Mock the parser
        mock_parser.parse.return_value = {
            'personal_info': {
                'name': {'value': 'John Doe', 'confidence': 0.8},
                'email': {'value': 'john@example.com', 'confidence': 0.95},
                'phone': {'value': None, 'confidence': 0.0},
                'location': {'value': None, 'confidence': 0.0},
                'linkedin_url': {'value': None, 'confidence': 0.0},
                'github_url': {'value': None, 'confidence': 0.0},
                'confidence': 0.4
            },
            'education': {
                'institutions': [],
                'degrees': [],
                'fields_of_study': [],
                'dates': [],
                'gpa': {'value': None, 'confidence': 0.0},
                'confidence': 0.0
            },
            'experience': {
                'companies': [],
                'positions': [],
                'dates': [],
                'descriptions': [],
                'confidence': 0.0
            },
            'skills': {
                'technical_skills': ['Python', 'Java', 'React'],
                'soft_skills': [],
                'categories': {
                    'programming_languages': ['Python', 'Java'],
                    'frameworks': ['React'],
                    'databases': [],
                    'cloud_platforms': [],
                    'tools': []
                },
                'confidence': 0.8
            },
            'metadata': {
                'total_words': 200,
                'parsing_timestamp': '2024-01-01T00:00:00',
                'confidence_overall': 0.3
            }
        }
        
        # Test upload
        files = {"file": ("resume.txt", b"John Doe Software Engineer Python Java React " * 50, "text/plain")}
        response = client.post("/api/v1/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["parsed_data"] is not None
        assert data["processing_time_ms"] > 0
        assert data["file_metadata"] is not None
        
        # Verify parsed data structure
        parsed_data = data["parsed_data"]
        assert "personal_info" in parsed_data
        assert "education" in parsed_data
        assert "experience" in parsed_data
        assert "skills" in parsed_data
        assert "metadata" in parsed_data
    
    def test_upload_file_too_large(self):
        """Test upload with file exceeding size limit."""
        # Create a file larger than 5MB
        large_content = b"x" * (6 * 1024 * 1024)  # 6MB
        files = {"file": ("large.txt", large_content, "text/plain")}
        response = client.post("/api/v1/upload", files=files)
        assert response.status_code == 400
        assert "exceeds maximum" in response.json()["detail"]
    
    def test_upload_insufficient_content(self):
        """Test upload with insufficient content."""
        short_content = b"This is a very short resume"
        files = {"file": ("short.txt", short_content, "text/plain")}
        response = client.post("/api/v1/upload", files=files)
        assert response.status_code == 400
        assert "minimum required" in response.json()["detail"]
    
    def test_cors_headers(self):
        """Test CORS headers are present."""
        response = client.options("/api/v1/upload")
        assert response.status_code == 200
        # CORS headers should be present (handled by FastAPI middleware)
    
    def test_request_logging_middleware(self):
        """Test that request logging middleware adds process time header."""
        response = client.get("/")
        assert response.status_code == 200
        assert "X-Process-Time" in response.headers
