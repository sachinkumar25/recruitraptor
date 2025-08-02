#!/usr/bin/env python3
"""Test script for Narrative Engine Service."""

import asyncio
import json
from src.narrative_engine.core.models import (
    NarrativeGenerationRequest, JobRequirement, NarrativeStyle, LLMProvider
)
from src.narrative_engine.services.narrative_service import narrative_service


async def test_narrative_generation():
    """Test narrative generation with mock data."""
    
    print("🧪 Testing Narrative Engine Service...")
    
    # Mock enriched profile data
    enriched_profile_data = {
        "candidate_id": "test-candidate-123",
        "name": "Sachin Kumar",
        "email": "sachin.kumar@example.com",
        "location": "San Francisco, CA",
        "github_url": "https://github.com/sachinkumar",
        "technical_skills": [
            {"skill": "Python", "confidence": 0.9, "evidence": ["resume", "github"]},
            {"skill": "JavaScript", "confidence": 0.8, "evidence": ["resume"]},
            {"skill": "React", "confidence": 0.7, "evidence": ["github"]}
        ],
        "programming_languages": ["Python", "JavaScript", "TypeScript"],
        "frameworks": ["React", "FastAPI", "Django"],
        "experience_years": 5.0,
        "github_analysis": {
            "total_repositories": 15,
            "total_stars": 45,
            "languages": ["Python", "JavaScript", "TypeScript"],
            "recent_activity_score": 0.85
        },
        "job_relevance_score": 0.78,
        "skill_match_percentage": 0.75,
        "skill_gaps": ["Kubernetes", "AWS"],
        "skill_strengths": ["Python", "React", "API Development"]
    }
    
    # Mock job requirement
    job_requirement = JobRequirement(
        title="Senior Software Engineer",
        department="Engineering",
        required_skills=["Python", "JavaScript", "React", "API Development"],
        preferred_skills=["TypeScript", "Docker", "AWS"],
        experience_level="senior",
        responsibilities=[
            "Design and implement scalable backend services",
            "Lead technical projects and mentor junior developers",
            "Collaborate with cross-functional teams"
        ],
        company_context="Fast-growing tech startup focused on AI/ML solutions"
    )
    
    # Test request
    request = NarrativeGenerationRequest(
        candidate_id="test-candidate-123",
        job_requirement=job_requirement,
        narrative_style=NarrativeStyle.COMPREHENSIVE,
        llm_provider=LLMProvider.OPENAI,
        generation_parameters={
            "max_tokens": 1500,
            "temperature": 0.7
        }
    )
    
    try:
        # Import the EnrichedProfile model
        from src.narrative_engine.core.models import EnrichedProfile
        enriched_profile = EnrichedProfile(**enriched_profile_data)
        
        print("✅ Mock data created successfully")
        print(f"📋 Candidate: {enriched_profile.name}")
        print(f"🎯 Job: {job_requirement.title}")
        print(f"📝 Style: {request.narrative_style.value}")
        
        # Test prompt building (without actual LLM call)
        print("\n🔧 Testing prompt building...")
        prompt = narrative_service._build_narrative_prompt(
            enriched_profile=enriched_profile,
            job_requirement=job_requirement,
            narrative_style=request.narrative_style
        )
        
        print(f"📏 Prompt length: {len(prompt)} characters")
        print("📄 Prompt preview:")
        print("-" * 50)
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        print("-" * 50)
        
        print("\n✅ Prompt building test passed!")
        
        # Test service initialization
        print("\n🔧 Testing service initialization...")
        from src.narrative_engine.services.llm_service import llm_service
        available_providers = llm_service.get_available_providers()
        print(f"🤖 Available LLM providers: {available_providers}")
        
        print("\n✅ Service initialization test passed!")
        
        print("\n🎉 All tests passed! Narrative Engine Service is ready.")
        print("\n📋 Next steps:")
        print("1. Set up your OpenAI API key in .env file")
        print("2. Run: poetry run uvicorn src.narrative_engine.main:app --reload --port 8003")
        print("3. Visit: http://localhost:8003/docs for API documentation")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_narrative_generation()) 