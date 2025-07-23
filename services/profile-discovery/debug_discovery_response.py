#!/usr/bin/env python3
"""Debug script to see the full Profile Discovery response."""

import requests
import json
import time

def debug_discovery_response():
    """Debug the Profile Discovery service response."""
    print("🔍 DEBUGGING PROFILE DISCOVERY RESPONSE")
    print("=" * 50)
    
    # Test data with Sachin's actual GitHub and LinkedIn URLs
    test_request = {
        "candidate_data": {
            "personal_info": {
                "name": {"value": "Sashvad (Sachin) Satishkumar", "confidence": 0.9},
                "email": {"value": "sskumar@umd.edu", "confidence": 0.95},
                "phone": {"value": "571-236-6612", "confidence": 0.9},
                "location": {"value": "College Park, MD", "confidence": 0.8},
                "linkedin_url": {"value": "linkedin.com/in/sashvad-satishkumar", "confidence": 0.95},
                "github_url": {"value": "https://github.com/sachinkumar25", "confidence": 1.0},
                "confidence": 0.9
            },
            "education": {
                "institutions": ["University of Maryland"],
                "degrees": ["Bachelor of Science"],
                "fields_of_study": ["Computer Science"],
                "dates": ["2020-2024"],
                "gpa": {"value": "3.83", "confidence": 0.9},
                "confidence": 0.8
            },
            "experience": {
                "companies": ["Google", "Microsoft"],
                "positions": ["Software Engineer", "Data Scientist"],
                "dates": ["2022-2024", "2020-2022"],
                "descriptions": ["Developed scalable systems", "Built ML models"],
                "confidence": 0.8
            },
            "skills": {
                "technical_skills": ["Python", "JavaScript", "AWS", "Docker"],
                "soft_skills": ["Leadership", "Communication"],
                "categories": {
                    "programming_languages": ["Python", "JavaScript"],
                    "frameworks": ["React", "Django"],
                    "databases": ["PostgreSQL", "MongoDB"],
                    "cloud_platforms": ["AWS", "GCP"],
                    "tools": ["Docker", "Git"]
                },
                "confidence": 0.9
            },
            "metadata": {
                "total_words": 500,
                "parsing_timestamp": "2025-07-23T13:52:25",
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
        print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200:
            discovery_data = response.json()
            print(f"\n✅ SUCCESS RESPONSE:")
            print(json.dumps(discovery_data, indent=2))
            
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
            
        else:
            print(f"\n❌ ERROR RESPONSE:")
            print(f"   Status: {response.status_code}")
            print(f"   Text: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ CONNECTION ERROR:")
        print("   Could not connect to Profile Discovery service at http://localhost:8001")
        print("   Make sure the service is running with: python -m profile_discovery.main")
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR:")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_discovery_response() 