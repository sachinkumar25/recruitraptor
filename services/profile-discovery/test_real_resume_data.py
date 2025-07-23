#!/usr/bin/env python3
"""Test with real resume data structure."""

import requests
import json
import time

def test_with_real_resume_data():
    """Test with the exact data structure from real resume parsing."""
    print("🔍 TESTING WITH REAL RESUME DATA STRUCTURE")
    print("=" * 50)
    
    # Use the exact data structure from the real resume parsing output
    test_request = {
        "candidate_data": {
            "personal_info": {
                "name": {"value": "Satishkumar 571-236-6612", "confidence": 0.8},
                "email": {"value": "sskumar@umd.edu", "confidence": 0.95},
                "phone": {"value": " 5712366612", "confidence": 0.9},
                "location": {"value": "College Park", "confidence": 0.7},
                "linkedin_url": {"value": "linkedin.com/in/sashvad-satishkumar", "confidence": 0.95},
                "github_url": {"value": "https://github.com/sachinkumar25", "confidence": 1.0},
                "github_urls": [
                    {
                        "url": "https://github.com/sachinkumar25",
                        "username": "sachinkumar25", 
                        "confidence": 1.0,
                        "pattern_type": 1
                    }
                ],
                "confidence": 0.8833333333333333
            },
            "education": {
                "institutions": ["github.com/sachinkumar25 EDUCATION University of Maryland"],
                "degrees": [],
                "fields_of_study": [],
                "dates": [],
                "gpa": {"value": "3.83", "confidence": 0.9},
                "confidence": 0.8
            },
            "experience": {
                "companies": ["github.com/sachinkumar25 EDUCATION University of Maryland", "Data Science College Park", "Scholarship Recipient - Coursework: Computer Systems"],
                "positions": [],
                "dates": [],
                "descriptions": [],
                "confidence": 0.8
            },
            "skills": {
                "technical_skills": ["AWS", "PHP", "Go", "Python", "Pandas", "Scikit-Learn", "TensorFlow", "SQL", "CI/CD", "Flask"],
                "soft_skills": [],
                "categories": {
                    "programming_languages": [],
                    "frameworks": [],
                    "databases": [],
                    "cloud_platforms": [],
                    "tools": []
                },
                "confidence": 0.9
            },
            "metadata": {
                "total_words": 500,
                "parsing_timestamp": "2025-07-23T14:37:07",
                "confidence_overall": 0.85
            }
        },
        "discovery_options": {
            "search_github": True,
            "search_linkedin": True,
            "max_github_results": 5,
            "max_linkedin_results": 3,
            "min_confidence_score": 0.3,
            "include_repository_analysis": True
        }
    }
    
    print("📤 Sending request to Profile Discovery service...")
    print(f"   GitHub URL: {test_request['candidate_data']['personal_info']['github_url']['value']}")
    print(f"   LinkedIn URL: {test_request['candidate_data']['personal_info']['linkedin_url']['value']}")
    print(f"   Name: {test_request['candidate_data']['personal_info']['name']['value']}")
    print(f"   Companies: {test_request['candidate_data']['experience']['companies']}")
    
    try:
        start_time = time.time()
        response = requests.post(
            'http://localhost:8001/api/v1/discover',
            json=test_request,
            timeout=60
        )
        request_time = time.time() - start_time
        
        print(f"\n📥 RESPONSE RECEIVED ({request_time:.2f}s):")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            discovery_data = response.json()
            
            # Analyze the response
            success = discovery_data.get('success', False)
            github_profiles = discovery_data.get('github_profiles', [])
            linkedin_profiles = discovery_data.get('linkedin_profiles', [])
            metadata = discovery_data.get('discovery_metadata', {})
            errors = metadata.get('errors_encountered', [])
            
            print(f"\n📊 ANALYSIS:")
            print(f"   Success: {success}")
            print(f"   GitHub profiles found: {len(github_profiles)}")
            print(f"   LinkedIn profiles found: {len(linkedin_profiles)}")
            print(f"   Processing time: {discovery_data.get('processing_time_ms', 0):.2f}ms")
            print(f"   Strategies used: {metadata.get('strategies_used', [])}")
            
            if errors:
                print(f"   Errors encountered: {errors}")
            
            if github_profiles:
                print(f"\n🐙 GITHUB PROFILES:")
                for i, profile in enumerate(github_profiles):
                    print(f"   {i+1}. Username: {profile.get('profile', {}).get('username', 'N/A')}")
                    print(f"      URL: {profile.get('profile', {}).get('profile_url', 'N/A')}")
                    print(f"      Confidence: {profile.get('confidence', 0):.2f}")
                    print(f"      Strategy: {profile.get('discovery_strategy', 'N/A')}")
                    print(f"      Reasoning: {profile.get('match_reasoning', 'N/A')}")
            
            if linkedin_profiles:
                print(f"\n💼 LINKEDIN PROFILES:")
                for i, profile in enumerate(linkedin_profiles):
                    print(f"   {i+1}. URL: {profile.get('profile', {}).get('profile_url', 'N/A')}")
                    print(f"      Name: {profile.get('profile', {}).get('name', 'N/A')}")
                    print(f"      Confidence: {profile.get('confidence', 0):.2f}")
                    print(f"      Strategy: {profile.get('discovery_strategy', 'N/A')}")
                    print(f"      Reasoning: {profile.get('match_reasoning', 'N/A')}")
            
            # Show full response for debugging
            print(f"\n🔍 FULL RESPONSE:")
            print(json.dumps(discovery_data, indent=2))
            
        else:
            print(f"\n❌ ERROR RESPONSE:")
            print(f"   Status: {response.status_code}")
            print(f"   Text: {response.text}")
            
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR:")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_real_resume_data() 