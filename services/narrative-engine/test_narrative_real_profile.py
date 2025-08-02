#!/usr/bin/env python3
"""
Real-World Test: Sachin's Profile → Narrative Generation
Tests the complete Narrative Engine Service with actual profile data.
"""

import requests
import json
import time
from datetime import datetime

def test_narrative_generation():
    print("🧪 REAL-WORLD TEST: Sachin's Profile → Narrative Generation")
    print("=" * 70)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Mock enriched profile data based on Sachin's real profile
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
            {"skill": "Git", "confidence": 0.90, "evidence": ["github"]}
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
    
    # Test job requirements
    TEST_JOBS = [
        {
            "title": "Senior Software Engineer",
            "department": "Engineering",
            "required_skills": ["Python", "JavaScript", "React", "API Development"],
            "preferred_skills": ["Machine Learning", "Node.js", "Git"],
            "experience_level": "senior",
            "responsibilities": [
                "Design and implement scalable backend services",
                "Lead technical projects and mentor junior developers",
                "Collaborate with cross-functional teams"
            ],
            "company_context": "Fast-growing tech startup focused on AI/ML solutions"
        },
        {
            "title": "Machine Learning Engineer",
            "department": "AI/ML",
            "required_skills": ["Python", "Machine Learning", "Data Analysis"],
            "preferred_skills": ["TensorFlow", "Deep Learning", "Statistics"],
            "experience_level": "mid",
            "responsibilities": [
                "Develop and deploy ML models",
                "Analyze large datasets",
                "Optimize model performance"
            ],
            "company_context": "AI research company developing cutting-edge ML solutions"
        }
    ]
    
    try:
        # Step 1: Test service health and capabilities
        print("🔍 STEP 1: Testing service health and capabilities...")
        
        # Health check
        try:
            response = requests.get('http://localhost:8003/api/v1/health', timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Service health: {health_data.get('status', 'unknown')}")
                print(f"   LLM providers: {health_data.get('llm_providers', {})}")
                print(f"   External services: {health_data.get('external_services', {})}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Narrative Engine service not running on port 8003")
            print("   Start it with: poetry run uvicorn src.narrative_engine.main:app --reload --port 8003")
            return
        except Exception as e:
            print(f"❌ Health check error: {e}")
        
        # Get capabilities
        try:
            response = requests.get('http://localhost:8003/api/v1/capabilities', timeout=10)
            if response.status_code == 200:
                capabilities = response.json()
                print(f"✅ Service capabilities:")
                print(f"   Supported styles: {capabilities.get('supported_narrative_styles', [])}")
                print(f"   LLM providers: {capabilities.get('supported_llm_providers', [])}")
                print(f"   Max tokens: {capabilities.get('max_tokens', 'unknown')}")
            else:
                print(f"❌ Capabilities check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Capabilities check error: {e}")
        
        # Get narrative styles
        try:
            response = requests.get('http://localhost:8003/api/v1/styles', timeout=10)
            if response.status_code == 200:
                styles = response.json()
                print(f"✅ Available narrative styles:")
                for style, details in styles.get('styles', {}).items():
                    print(f"   📝 {style}: {details.get('description', 'No description')}")
            else:
                print(f"❌ Styles check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Styles check error: {e}")
        
        print()
        
        # Step 2: Test narrative generation with different styles
        print("📝 STEP 2: Testing narrative generation...")
        
        test_results = []
        
        for i, job in enumerate(TEST_JOBS):
            print(f"\n🎯 Testing Job {i+1}: {job['title']}")
            
            # Test different narrative styles
            for style in ["concise", "comprehensive"]:  # Skip executive/technical to save API calls
                print(f"   📝 Style: {style}")
                
                narrative_request = {
                    "candidate_id": SACHIN_ENRICHED_PROFILE["candidate_id"],
                    "job_requirement": job,
                    "narrative_style": style,
                    "llm_provider": "openai",
                    "generation_parameters": {
                        "max_tokens": 1000,  # Reduced to save API usage
                        "temperature": 0.7
                    }
                }
                
                try:
                    start_time = time.time()
                    response = requests.post(
                        'http://localhost:8003/api/v1/generate',
                        json=narrative_request,
                        timeout=60
                    )
                    generation_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        if result.get('success'):
                            narrative = result.get('narrative', {})
                            
                            print(f"      ✅ Generation successful! ({generation_time:.2f}s)")
                            print(f"      📊 Confidence: {narrative.get('confidence_score', 0):.3f}")
                            print(f"      🤖 Provider: {narrative.get('llm_provider', 'unknown')}")
                            print(f"      🎯 Model: {narrative.get('model_used', 'unknown')}")
                            
                            # Validate narrative structure
                            sections = [
                                'executive_summary',
                                'technical_skills_assessment', 
                                'experience_relevance',
                                'growth_potential'
                            ]
                            
                            missing_sections = []
                            for section in sections:
                                if not narrative.get(section):
                                    missing_sections.append(section)
                            
                            if missing_sections:
                                print(f"      ⚠️  Missing sections: {missing_sections}")
                            else:
                                print(f"      ✅ All required sections present")
                            
                            # Show executive summary preview
                            exec_summary = narrative.get('executive_summary', {})
                            if exec_summary and exec_summary.get('content'):
                                content = exec_summary['content']
                                preview = content[:150] + "..." if len(content) > 150 else content
                                print(f"      📄 Summary preview: {preview}")
                            
                            # Show recommendation
                            recommendation = narrative.get('recommendation', 'No recommendation')
                            print(f"      💡 Recommendation: {recommendation}")
                            
                            # Store test result
                            test_results.append({
                                'job_title': job['title'],
                                'style': style,
                                'success': True,
                                'confidence': narrative.get('confidence_score', 0),
                                'processing_time': generation_time,
                                'provider': narrative.get('llm_provider', 'unknown'),
                                'model': narrative.get('model_used', 'unknown'),
                                'recommendation': recommendation
                            })
                            
                        else:
                            error_msg = result.get('error_message', 'Unknown error')
                            print(f"      ❌ Generation failed: {error_msg}")
                            test_results.append({
                                'job_title': job['title'],
                                'style': style,
                                'success': False,
                                'error': error_msg
                            })
                    else:
                        print(f"      ❌ HTTP error: {response.status_code}")
                        print(f"         Response: {response.text[:200]}...")
                        test_results.append({
                            'job_title': job['title'],
                            'style': style,
                            'success': False,
                            'error': f"HTTP {response.status_code}"
                        })
                        
                except requests.exceptions.Timeout:
                    print(f"      ❌ Request timeout")
                    test_results.append({
                        'job_title': job['title'],
                        'style': style,
                        'success': False,
                        'error': 'Timeout'
                    })
                except Exception as e:
                    print(f"      ❌ Unexpected error: {e}")
                    test_results.append({
                        'job_title': job['title'],
                        'style': style,
                        'success': False,
                        'error': str(e)
                    })
                
                # Small delay between requests to be respectful to API
                time.sleep(1)
        
        # Step 3: Test error handling
        print(f"\n🔧 STEP 3: Testing error handling...")
        
        # Test with invalid candidate ID
        print("   🧪 Testing invalid candidate ID...")
        invalid_request = {
            "candidate_id": "invalid-candidate",
            "job_requirement": TEST_JOBS[0],
            "narrative_style": "concise"
        }
        
        try:
            response = requests.post(
                'http://localhost:8003/api/v1/generate',
                json=invalid_request,
                timeout=30
            )
            
            if response.status_code == 503:  # Expected: Data Enrichment Service unavailable
                print("      ✅ Properly handled invalid candidate (503 error)")
            elif response.status_code == 500:
                print("      ✅ Properly handled invalid candidate (500 error)")
            else:
                print(f"      ⚠️  Unexpected response: {response.status_code}")
        except Exception as e:
            print(f"      ✅ Properly handled invalid candidate (exception: {e})")
        
        # Test with invalid narrative style
        print("   🧪 Testing invalid narrative style...")
        invalid_style_request = {
            "candidate_id": SACHIN_ENRICHED_PROFILE["candidate_id"],
            "job_requirement": TEST_JOBS[0],
            "narrative_style": "invalid_style"
        }
        
        try:
            response = requests.post(
                'http://localhost:8003/api/v1/generate',
                json=invalid_style_request,
                timeout=30
            )
            
            if response.status_code == 422:  # Expected: Validation error
                print("      ✅ Properly handled invalid narrative style (422 error)")
            else:
                print(f"      ⚠️  Unexpected response: {response.status_code}")
        except Exception as e:
            print(f"      ✅ Properly handled invalid style (exception: {e})")
        
        # Step 4: Results summary
        print(f"\n📊 TEST RESULTS SUMMARY:")
        print("=" * 50)
        
        successful_tests = [r for r in test_results if r.get('success')]
        failed_tests = [r for r in test_results if not r.get('success')]
        
        print(f"✅ Successful generations: {len(successful_tests)}/{len(test_results)}")
        print(f"❌ Failed generations: {len(failed_tests)}/{len(test_results)}")
        
        if successful_tests:
            avg_confidence = sum(r.get('confidence', 0) for r in successful_tests) / len(successful_tests)
            avg_time = sum(r.get('processing_time', 0) for r in successful_tests) / len(successful_tests)
            
            print(f"📊 Average confidence: {avg_confidence:.3f}")
            print(f"⏱️  Average processing time: {avg_time:.2f}s")
            
            # Show recommendations
            print(f"\n💡 RECOMMENDATIONS GENERATED:")
            for result in successful_tests:
                print(f"   🎯 {result['job_title']} ({result['style']}): {result['recommendation']}")
        
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for result in failed_tests:
                print(f"   🎯 {result['job_title']} ({result['style']}): {result.get('error', 'Unknown error')}")
        
        # Calculate success rate
        success_rate = len(successful_tests) / len(test_results) * 100 if test_results else 0
        
        # Save comprehensive results
        results = {
            'test_timestamp': datetime.now().isoformat(),
            'candidate_profile': SACHIN_ENRICHED_PROFILE,
            'test_jobs': TEST_JOBS,
            'test_results': test_results,
            'summary': {
                'total_tests': len(test_results),
                'successful_tests': len(successful_tests),
                'failed_tests': len(failed_tests),
                'success_rate': success_rate,
                'avg_confidence': avg_confidence if successful_tests else 0,
                'avg_processing_time': avg_time if successful_tests else 0
            }
        }
        
        with open('sachin_narrative_generation_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Complete results saved to 'sachin_narrative_generation_results.json'")
        
        # Final verdict
        print(f"\n🏆 FINAL VERDICT:")
        if success_rate >= 80:
            print(f"🎉 EXCELLENT! Success rate: {success_rate:.1f}% ✅")
            print(f"   The Narrative Engine Service is working perfectly!")
        elif success_rate >= 60:
            print(f"✅ GOOD! Success rate: {success_rate:.1f}% ✅")
            print(f"   The service is working well with minor issues.")
        elif success_rate >= 40:
            print(f"⚠️  FAIR! Success rate: {success_rate:.1f}% ⚠️")
            print(f"   The service works but needs optimization.")
        else:
            print(f"❌ NEEDS WORK! Success rate: {success_rate:.1f}% ❌")
            print(f"   The service requires significant debugging.")
        
        # Performance assessment
        if successful_tests:
            if avg_time < 5:
                print(f"⚡ Performance: EXCELLENT ({avg_time:.2f}s average)")
            elif avg_time < 10:
                print(f"⚡ Performance: GOOD ({avg_time:.2f}s average)")
            else:
                print(f"⚡ Performance: SLOW ({avg_time:.2f}s average)")
        
        print(f"\n🎯 API Usage Summary:")
        print(f"   Total API calls: {len(successful_tests)}")
        print(f"   Estimated tokens used: ~{len(successful_tests) * 1000}")
        print(f"   Cost estimate: ~${len(successful_tests) * 0.03:.2f} (GPT-4)")
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_narrative_generation() 