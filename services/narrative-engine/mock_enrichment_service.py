#!/usr/bin/env python3
"""
Mock Data Enrichment Service for testing Narrative Engine Service.
This simulates the Data Enrichment Service responses without needing the actual service running.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

app = FastAPI(title="Mock Data Enrichment Service", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock enriched profile data
SACHIN_ENRICHED_PROFILE = {
    "candidate_id": "sachin-kumar-2024",
    "name": "Sashvad (Sachin) Satishkumar",
    "email": "sskumar@umd.edu",
    "location": "College Park, MD",
    "github_url": "https://github.com/sachinkumar25",
    "technical_skills": [
        {"skill": "Python", "confidence": 0.95, "evidence": ["resume", "github"]},
        {"skill": "JavaScript", "confidence": 0.88, "evidence": ["resume", "github"]},
        {"skill": "React", "confidence": 0.82, "evidence": ["github"]},
        {"skill": "Node.js", "confidence": 0.85, "evidence": ["resume", "github"]},
        {"skill": "Machine Learning", "confidence": 0.78, "evidence": ["resume"]},
        {"skill": "Data Analysis", "confidence": 0.80, "evidence": ["resume"]},
        {"skill": "API Development", "confidence": 0.83, "evidence": ["github"]},
        {"skill": "Git", "confidence": 0.90, "evidence": ["github"]},
        {"skill": "TypeScript", "confidence": 0.75, "evidence": ["github"]},
        {"skill": "Java", "confidence": 0.70, "evidence": ["resume"]}
    ],
    "programming_languages": ["Python", "JavaScript", "TypeScript", "Java", "SQL"],
    "frameworks": ["React", "Node.js", "Express", "Django", "TensorFlow"],
    "experience_years": 3.5,
    "github_analysis": {
        "total_repositories": 25,
        "total_stars": 67,
        "languages": ["Python", "JavaScript", "TypeScript", "Java"],
        "recent_activity_score": 0.92,
        "top_repositories": [
            {"name": "ai-recruiter-agent", "stars": 15, "language": "Python"},
            {"name": "ml-project", "stars": 12, "language": "Python"},
            {"name": "web-app", "stars": 8, "language": "JavaScript"}
        ]
    },
    "job_relevance_score": 0.85,
    "skill_match_percentage": 0.82,
    "skill_gaps": ["Kubernetes", "AWS", "Docker"],
    "skill_strengths": ["Python", "Machine Learning", "API Development", "React"]
}

# Mock profiles database
MOCK_PROFILES = {
    "sachin-kumar-2024": SACHIN_ENRICHED_PROFILE,
    "test-candidate-123": {
        "candidate_id": "test-candidate-123",
        "name": "Test Candidate",
        "email": "test@example.com",
        "location": "San Francisco, CA",
        "github_url": "https://github.com/testuser",
        "technical_skills": [
            {"skill": "Python", "confidence": 0.8, "evidence": ["resume"]},
            {"skill": "JavaScript", "confidence": 0.7, "evidence": ["resume"]}
        ],
        "programming_languages": ["Python", "JavaScript"],
        "frameworks": ["React", "Django"],
        "experience_years": 2.0,
        "github_analysis": {
            "total_repositories": 10,
            "total_stars": 20,
            "languages": ["Python", "JavaScript"],
            "recent_activity_score": 0.75
        },
        "job_relevance_score": 0.65,
        "skill_match_percentage": 0.60,
        "skill_gaps": ["AWS", "Docker"],
        "skill_strengths": ["Python", "JavaScript"]
    }
}

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Mock Data Enrichment Service",
        "version": "0.1.0",
        "status": "running",
        "description": "Mock service for testing Narrative Engine Service"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Mock Data Enrichment Service",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/profiles/{candidate_id}")
async def get_profile(candidate_id: str):
    """Get enriched profile by candidate ID."""
    if candidate_id in MOCK_PROFILES:
        return MOCK_PROFILES[candidate_id]
    else:
        raise HTTPException(status_code=404, detail=f"Profile not found for candidate ID: {candidate_id}")

@app.get("/api/v1/capabilities")
async def get_capabilities():
    """Get service capabilities."""
    return {
        "service": "Mock Data Enrichment Service",
        "version": "0.1.0",
        "capabilities": [
            "profile_enrichment",
            "skill_analysis",
            "github_integration"
        ],
        "available_profiles": list(MOCK_PROFILES.keys())
    }

if __name__ == "__main__":
    print("🚀 Starting Mock Data Enrichment Service on port 8002...")
    print("   This simulates the Data Enrichment Service for testing.")
    print("   Available profiles:", list(MOCK_PROFILES.keys()))
    uvicorn.run(app, host="0.0.0.0", port=8002) 