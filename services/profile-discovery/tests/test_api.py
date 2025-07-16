"""Basic API tests for Profile Discovery Service."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from profile_discovery.main import app
from profile_discovery.core.models import ExtractedResumeData, PersonalInfo, ConfidenceField


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_candidate_data():
    """Sample candidate data for testing."""
    return ExtractedResumeData(
        personal_info=PersonalInfo(
            name=ConfidenceField(value="John Doe", confidence=0.9),
            email=ConfidenceField(value="john.doe@example.com", confidence=0.95),
            location=ConfidenceField(value="San Francisco, CA", confidence=0.8),
            github_url=ConfidenceField(value="https://github.com/johndoe", confidence=0.9),
            linkedin_url=ConfidenceField(value="https://linkedin.com/in/johndoe", confidence=0.8),
            confidence=0.85
        ),
        education={},
        experience={
            "companies": ["Tech Corp", "Startup Inc"],
            "positions": ["Software Engineer", "Senior Developer"]
        },
        skills={
            "technical_skills": ["Python", "JavaScript", "React", "Django"]
        },
        metadata={}
    )


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["service"] == "Profile Discovery Service"
    assert "version" in data
    assert "endpoints" in data


def test_health_endpoint(client):
    """Test health endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data
    assert "external_services" in data


def test_supported_platforms_endpoint(client):
    """Test supported platforms endpoint."""
    response = client.get("/api/v1/supported-platforms")
    assert response.status_code == 200
    
    data = response.json()
    assert "platforms" in data
    assert "discovery_strategies" in data
    assert "rate_limits" in data
    
    # Check that GitHub and LinkedIn are supported
    platforms = [p["value"] for p in data["platforms"]]
    assert "github" in platforms
    assert "linkedin" in platforms


@patch('profile_discovery.services.discovery_service.DiscoveryService')
def test_discover_profiles_endpoint(mock_discovery_service, client, sample_candidate_data):
    """Test discover profiles endpoint."""
    # Mock the discovery service
    mock_service = Mock()
    mock_discovery_service.return_value = mock_service
    
    # Mock the discovery response
    mock_response = Mock()
    mock_response.success = True
    mock_response.github_profiles = []
    mock_response.linkedin_profiles = []
    mock_response.processing_time_ms = 100.0
    mock_response.discovery_metadata = Mock()
    mock_response.error_message = None
    
    mock_service.discover_profiles.return_value = mock_response
    
    # Create request payload
    request_data = {
        "candidate_data": sample_candidate_data.model_dump(),
        "discovery_options": {
            "search_github": True,
            "search_linkedin": True,
            "max_github_results": 5,
            "max_linkedin_results": 3,
            "min_confidence_score": 0.3,
            "include_repository_analysis": True
        }
    }
    
    response = client.post("/api/v1/discover", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "github_profiles" in data
    assert "linkedin_profiles" in data
    assert "processing_time_ms" in data


def test_discover_profiles_missing_name(client):
    """Test discover profiles with missing candidate name."""
    request_data = {
        "candidate_data": {
            "personal_info": {
                "name": {"value": None, "confidence": 0.0},
                "email": {"value": "test@example.com", "confidence": 0.9},
                "phone": {"value": None, "confidence": 0.0},
                "location": {"value": None, "confidence": 0.0},
                "linkedin_url": {"value": None, "confidence": 0.0},
                "github_url": {"value": None, "confidence": 0.0},
                "confidence": 0.0
            },
            "education": {},
            "experience": {},
            "skills": {},
            "metadata": {}
        }
    }
    
    response = client.post("/api/v1/discover", json=request_data)
    assert response.status_code == 400
    assert "Candidate name is required" in response.json()["detail"]


def test_cors_headers(client):
    """Test that CORS headers are present."""
    response = client.options("/api/v1/health")
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


def test_correlation_id_header(client):
    """Test that correlation ID is added to response headers."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "x-correlation-id" in response.headers
    assert response.headers["x-correlation-id"] is not None
