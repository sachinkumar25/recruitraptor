#!/usr/bin/env python3
"""Test script for Data Enrichment Service with real data."""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_enrichment.core.models import (
    EnrichmentRequest,
    ExtractedResumeData,
    PersonalInfo,
    ConfidenceField,
    GitHubProfile,
    GitHubProfileMatch,
    GitHubRepository,
    JobContext,
    ExperienceLevel
)
from data_enrichment.services.enrichment_service import EnrichmentService


def load_test_data():
    """Load test data from the profile discovery service."""
    
    # Load resume data from the resume parser output
    resume_file = Path(__file__).parent.parent / "profile-discovery" / "resume_output.json"
    
    if not resume_file.exists():
        print(f"❌ Resume data file not found: {resume_file}")
        return None
    
    try:
        with open(resume_file, 'r') as f:
            resume_data = json.load(f)
        print(f"✅ Loaded resume data from {resume_file}")
        return resume_data
    except Exception as e:
        print(f"❌ Failed to load resume data: {e}")
        return None


def create_test_github_profile():
    """Create a test GitHub profile based on Sachin's real profile."""
    
    # Create GitHub repositories
    repositories = [
        GitHubRepository(
            name="recruitraptor",
            full_name="sachinkumar/recruitraptor",
            description="AI Recruiter Agent - Intelligent recruitment platform",
            language="Python",
            stars=5,
            forks=2,
            created_at="2024-01-15T00:00:00Z",
            updated_at="2024-12-15T00:00:00Z",
            topics=["ai", "recruitment", "python", "fastapi", "machine-learning"],
            is_fork=False,
            is_archived=False
        ),
        GitHubRepository(
            name="data-science-project",
            full_name="sachinkumar/data-science-project",
            description="Machine learning and data analysis projects",
            language="Python",
            stars=3,
            forks=1,
            created_at="2023-06-10T00:00:00Z",
            updated_at="2024-11-20T00:00:00Z",
            topics=["machine-learning", "data-science", "python", "jupyter"],
            is_fork=False,
            is_archived=False
        ),
        GitHubRepository(
            name="web-app",
            full_name="sachinkumar/web-app",
            description="Modern web application with React and Node.js",
            language="JavaScript",
            stars=2,
            forks=0,
            created_at="2023-03-15T00:00:00Z",
            updated_at="2024-10-05T00:00:00Z",
            topics=["react", "nodejs", "javascript", "web-development"],
            is_fork=False,
            is_archived=False
        )
    ]
    
    # Create GitHub profile
    github_profile = GitHubProfile(
        username="sachinkumar",
        name="Sachin Kumar",
        bio="Software Engineer | AI/ML Enthusiast | Open Source Contributor",
        location="San Francisco, CA",
        company="Tech Company",
        email="sachin.kumar@example.com",
        blog="https://sachinkumar.dev",
        public_repos=15,
        public_gists=5,
        followers=25,
        following=30,
        created_at="2020-01-15T00:00:00Z",
        updated_at="2024-12-15T00:00:00Z",
        avatar_url="https://avatars.githubusercontent.com/u/sachinkumar",
        profile_url="https://github.com/sachinkumar"
    )
    
    # Create GitHub profile match
    github_profile_match = GitHubProfileMatch(
        profile=github_profile,
        confidence=0.85,
        match_reasoning="High confidence match based on name, location, and repository analysis",
        repositories=repositories,
        languages_used={
            "Python": 8,
            "JavaScript": 5,
            "TypeScript": 3,
            "HTML": 2,
            "CSS": 2
        },
        frameworks_detected=[
            "FastAPI",
            "React",
            "Node.js",
            "Django",
            "TensorFlow",
            "Pandas"
        ]
    )
    
    return github_profile_match


def convert_resume_data(resume_json):
    """Convert resume JSON data to ExtractedResumeData model."""
    
    try:
        # Extract personal info
        personal_info = PersonalInfo(
            name=ConfidenceField(
                value=resume_json.get("personal_info", {}).get("name", {}).get("value"),
                confidence=resume_json.get("personal_info", {}).get("name", {}).get("confidence", 0.8)
            ),
            email=ConfidenceField(
                value=resume_json.get("personal_info", {}).get("email", {}).get("value"),
                confidence=resume_json.get("personal_info", {}).get("email", {}).get("confidence", 0.9)
            ),
            phone=ConfidenceField(
                value=resume_json.get("personal_info", {}).get("phone", {}).get("value"),
                confidence=resume_json.get("personal_info", {}).get("phone", {}).get("confidence", 0.8)
            ),
            location=ConfidenceField(
                value=resume_json.get("personal_info", {}).get("location", {}).get("value"),
                confidence=resume_json.get("personal_info", {}).get("location", {}).get("confidence", 0.7)
            ),
            linkedin_url=ConfidenceField(
                value=resume_json.get("personal_info", {}).get("linkedin_url", {}).get("value"),
                confidence=resume_json.get("personal_info", {}).get("linkedin_url", {}).get("confidence", 0.6)
            ),
            github_url=ConfidenceField(
                value=resume_json.get("personal_info", {}).get("github_url", {}).get("value"),
                confidence=resume_json.get("personal_info", {}).get("github_url", {}).get("confidence", 0.9)
            ),
            confidence=resume_json.get("personal_info", {}).get("confidence", 0.8)
        )
        
        # Create ExtractedResumeData
        extracted_data = ExtractedResumeData(
            personal_info=personal_info,
            education=resume_json.get("education", {}),
            experience=resume_json.get("experience", {}),
            skills=resume_json.get("skills", {}),
            metadata=resume_json.get("metadata", {})
        )
        
        return extracted_data
        
    except Exception as e:
        print(f"❌ Failed to convert resume data: {e}")
        return None


