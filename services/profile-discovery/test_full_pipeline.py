#!/usr/bin/env python3
import requests
import json
import time

def test_resume_to_profiles():
    print("�� Testing Full Resume → Profile Discovery Pipeline\n")
    
    # Step 1: Upload resume to Resume Parser (port 8000)
    print("📄 Step 1: Uploading resume to Resume Parser...")
    
    # Create test resume content
    resume_content = """
John Smith
Senior Software Engineer
Email: john.smith@gmail.com
Phone: (555) 123-4567
Location: San Francisco, CA
LinkedIn: https://linkedin.com/in/johnsmith
GitHub: https://github.com/johnsmith

EDUCATION
Stanford University
Bachelor of Science in Computer Science
Graduated: June 2020

EXPERIENCE
Senior Software Engineer | Google | 2022-Present
- Led microservices development with Python and Kubernetes
- Built scalable systems serving 1M+ users

Software Engineer | GitHub | 2020-2022
- Developed React applications and REST APIs
- Technologies: Python, JavaScript, React, Django

SKILLS
Python, JavaScript, React, Django, Kubernetes, AWS, PostgreSQL
"""
    
    # Save test resume
    with open('test_resume_for_discovery.txt', 'w') as f:
        f.write(resume_content)
    
    # Upload to Resume Parser
    try:
        with open('test_resume_for_discovery.txt', 'rb') as f:
            response = requests.post(
                'http://localhost:8000/api/v1/upload',
                files={'file': f},
                timeout=30
            )
        
        if response.status_code == 200:
            parsed_data = response.json()
            print("✅ Resume parsing successful!")
            print(f"   📊 Extracted {len(parsed_data['parsed_data']['skills']['technical_skills'])} technical skills")
            print(f"   📧 Email: {parsed_data['parsed_data']['personal_info']['email']['value']}")
            print(f"   🏢 Companies: {parsed_data['parsed_data']['experience']['companies'][:3]}")
            
            # Step 2: Send to Profile Discovery
            print("\n🔍 Step 2: Discovering profiles...")
            
            discovery_request = {
                "candidate_data": parsed_data["parsed_data"],
                "discovery_options": {
                    "platforms": ["github", "linkedin"],
                    "max_results_per_platform": 3,
                    "strategies": ["email", "name_context"]
                }
            }
            
            response = requests.post(
                'http://localhost:8001/api/v1/discover',
                json=discovery_request,
                timeout=30
            )
            
            if response.status_code == 200:
                discovery_data = response.json()
                print("✅ Profile discovery successful!")
                
                # Display results
                print(f"\n�� DISCOVERY RESULTS:")
                print(f"   🐙 GitHub profiles found: {len(discovery_data.get('github_profiles', []))}")
                print(f"   💼 LinkedIn profiles found: {len(discovery_data.get('linkedin_profiles', []))}")
                print(f"   ⏱️  Processing time: {discovery_data.get('processing_time_ms', 0)}ms")
                
                # Show GitHub profiles
                if discovery_data.get('github_profiles'):
                    print(f"\n🐙 GITHUB PROFILES:")
                    for i, profile in enumerate(discovery_data['github_profiles'][:2]):
                        print(f"   {i+1}. {profile.get('username', 'N/A')}")
                        print(f"      URL: {profile.get('profile_url', 'N/A')}")
                        print(f"      Confidence: {profile.get('confidence_score', 0):.2f}")
                        print(f"      Match reason: {profile.get('match_reasoning', 'N/A')}")
                        
                        if profile.get('repository_analysis'):
                            repo_data = profile['repository_analysis']
                            print(f"      Repositories: {repo_data.get('total_repos', 0)}")
                            if repo_data.get('languages'):
                                top_lang = max(repo_data['languages'].items(), key=lambda x: x[1])
                                print(f"      Top language: {top_lang[0]} ({top_lang[1]:.1f}%)")
                        print()
                
                # Show LinkedIn profiles
                if discovery_data.get('linkedin_profiles'):
                    print(f"💼 LINKEDIN PROFILES:")
                    for i, profile in enumerate(discovery_data['linkedin_profiles'][:2]):
                        print(f"   {i+1}. {profile.get('profile_url', 'N/A')}")
                        print(f"      Confidence: {profile.get('confidence_score', 0):.2f}")
                        print(f"      Match reason: {profile.get('match_reasoning', 'N/A')}")
                        if profile.get('profile_data'):
                            data = profile['profile_data']
                            print(f"      Name: {data.get('name', 'N/A')}")
                            print(f"      Headline: {data.get('headline', 'N/A')}")
                        print()
                
                # Save results
                with open('discovery_results.json', 'w') as f:
                    json.dump(discovery_data, f, indent=2)
                print("💾 Results saved to discovery_results.json")
                
            else:
                print(f"❌ Profile discovery failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        else:
            print(f"❌ Resume parsing failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        if "8000" in str(e):
            print("❌ Resume Parser service not running on port 8000")
            print("   Start it with: cd ../resume-parser && poetry run python -m src.resume_parser.main")
        elif "8001" in str(e):
            print("❌ Profile Discovery service not running on port 8001")
        else:
            print(f"❌ Connection error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_resume_to_profiles()
