#!/usr/bin/env python3
"""
Comprehensive test script for Data Enrichment Service.
Tests all endpoints and functionality with realistic data.
"""

import asyncio
import json
import time
from typing import Dict, Any
import aiohttp
import requests


class DataEnrichmentTester:
    """Test suite for Data Enrichment Service."""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def create_sample_resume_data(self) -> Dict[str, Any]:
        """Create sample resume data for testing."""
        return {
            "personal_info": {
                "name": {"value": "John Doe", "confidence": 0.95},
                "email": {"value": "john.doe@email.com", "confidence": 0.90},
                "phone": {"value": "+1-555-123-4567", "confidence": 0.85},
                "location": {"value": "San Francisco, CA", "confidence": 0.80},
                "linkedin_url": {"value": "https://linkedin.com/in/johndoe", "confidence": 0.75},
                "github_url": {"value": "https://github.com/johndoe", "confidence": 0.70},
                "confidence": 0.85
            },
            "education": {
                "institutions": ["Stanford University"],
                "degrees": ["Bachelor of Science in Computer Science"],
                "fields_of_study": ["Computer Science"],
                "dates": ["2018-2022"],
                "gpa": 3.8
            },
            "experience": {
                "companies": ["Tech Corp", "Startup Inc"],
                "positions": ["Senior Software Engineer", "Software Engineer"],
                "dates": ["2022-Present", "2020-2022"],
                "descriptions": [
                    "Led development of microservices architecture",
                    "Built full-stack web applications"
                ],
                "technologies_used": {
                    "Tech Corp": ["Python", "Django", "PostgreSQL", "AWS"],
                    "Startup Inc": ["JavaScript", "React", "Node.js", "MongoDB"]
                }
            },
            "skills": {
                "technical_skills": [
                    "Python", "JavaScript", "React", "Node.js", "Django",
                    "PostgreSQL", "MongoDB", "AWS", "Docker", "Kubernetes"
                ],
                "soft_skills": [
                    "Leadership", "Problem Solving", "Team Collaboration"
                ],
                "categories": {
                    "programming_languages": ["Python", "JavaScript"],
                    "frameworks": ["React", "Node.js", "Django"],
                    "databases": ["PostgreSQL", "MongoDB"],
                    "cloud_platforms": ["AWS"],
                    "tools": ["Docker", "Kubernetes"]
                }
            },
            "metadata": {
                "parsing_confidence": 0.85,
                "source": "resume_parser"
            }
        }
    
    def create_sample_github_profile(self) -> Dict[str, Any]:
        """Create sample GitHub profile data for testing."""
        return {
            "profile": {
                "username": "johndoe",
                "name": "John Doe",
                "bio": "Full-stack developer passionate about building scalable applications",
                "location": "San Francisco, CA",
                "company": "Tech Corp",
                "email": "john.doe@email.com",
                "blog": "https://johndoe.dev",
                "public_repos": 25,
                "public_gists": 10,
                "followers": 150,
                "following": 75,
                "created_at": "2018-01-15T00:00:00Z",
                "updated_at": "2024-01-15T00:00:00Z",
                "avatar_url": "https://avatars.githubusercontent.com/u/12345678",
                "profile_url": "https://github.com/johndoe"
            },
            "confidence": 0.90,
            "match_reasoning": "Email and name match with resume data",
            "repositories": [
                {
                    "name": "awesome-project",
                    "full_name": "johndoe/awesome-project",
                    "description": "A full-stack web application",
                    "language": "Python",
                    "stars": 45,
                    "forks": 12,
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2024-01-15T00:00:00Z",
                    "topics": ["python", "django", "react"],
                    "is_fork": False,
                    "is_archived": False
                },
                {
                    "name": "microservice-api",
                    "full_name": "johndoe/microservice-api",
                    "description": "RESTful API built with FastAPI",
                    "language": "Python",
                    "stars": 23,
                    "forks": 8,
                    "created_at": "2023-06-01T00:00:00Z",
                    "updated_at": "2024-01-10T00:00:00Z",
                    "topics": ["fastapi", "python", "api"],
                    "is_fork": False,
                    "is_archived": False
                }
            ],
            "languages_used": {
                "Python": 60,
                "JavaScript": 25,
                "TypeScript": 10,
                "Go": 5
            },
            "frameworks_detected": ["Django", "FastAPI", "React", "Express"]
        }
    
    def create_sample_linkedin_profile(self) -> Dict[str, Any]:
        """Create sample LinkedIn profile data for testing."""
        return {
            "profile": {
                "profile_url": "https://linkedin.com/in/johndoe",
                "name": "John Doe",
                "headline": "Senior Software Engineer at Tech Corp",
                "location": "San Francisco Bay Area",
                "current_position": "Senior Software Engineer",
                "current_company": "Tech Corp",
                "summary": "Experienced software engineer with 4+ years building scalable applications",
                "experience_count": 3,
                "education_count": 1
            },
            "confidence": 0.85,
            "match_reasoning": "Name and company match with resume data"
        }
    
    def create_sample_job_context(self) -> Dict[str, Any]:
        """Create sample job context for testing."""
        return {
            "required_skills": ["Python", "JavaScript", "React", "PostgreSQL"],
            "preferred_skills": ["Django", "Node.js", "AWS", "Docker"],
            "experience_level": "senior",
            "role_type": "fullstack",
            "industry": "technology",
            "company_size": "mid-size",
            "location_requirements": "San Francisco Bay Area"
        }
    
    async def test_health_check(self) -> bool:
        """Test health check endpoint."""
        print("\n🔍 Testing Health Check...")
        
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health Check: {data['status']}")
                    print(f"   Version: {data['version']}")
                    print(f"   Uptime: {data['uptime_seconds']:.2f} seconds")
                    return True
                else:
                    print(f"❌ Health Check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Health Check error: {e}")
            return False
    
    async def test_root_endpoint(self) -> bool:
        """Test root endpoint."""
        print("\n🔍 Testing Root Endpoint...")
        
        try:
            async with self.session.get(f"{self.base_url}/") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Root Endpoint: {data['service']}")
                    print(f"   Status: {data['status']}")
                    print(f"   Version: {data['version']}")
                    return True
                else:
                    print(f"❌ Root endpoint failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")
            return False
    
    async def test_capabilities(self) -> bool:
        """Test capabilities endpoint."""
        print("\n🔍 Testing Capabilities...")
        
        try:
            async with self.session.get(f"{self.base_url}/api/v1/capabilities") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Capabilities: {data['service_name']}")
                    print(f"   Supported sources: {', '.join(data['supported_data_sources'])}")
                    print(f"   Algorithms: {', '.join(data['supported_algorithms'])}")
                    return True
                else:
                    print(f"❌ Capabilities failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Capabilities error: {e}")
            return False
    
    async def test_configuration(self) -> bool:
        """Test configuration endpoint."""
        print("\n🔍 Testing Configuration...")
        
        try:
            async with self.session.get(f"{self.base_url}/api/v1/config") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Configuration retrieved")
                    print(f"   Min confidence: {data['min_confidence_threshold']}")
                    print(f"   Skill weighting: {data['skill_weighting_factor']}")
                    return True
                else:
                    print(f"❌ Configuration failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Configuration error: {e}")
            return False
    
    async def test_validation(self) -> bool:
        """Test request validation endpoint."""
        print("\n🔍 Testing Request Validation...")
        
        # Create a valid request
        valid_request = {
            "resume_data": self.create_sample_resume_data(),
            "github_profiles": [self.create_sample_github_profile()],
            "linkedin_profiles": [self.create_sample_linkedin_profile()]
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/validate",
                json=valid_request
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Validation: {data['valid']}")
                    print(f"   Error count: {data['error_count']}")
                    return data['valid']
                else:
                    print(f"❌ Validation failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return False
    
    async def test_basic_enrichment(self) -> bool:
        """Test basic enrichment without job context."""
        print("\n🔍 Testing Basic Enrichment...")
        
        request_data = {
            "resume_data": self.create_sample_resume_data(),
            "github_profiles": [self.create_sample_github_profile()],
            "linkedin_profiles": [self.create_sample_linkedin_profile()]
        }
        
        try:
            start_time = time.time()
            async with self.session.post(
                f"{self.base_url}/api/v1/enrich",
                json=request_data
            ) as response:
                processing_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Basic Enrichment successful")
                    print(f"   Processing time: {processing_time:.2f}s")
                    print(f"   Overall confidence: {data['enriched_profile']['overall_confidence']}")
                    print(f"   Data sources: {len(data['enriched_profile']['data_sources'])}")
                    
                    # Print some key insights
                    profile = data['enriched_profile']
                    print(f"   Name: {profile['personal_info']['name']}")
                    print(f"   Skills count: {len(profile['skills']['technical_skills'])}")
                    print(f"   GitHub repos: {profile['github_analysis']['total_repositories']}")
                    
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Basic enrichment failed: {response.status}")
                    print(f"   Error: {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Basic enrichment error: {e}")
            return False
    
    async def test_enrichment_with_job_context(self) -> bool:
        """Test enrichment with job context."""
        print("\n🔍 Testing Enrichment with Job Context...")
        
        request_data = {
            "resume_data": self.create_sample_resume_data(),
            "github_profiles": [self.create_sample_github_profile()],
            "linkedin_profiles": [self.create_sample_linkedin_profile()],
            "job_context": self.create_sample_job_context()
        }
        
        try:
            start_time = time.time()
            async with self.session.post(
                f"{self.base_url}/api/v1/enrich",
                json=request_data
            ) as response:
                processing_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Job Context Enrichment successful")
                    print(f"   Processing time: {processing_time:.2f}s")
                    print(f"   Job relevance: {data['enriched_profile']['job_relevance_score']}")
                    print(f"   Skill match: {data['enriched_profile']['skill_match_percentage']}")
                    
                    # Print skill analysis
                    profile = data['enriched_profile']
                    print(f"   Skill gaps: {len(profile['skills']['skill_gaps'])}")
                    print(f"   Skill strengths: {len(profile['skills']['skill_strengths'])}")
                    
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Job context enrichment failed: {response.status}")
                    print(f"   Error: {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Job context enrichment error: {e}")
            return False
    
    async def test_statistics(self) -> bool:
        """Test statistics endpoint."""
        print("\n🔍 Testing Statistics...")
        
        try:
            async with self.session.get(f"{self.base_url}/api/v1/statistics") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Statistics retrieved")
                    print(f"   Service: {data['service_name']}")
                    print(f"   Version: {data['version']}")
                    print(f"   Success rate: {data['success_rate']}")
                    return True
                else:
                    print(f"❌ Statistics failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Statistics error: {e}")
            return False
    
    async def test_error_handling(self) -> bool:
        """Test error handling with invalid requests."""
        print("\n🔍 Testing Error Handling...")
        
        # Test with missing resume data
        invalid_request = {
            "github_profiles": [self.create_sample_github_profile()]
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/enrich",
                json=invalid_request
            ) as response:
                if response.status == 400:
                    print("✅ Error handling: Correctly rejected invalid request")
                    return True
                else:
                    print(f"❌ Error handling: Expected 400, got {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests and provide summary."""
        print("🚀 Starting Data Enrichment Service Tests")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Root Endpoint", self.test_root_endpoint),
            ("Capabilities", self.test_capabilities),
            ("Configuration", self.test_configuration),
            ("Validation", self.test_validation),
            ("Basic Enrichment", self.test_basic_enrichment),
            ("Job Context Enrichment", self.test_enrichment_with_job_context),
            ("Statistics", self.test_statistics),
            ("Error Handling", self.test_error_handling)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results.append((test_name, False))
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
            if result:
                passed += 1
        
        print(f"\nResults: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Data Enrichment Service is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the service logs for details.")
        
        return passed == total


async def main():
    """Main test runner."""
    print("Data Enrichment Service Test Suite")
    print("Make sure the service is running on http://localhost:8002")
    
    async with DataEnrichmentTester() as tester:
        success = await tester.run_all_tests()
        return success


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1) 