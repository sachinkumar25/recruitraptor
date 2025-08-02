#!/usr/bin/env python3
"""
Quick test script for Data Enrichment Service.
Simple manual testing with curl-like functionality.
"""

import requests
import json
import time


def test_health():
    """Test health endpoint."""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8002/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health: {data['status']}")
            print(f"   Version: {data['version']}")
            print(f"   Uptime: {data['uptime_seconds']:.2f}s")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def test_root():
    """Test root endpoint."""
    print("\n🔍 Testing root endpoint...")
    try:
        response = requests.get("http://localhost:8002/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root: {data['service']}")
            print(f"   Status: {data['status']}")
            return True
        else:
            print(f"❌ Root failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root error: {e}")
        return False


def test_capabilities():
    """Test capabilities endpoint."""
    print("\n🔍 Testing capabilities...")
    try:
        response = requests.get("http://localhost:8002/api/v1/capabilities")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Capabilities: {data['service_name']}")
            print(f"   Sources: {', '.join(data['supported_data_sources'])}")
            return True
        else:
            print(f"❌ Capabilities failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Capabilities error: {e}")
        return False


def test_basic_enrichment():
    """Test basic enrichment."""
    print("\n🔍 Testing basic enrichment...")
    
    # Sample data
    sample_data = {
        "resume_data": {
            "personal_info": {
                "name": {"value": "John Doe", "confidence": 0.95},
                "email": {"value": "john.doe@email.com", "confidence": 0.90},
                "confidence": 0.85
            },
            "skills": {
                "technical_skills": ["Python", "JavaScript", "React"],
                "categories": {
                    "programming_languages": ["Python", "JavaScript"],
                    "frameworks": ["React"]
                }
            }
        },
        "github_profiles": [{
            "profile": {
                "username": "johndoe",
                "name": "John Doe",
                "public_repos": 25,
                "profile_url": "https://github.com/johndoe"
            },
            "confidence": 0.90,
            "match_reasoning": "Name match",
            "repositories": [],
            "languages_used": {"Python": 60, "JavaScript": 40},
            "frameworks_detected": ["React"]
        }]
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:8002/api/v1/enrich",
            json=sample_data,
            headers={"Content-Type": "application/json"}
        )
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Enrichment successful")
            print(f"   Processing time: {processing_time:.2f}s")
            print(f"   Overall confidence: {data['enriched_profile']['overall_confidence']}")
            print(f"   Name: {data['enriched_profile']['personal_info']['name']}")
            return True
        else:
            print(f"❌ Enrichment failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Enrichment error: {e}")
        return False


def main():
    """Run quick tests."""
    print("🚀 Quick Data Enrichment Service Tests")
    print("=" * 40)
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Capabilities", test_capabilities),
        ("Basic Enrichment", test_basic_enrichment)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 SUMMARY")
    print("=" * 40)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed.")


if __name__ == "__main__":
    main() 