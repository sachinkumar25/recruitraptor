#!/usr/bin/env python3
"""Debug script to test GitHub profile validation logic."""

import sys
import os
sys.path.append('src')

from profile_discovery.clients.github_client import GitHubClient
from profile_discovery.core.models import GitHubProfile

def test_github_validation():
    """Test GitHub profile validation with Sachin's actual data."""
    print("🔍 TESTING GITHUB PROFILE VALIDATION")
    print("=" * 50)
    
    # Create GitHub client
    client = GitHubClient()
    
    # Test data from Sachin's resume
    candidate_data = {
        'name': {'value': 'Sashvad (Sachin) Satishkumar', 'confidence': 0.9},
        'email': {'value': 'sskumar@umd.edu', 'confidence': 0.95},
        'location': {'value': 'College Park, MD', 'confidence': 0.8},
        'experience': {
            'companies': ['University of Maryland', 'Google', 'Microsoft']
        }
    }
    
    print("📊 CANDIDATE DATA:")
    print(f"   Name: {candidate_data['name']['value']}")
    print(f"   Email: {candidate_data['email']['value']}")
    print(f"   Location: {candidate_data['location']['value']}")
    print(f"   Companies: {candidate_data['experience']['companies']}")
    
    # Get Sachin's actual GitHub profile
    print(f"\n🔍 FETCHING GITHUB PROFILE: sachinkumar25")
    profile = client.get_user_profile('sachinkumar25')
    
    if profile:
        print(f"\n📊 GITHUB PROFILE DATA:")
        print(f"   Username: {profile.username}")
        print(f"   Name: {profile.name}")
        print(f"   Email: {profile.email}")
        print(f"   Location: {profile.location}")
        print(f"   Company: {profile.company}")
        print(f"   Bio: {profile.bio}")
        print(f"   Public repos: {profile.public_repos}")
        print(f"   Followers: {profile.followers}")
        
        # Test validation
        print(f"\n🔍 TESTING VALIDATION LOGIC:")
        confidence, reasoning = client.validate_profile_match(profile, candidate_data)
        
        print(f"   Confidence Score: {confidence:.2f}")
        print(f"   Reasoning: {reasoning}")
        
        # Test individual validation components
        print(f"\n🔍 DETAILED VALIDATION BREAKDOWN:")
        
        # Name matching
        candidate_name = candidate_data['name']['value'].lower()
        profile_name = profile.name.lower() if profile.name else ""
        print(f"   Name matching:")
        print(f"     Candidate: '{candidate_name}'")
        print(f"     Profile: '{profile_name}'")
        print(f"     Contains check: {candidate_name in profile_name or profile_name in candidate_name}")
        print(f"     Word check: {any(word in profile_name for word in candidate_name.split())}")
        
        # Email matching
        candidate_email = candidate_data['email']['value'].lower()
        profile_email = profile.email.lower() if profile.email else ""
        print(f"   Email matching:")
        print(f"     Candidate: '{candidate_email}'")
        print(f"     Profile: '{profile_email}'")
        print(f"     Exact match: {candidate_email == profile_email}")
        
        # Location matching
        candidate_location = candidate_data['location']['value'].lower()
        profile_location = profile.location.lower() if profile.location else ""
        print(f"   Location matching:")
        print(f"     Candidate: '{candidate_location}'")
        print(f"     Profile: '{profile_location}'")
        print(f"     Contains check: {candidate_location in profile_location or profile_location in candidate_location}")
        
        # Company matching
        candidate_companies = [c.lower() for c in candidate_data['experience']['companies']]
        profile_company = profile.company.lower() if profile.company else ""
        print(f"   Company matching:")
        print(f"     Candidate companies: {candidate_companies}")
        print(f"     Profile company: '{profile_company}'")
        print(f"     Any match: {any(company in profile_company or profile_company in company for company in candidate_companies)}")
        
        # Activity level
        print(f"   Activity level:")
        print(f"     Public repos > 5: {profile.public_repos > 5}")
        print(f"     Followers > 10: {profile.followers > 10}")
        
    else:
        print("❌ Failed to fetch GitHub profile")

if __name__ == "__main__":
    test_github_validation() 