async def test_enrichment_service():
    """Test the enrichment service with real data."""
    
    print("🚀 Testing Data Enrichment Service with Real Data")
    print("=" * 60)
    
    # Load test data
    resume_json = load_test_data()
    if not resume_json:
        print("❌ Cannot proceed without resume data")
        return
    
    # Convert resume data
    resume_data = convert_resume_data(resume_json)
    if not resume_data:
        print("❌ Failed to convert resume data")
        return
    
    # Create GitHub profile
    github_profile = create_test_github_profile()
    
    # Create job context
    job_context = JobContext(
        required_skills=["Python", "JavaScript", "FastAPI", "React"],
        preferred_skills=["Machine Learning", "Docker", "AWS"],
        experience_level=ExperienceLevel.MID,
        role_type="fullstack",
        industry="technology",
        company_size="startup"
    )
    
    # Create enrichment request
    request = EnrichmentRequest(
        resume_data=resume_data,
        github_profiles=[github_profile],
        linkedin_profiles=[],  # No LinkedIn profiles for this test
        job_context=job_context
    )
    
    print(f"✅ Created enrichment request with:")
    print(f"   - Resume data: {resume_data.personal_info.name.value}")
    print(f"   - GitHub profile: {github_profile.profile.username}")
    print(f"   - Job context: {job_context.role_type} role")
    
    # Initialize enrichment service
    service = EnrichmentService()
    
    print("\n🔄 Processing enrichment request...")
    
    try:
        # Perform enrichment
        response = await service.enrich_candidate_data(request)
        
        if response.success:
            print("✅ Enrichment completed successfully!")
            print(f"   - Processing time: {response.processing_time_ms:.2f}ms")
            print(f"   - Overall confidence: {response.enriched_profile.overall_confidence:.2f}")
            print(f"   - Data sources: {len(response.enriched_profile.data_sources)}")
            
            # Display enriched profile details
            profile = response.enriched_profile
            print(f"\n📋 Enriched Profile Details:")
            print(f"   - Candidate ID: {profile.candidate_id}")
            print(f"   - Name: {profile.personal_info.name}")
            print(f"   - Email: {profile.personal_info.email}")
            print(f"   - Location: {profile.personal_info.location}")
            print(f"   - GitHub: {profile.personal_info.github_url}")
            
            # Display skills analysis
            print(f"\n💻 Skills Analysis:")
            print(f"   - Technical skills: {len(profile.skills.technical_skills)}")
            print(f"   - Programming languages: {list(profile.skills.programming_languages.keys())}")
            print(f"   - Frameworks: {list(profile.skills.frameworks.keys())}")
            print(f"   - Overall confidence: {profile.skills.overall_confidence:.2f}")
            
            # Display GitHub analysis
            print(f"\n🔗 GitHub Analysis:")
            print(f"   - Total repositories: {profile.github_analysis.total_repositories}")
            print(f"   - Total stars: {profile.github_analysis.total_stars}")
            print(f"   - Languages: {list(profile.github_analysis.languages_distribution.keys())}")
            print(f"   - Recent activity score: {profile.github_analysis.recent_activity_score:.2f}")
            
            # Display job relevance
            if profile.job_relevance_score:
                print(f"\n🎯 Job Relevance:")
                print(f"   - Job relevance score: {profile.job_relevance_score:.2f}")
                print(f"   - Skill match percentage: {profile.skill_match_percentage:.2f}")
                print(f"   - Skill gaps: {profile.skills.skill_gaps}")
                print(f"   - Skill strengths: {profile.skills.skill_strengths}")
            
            # Display conflicts resolved
            if response.enrichment_metadata.conflicts_resolved:
                print(f"\n⚖️ Conflicts Resolved:")
                for conflict in response.enrichment_metadata.conflicts_resolved:
                    print(f"   - {conflict.field_name}: {conflict.resolution_strategy.value}")
            
            print(f"\n✅ Test completed successfully!")
            print(f"   - Enrichment version: {response.enrichment_metadata.enrichment_version}")
            print(f"   - Algorithms used: {response.enrichment_metadata.algorithms_used}")
            
        else:
            print(f"❌ Enrichment failed: {response.error_message}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


async def test_validation():
    """Test request validation."""
    
    print("\n🔍 Testing Request Validation")
    print("=" * 40)
    
    service = EnrichmentService()
    
    # Test valid request
    resume_data = ExtractedResumeData(
        personal_info=PersonalInfo(
            name=ConfidenceField(value="Test User"),
            confidence=0.8
        ),
        skills={"technical_skills": ["Python", "JavaScript"]}
    )
    
    github_profile = GitHubProfileMatch(
        profile=GitHubProfile(
            username="testuser",
            profile_url="https://github.com/testuser"
        ),
        confidence=0.8,
        match_reasoning="Test match"
    )
    
    valid_request = EnrichmentRequest(
        resume_data=resume_data,
        github_profiles=[github_profile]
    )
    
    errors = await service.validate_enrichment_request(valid_request)
    print(f"✅ Valid request validation: {len(errors)} errors")
    
    # Test invalid request (empty resume data)
    invalid_request = EnrichmentRequest(
        resume_data=ExtractedResumeData(
            personal_info=PersonalInfo(
                name=ConfidenceField(value=""),  # Empty name
                confidence=0.8
            ),
            skills={}  # Empty skills
        ),
        github_profiles=[github_profile]
    )
    
    errors = await service.validate_enrichment_request(invalid_request)
    print(f"✅ Invalid request validation: {len(errors)} errors")
    for error in errors:
        print(f"   - {error}")


if __name__ == "__main__":
    asyncio.run(test_enrichment_service())
    asyncio.run(test_validation()) 