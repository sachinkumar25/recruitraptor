#!/usr/bin/env python3
"""Debug test to isolate the list index error."""

import sys
import os
sys.path.append('src')

from profile_discovery.services.discovery_service import DiscoveryService
from profile_discovery.core.models import ExtractedResumeData, PersonalInfo, ConfidenceField, DiscoveryRequest, DiscoveryOptions

def test_discovery_service():
    """Test the discovery service with minimal data."""
    print("🔧 Testing Discovery Service...")
    
    # Create minimal test data
    personal_info = PersonalInfo(
        name=ConfidenceField(value="John Smith", confidence=0.9),
        email=ConfidenceField(value="john.smith@gmail.com", confidence=0.9),
        phone=ConfidenceField(value="(555) 123-4567", confidence=0.8),
        location=ConfidenceField(value="San Francisco, CA", confidence=0.7),
        linkedin_url=ConfidenceField(value="linkedin.com/in/johnsmith", confidence=0.8),
        github_url=ConfidenceField(value="https://github.com/johnsmith", confidence=1.0),
        confidence=0.8
    )
    
    candidate_data = ExtractedResumeData(
        personal_info=personal_info,
        education={},
        experience={},
        skills={}
    )
    
    # Create discovery request
    request = DiscoveryRequest(
        candidate_data=candidate_data,
        discovery_options=DiscoveryOptions(
            search_github=True,
            search_linkedin=True,
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
        print(f"✅ Candidate info extracted: {candidate_info}")
        
        # Test GitHub username extraction
        username = service._extract_github_username(candidate_info['github_url'])
        print(f"✅ GitHub username extracted: {username}")
        
        # Test LinkedIn URL normalization
        linkedin_url = service._normalize_linkedin_url(candidate_info['linkedin_url'])
        print(f"✅ LinkedIn URL normalized: {linkedin_url}")
        
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_discovery_service() 