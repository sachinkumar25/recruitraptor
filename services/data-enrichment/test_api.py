#!/usr/bin/env python3
"""Simple API test for Data Enrichment Service."""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastapi.testclient import TestClient
from data_enrichment.main import app

# Create test client
client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint."""
    print("🔍 Testing root endpoint...")
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Data Enrichment Service"
    assert data["status"] == "running"
    print("✅ Root endpoint works correctly")


def test_health_endpoint():
    """Test the health endpoint."""
    print("🔍 Testing health endpoint...")
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Data Enrichment Service"
    print("✅ Health endpoint works correctly")


def test_api_health_endpoint():
    """Test the API health endpoint."""
    print("🔍 Testing API health endpoint...")
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    print("✅ API health endpoint works correctly")


def test_capabilities_endpoint():
    """Test the capabilities endpoint."""
    print("🔍 Testing capabilities endpoint...")
    response = client.get("/api/v1/capabilities")
    assert response.status_code == 200
    data = response.json()
    assert data["service_name"] == "data-enrichment"
    assert "supported_data_sources" in data
    assert "supported_algorithms" in data
    print("✅ Capabilities endpoint works correctly")


def test_config_endpoint():
    """Test the config endpoint."""
    print("🔍 Testing config endpoint...")
    response = client.get("/api/v1/config")
    assert response.status_code == 200
    data = response.json()
    assert data["service_name"] == "data-enrichment"
    assert "min_confidence_threshold" in data
    assert "skill_weighting_factor" in data
    print("✅ Config endpoint works correctly")


def test_statistics_endpoint():
    """Test the statistics endpoint."""
    print("🔍 Testing statistics endpoint...")
    response = client.get("/api/v1/statistics")
    assert response.status_code == 200
    data = response.json()
    assert data["service_name"] == "data-enrichment"
    assert "version" in data
    print("✅ Statistics endpoint works correctly")


def test_metrics_endpoint():
    """Test the metrics endpoint."""
    print("🔍 Testing metrics endpoint...")
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Data Enrichment Service"
    assert "uptime_seconds" in data
    print("✅ Metrics endpoint works correctly")


def test_validation_endpoint():
    """Test the validation endpoint."""
    print("🔍 Testing validation endpoint...")
    
    # Test with valid request
    valid_request = {
        "resume_data": {
            "personal_info": {
                "name": {"value": "Test User", "confidence": 0.8},
                "confidence": 0.8
            },
            "skills": {"technical_skills": ["Python", "JavaScript"]}
        },
        "github_profiles": [
            {
                "profile": {
                    "username": "testuser",
                    "profile_url": "https://github.com/testuser"
                },
                "confidence": 0.8,
                "match_reasoning": "Test match"
            }
        ],
        "linkedin_profiles": []
    }
    
    response = client.post("/api/v1/validate", json=valid_request)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] == True
    assert data["error_count"] == 0
    print("✅ Validation endpoint works correctly")


def run_all_tests():
    """Run all API tests."""
    print("🚀 Running Data Enrichment Service API Tests")
    print("=" * 50)
    
    try:
        test_root_endpoint()
        test_health_endpoint()
        test_api_health_endpoint()
        test_capabilities_endpoint()
        test_config_endpoint()
        test_statistics_endpoint()
        test_metrics_endpoint()
        test_validation_endpoint()
        
        print("\n✅ All API tests passed successfully!")
        print("🎉 Data Enrichment Service is ready for use!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests() 