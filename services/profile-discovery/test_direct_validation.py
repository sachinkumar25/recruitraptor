#!/usr/bin/env python3
"""Test direct URL validation for GitHub profiles."""

import sys
import os
sys.path.append('src')

from profile_discovery.services.discovery_service import DiscoveryService
from profile_discovery.core.models import ExtractedResumeData, PersonalInfo, ConfidenceField, DiscoveryRequest, DiscoveryOptions

def test_direct_github_validation():
    """Test direct GitHub URL validation."""
    print("🔍 TESTING DIRECT GITHUB URL VALIDATION")
    print("=" * 50)
    
    # Create minimal test data with Sachin's GitHub URL
    personal_info = PersonalInfo(
        name=ConfidenceField(value="Sashvad (Sachin) Satishkumar", confidence=0.9),
        email=ConfidenceField(value="sskumar@umd.edu", confidence=0.95),
        phone=ConfidenceField(value="571-236-6612", confidence=0.9),
        location=ConfidenceField(value="College Park, MD", confidence=0.8),
        linkedin_url=ConfidenceField(value="linkedin.com/in/sashvad-satishkumar", confidence=0.95),
        github_url=ConfidenceField(value="https://github.com/sachinkumar25", confidence=1.0),
        confidence=0.9
    )
    
    candidate_data = ExtractedResumeData(
        personal_info=personal_info,
        education={
            "institutions": ["University of Maryland"],
            "companies": ["University of Maryland", "Google", "Microsoft"]
        },
        experience={
            "companies": ["University of Maryland", "Google", "Microsoft"],
            "positions": ["Software Engineer", "Data Scientist"]
        },
        skills={
            "technical_skills": ["Python", "JavaScript", "AWS", "Docker"]
        }
    )
    
    # Create discovery request
    request = DiscoveryRequest(
        candidate_data=candidate_data,
        discovery_options=DiscoveryOptions(
            search_github=True,
            search_linkedin=False,  # Skip LinkedIn for this test
            max_github_results=5,
            max_linkedin_results=3,
            min_confidence_score=0.3,
            include_repository_analysis=True
        )
    )
    
    # Test discovery service
    try:
        service = DiscoveryService()
        print("✅ Discovery service initialized")
        
        # Test candidate info extraction
        candidate_info = service._extract_candidate_info(candidate_data)
        print(f"✅ Candidate info extracted:")
        print(f"   Name: {candidate_info['name']}")
        print(f"   Email: {candidate_info['email']}")
        print(f"   GitHub URL: {candidate_info['github_url']}")
        print(f"   Companies: {candidate_info['companies']}")
        
        # Test GitHub username extraction
        username = service._extract_github_username(candidate_info['github_url'])
        print(f"✅ GitHub username extracted: {username}")
        
        # Test direct GitHub profile discovery
        print(f"\n🔍 TESTING DIRECT GITHUB PROFILE DISCOVERY:")
        github_profiles = service._discover_github_profiles(candidate_info, request.discovery_options, candidate_data)
        
        print(f"✅ GitHub profiles found: {len(github_profiles)}")
        
        for i, profile_match in enumerate(github_profiles):
            print(f"\n🐙 GitHub Profile {i+1}:")
            print(f"   Username: {profile_match.profile.username}")
            print(f"   Name: {profile_match.profile.name}")
            print(f"   URL: {profile_match.profile.profile_url}")
            print(f"   Confidence: {profile_match.confidence:.2f}")
            print(f"   Strategy: {profile_match.discovery_strategy}")
            print(f"   Reasoning: {profile_match.match_reasoning}")
            
            if profile_match.repositories:
                print(f"   Repositories: {len(profile_match.repositories)}")
            if profile_match.languages_used:
                print(f"   Languages: {list(profile_match.languages_used.keys())}")
            if profile_match.frameworks_detected:
                print(f"   Frameworks: {profile_match.frameworks_detected}")
        
        if not github_profiles:
            print("❌ No GitHub profiles found - this indicates an issue with the validation logic")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_github_validation() 