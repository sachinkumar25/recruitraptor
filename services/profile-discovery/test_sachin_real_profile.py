#!/usr/bin/env python3
"""
Real-World Test: Sachin's Resume → Profile Discovery
Tests the complete AI Recruiter Agent pipeline with actual resume and profiles.
"""

import requests
import json
import time
from datetime import datetime

def test_sachin_profile_discovery():
    print("🧪 REAL-WORLD TEST: Sachin's Resume → Profile Discovery Pipeline")
    print("=" * 70)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Expected results for validation
    EXPECTED_RESULTS = {
        'name': 'Sashvad (Sachin) Satishkumar',
        'email': 'sskumar@umd.edu',
        'github': 'github.com/sachinkumar25',
        'linkedin': 'linkedin.com/in/sashvad-satishkumar',
        'phone': '571-236-6612'
    }
    
    try:
        # Step 1: Upload Sachin's real resume
        print("📄 STEP 1: Processing Sachin's actual resume...")
        
        with open('sachin_real_resume.txt', 'rb') as f:
            start_time = time.time()
            response = requests.post(
                'http://localhost:8000/api/v1/upload',
                files={'file': f},
                timeout=30
            )
            parse_time = time.time() - start_time
        
        if response.status_code == 200:
            parsed_data = response.json()
            print(f"✅ Resume parsing successful! ({parse_time:.2f}s)")
            
            # Extract and validate personal info
            personal_info = parsed_data['parsed_data']['personal_info']
            
            print(f"\n📊 EXTRACTED PERSONAL INFORMATION:")
            print(f"   👤 Name: {personal_info.get('name', {}).get('value', 'Not found')}")
            print(f"      Expected: {EXPECTED_RESULTS['name']}")
            print(f"      Match: {'✅' if EXPECTED_RESULTS['name'].lower() in personal_info.get('name', {}).get('value', '').lower() else '❌'}")
            
            print(f"   📧 Email: {personal_info.get('email', {}).get('value', 'Not found')}")
            print(f"      Expected: {EXPECTED_RESULTS['email']}")
            print(f"      Match: {'✅' if EXPECTED_RESULTS['email'] in personal_info.get('email', {}).get('value', '') else '❌'}")
            
            print(f"   📱 Phone: {personal_info.get('phone', {}).get('value', 'Not found')}")
            print(f"      Expected: {EXPECTED_RESULTS['phone']}")
            print(f"      Match: {'✅' if EXPECTED_RESULTS['phone'] in personal_info.get('phone', {}).get('value', '') else '❌'}")
            
            print(f"   🐙 GitHub: {personal_info.get('github_url', {}).get('value', 'Not found')}")
            print(f"      Expected: {EXPECTED_RESULTS['github']}")
            print(f"      Match: {'✅' if 'sachinkumar25' in personal_info.get('github_url', {}).get('value', '') else '❌'}")
            
            print(f"   💼 LinkedIn: {personal_info.get('linkedin_url', {}).get('value', 'Not found')}")
            print(f"      Expected: {EXPECTED_RESULTS['linkedin']}")
            print(f"      Match: {'✅' if 'sashvad-satishkumar' in personal_info.get('linkedin_url', {}).get('value', '') else '❌'}")
            
            # Show education and experience
            education = parsed_data['parsed_data']['education']
            experience = parsed_data['parsed_data']['experience']
            skills = parsed_data['parsed_data']['skills']
            
            print(f"\n📚 EDUCATION:")
            print(f"   🏫 Institution: {education.get('institutions', ['Not found'])[0] if education.get('institutions') else 'Not found'}")
            print(f"   🎓 GPA: {education.get('gpa', {}).get('value', 'Not found')}")
            
            print(f"\n💼 EXPERIENCE:")
            companies = experience.get('companies', [])[:3]
            print(f"   🏢 Companies: {', '.join(companies) if companies else 'Not found'}")
            
            print(f"\n💻 TECHNICAL SKILLS:")
            tech_skills = skills.get('technical_skills', [])[:10]
            print(f"   🛠️  Top Skills: {', '.join(tech_skills) if tech_skills else 'Not found'}")
            
            # Step 2: Profile Discovery
            print(f"\n🔍 STEP 2: Discovering Sachin's real profiles...")
            
            discovery_request = {
                "candidate_data": parsed_data["parsed_data"],
                "discovery_options": {
                    "platforms": ["github", "linkedin"],
                    "max_results_per_platform": 5,
                    "strategies": ["email", "name_context", "fuzzy_match"]
                }
            }
            
            start_time = time.time()
            response = requests.post(
                'http://localhost:8001/api/v1/discover',
                json=discovery_request,
                timeout=60
            )
            discovery_time = time.time() - start_time
            
            if response.status_code == 200:
                discovery_data = response.json()
                print(f"✅ Profile discovery completed! ({discovery_time:.2f}s)")
                
                print(f"\n🎯 DISCOVERY RESULTS:")
                print(f"   ⏱️  Total processing time: {discovery_time:.2f}s")
                print(f"   ✅ Discovery success: {discovery_data.get('success', False)}")
                
                # Analyze GitHub Results
                github_profiles = discovery_data.get('github_profiles', [])
                print(f"\n🐙 GITHUB PROFILES DISCOVERED: {len(github_profiles)}")
                
                sachin_github_found = False
                for i, profile in enumerate(github_profiles[:5]):
                    username = profile.get('username', 'N/A')
                    url = profile.get('profile_url', 'N/A')
                    confidence = profile.get('confidence_score', 0)
                    reason = profile.get('match_reasoning', 'N/A')
                    
                    is_sachin = 'sachinkumar25' in username.lower()
                    if is_sachin:
                        sachin_github_found = True
                    
                    print(f"   {i+1}. {'🎯' if is_sachin else '📍'} Username: {username}")
                    print(f"      URL: {url}")
                    print(f"      Confidence: {confidence:.3f}")
                    print(f"      Match reason: {reason}")
                    
                    # Repository analysis
                    if profile.get('repository_analysis'):
                        repo_data = profile['repository_analysis']
                        total_repos = repo_data.get('total_repos', 0)
                        print(f"      📊 Total repositories: {total_repos}")
                        
                        if repo_data.get('languages'):
                            langs = repo_data['languages']
                            top_3_langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)[:3]
                            lang_str = ", ".join([f"{lang}({pct:.1f}%)" for lang, pct in top_3_langs])
                            print(f"      💻 Top languages: {lang_str}")
                        
                        if repo_data.get('frameworks'):
                            frameworks = repo_data['frameworks'][:5]
                            print(f"      🔧 Frameworks: {', '.join(frameworks)}")
                    print()
                
                # Analyze LinkedIn Results
                linkedin_profiles = discovery_data.get('linkedin_profiles', [])
                print(f"💼 LINKEDIN PROFILES DISCOVERED: {len(linkedin_profiles)}")
                
                sachin_linkedin_found = False
                for i, profile in enumerate(linkedin_profiles[:5]):
                    url = profile.get('profile_url', 'N/A')
                    confidence = profile.get('confidence_score', 0)
                    reason = profile.get('match_reasoning', 'N/A')
                    
                    is_sachin = 'sashvad' in url.lower() or 'satishkumar' in url.lower()
                    if is_sachin:
                        sachin_linkedin_found = True
                    
                    print(f"   {i+1}. {'🎯' if is_sachin else '📍'} URL: {url}")
                    print(f"      Confidence: {confidence:.3f}")
                    print(f"      Match reason: {reason}")
                    
                    if profile.get('profile_data'):
                        data = profile['profile_data']
                        print(f"      👤 Name: {data.get('name', 'N/A')}")
                        print(f"      💼 Headline: {data.get('headline', 'N/A')}")
                        print(f"      📍 Location: {data.get('location', 'N/A')}")
                    print()
                
                # Final Validation Summary
                print(f"🏆 FINAL VALIDATION RESULTS:")
                print(f"   👤 Name extraction: {'✅' if 'sachin' in personal_info.get('name', {}).get('value', '').lower() else '❌'}")
                print(f"   📧 Email extraction: {'✅' if 'sskumar@umd.edu' in personal_info.get('email', {}).get('value', '') else '❌'}")
                print(f"   🐙 GitHub discovery: {'✅' if sachin_github_found else '❌'}")
                print(f"   💼 LinkedIn discovery: {'✅' if sachin_linkedin_found else '❌'}")
                
                success_rate = sum([
                    'sachin' in personal_info.get('name', {}).get('value', '').lower(),
                    'sskumar@umd.edu' in personal_info.get('email', {}).get('value', ''),
                    sachin_github_found,
                    sachin_linkedin_found
                ]) / 4 * 100
                
                print(f"   📊 Overall success rate: {success_rate:.1f}%")
                
                # Performance metrics
                total_time = parse_time + discovery_time
                print(f"\n⚡ PERFORMANCE METRICS:")
                print(f"   📄 Resume parsing time: {parse_time:.2f}s")
                print(f"   🔍 Profile discovery time: {discovery_time:.2f}s")
                print(f"   🎯 Total pipeline time: {total_time:.2f}s")
                print(f"   🎯 Target: <45s {'✅' if total_time < 45 else '❌'}")
                
                # Save comprehensive results
                results = {
                    'test_timestamp': datetime.now().isoformat(),
                    'expected_results': EXPECTED_RESULTS,
                    'parsed_resume': parsed_data,
                    'discovery_results': discovery_data,
                    'validation': {
                        'name_extracted': 'sachin' in personal_info.get('name', {}).get('value', '').lower(),
                        'email_extracted': 'sskumar@umd.edu' in personal_info.get('email', {}).get('value', ''),
                        'github_found': sachin_github_found,
                        'linkedin_found': sachin_linkedin_found,
                        'success_rate': success_rate
                    },
                    'performance': {
                        'parse_time_seconds': parse_time,
                        'discovery_time_seconds': discovery_time,
                        'total_time_seconds': total_time
                    }
                }
                
                with open('sachin_profile_discovery_results.json', 'w') as f:
                    json.dump(results, f, indent=2)
                
                print(f"\n💾 Complete results saved to 'sachin_profile_discovery_results.json'")
                
                # Final verdict
                if success_rate >= 75 and total_time < 45:
                    print(f"\n🎉 TEST VERDICT: SUCCESS! ✅")
                    print(f"   The AI Recruiter Agent successfully processed Sachin's resume and found his profiles!")
                elif success_rate >= 50:
                    print(f"\n⚠️  TEST VERDICT: PARTIAL SUCCESS ⚠️")
                    print(f"   The system works but needs optimization for better accuracy.")
                else:
                    print(f"\n❌ TEST VERDICT: NEEDS IMPROVEMENT ❌")
                    print(f"   The system requires debugging and optimization.")
                
            else:
                print(f"❌ Profile discovery failed: {response.status_code}")
                print(f"   Error details: {response.text}")
                
        else:
            print(f"❌ Resume parsing failed: {response.status_code}")
            print(f"   Error details: {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        if "8000" in str(e):
            print("❌ Resume Parser service not running on port 8000")
            print("   Start it with: cd services/resume-parser && poetry run python -m src.resume_parser.main")
        elif "8001" in str(e):
            print("❌ Profile Discovery service not running on port 8001")
            print("   Start it with: cd services/profile-discovery && PYTHONPATH=src poetry run python -m profile_discovery.main")
        else:
            print(f"❌ Connection error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_sachin_profile_discovery()