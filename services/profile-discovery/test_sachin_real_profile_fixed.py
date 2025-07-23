#!/usr/bin/env python3
"""
Real-World Test: Sachin's Resume → Profile Discovery (Fixed)
Tests the complete AI Recruiter Agent pipeline with actual resume and profiles.
"""

import requests
import json
import time
from datetime import datetime

def safe_get_value(data_dict, default='Not found'):
    """Safely get value from nested dict structure."""
    if isinstance(data_dict, dict) and 'value' in data_dict:
        return data_dict['value'] or default
    return default

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
            
            # Extract and validate personal info safely
            personal_info = parsed_data['parsed_data']['personal_info']
            
            print(f"\n📊 EXTRACTED PERSONAL INFORMATION:")
            
            # Name check
            name_extracted = safe_get_value(personal_info.get('name', {}))
            print(f"   👤 Name: {name_extracted}")
            print(f"      Expected: {EXPECTED_RESULTS['name']}")
            name_match = 'sachin' in name_extracted.lower() if name_extracted != 'Not found' else False
            print(f"      Match: {'✅' if name_match else '❌'}")
            
            # Email check
            email_extracted = safe_get_value(personal_info.get('email', {}))
            print(f"   📧 Email: {email_extracted}")
            print(f"      Expected: {EXPECTED_RESULTS['email']}")
            email_match = EXPECTED_RESULTS['email'] in email_extracted if email_extracted != 'Not found' else False
            print(f"      Match: {'✅' if email_match else '❌'}")
            
            # Phone check
            phone_extracted = safe_get_value(personal_info.get('phone', {}))
            print(f"   📱 Phone: {phone_extracted}")
            print(f"      Expected: {EXPECTED_RESULTS['phone']}")
            phone_match = EXPECTED_RESULTS['phone'] in phone_extracted if phone_extracted != 'Not found' else False
            print(f"      Match: {'✅' if phone_match else '❌'}")
            
            # GitHub check
            github_extracted = safe_get_value(personal_info.get('github_url', {}))
            print(f"   🐙 GitHub: {github_extracted}")
            print(f"      Expected: {EXPECTED_RESULTS['github']}")
            github_match = 'sachinkumar25' in github_extracted if github_extracted != 'Not found' else False
            print(f"      Match: {'✅' if github_match else '❌'}")
            
            # LinkedIn check
            linkedin_extracted = safe_get_value(personal_info.get('linkedin_url', {}))
            print(f"   💼 LinkedIn: {linkedin_extracted}")
            print(f"      Expected: {EXPECTED_RESULTS['linkedin']}")
            linkedin_match = 'sashvad-satishkumar' in linkedin_extracted if linkedin_extracted != 'Not found' else False
            print(f"      Match: {'✅' if linkedin_match else '❌'}")
            
            # Show additional extracted data
            education = parsed_data['parsed_data']['education']
            experience = parsed_data['parsed_data']['experience']
            skills = parsed_data['parsed_data']['skills']
            
            print(f"\n📚 EDUCATION:")
            institutions = education.get('institutions', [])
            print(f"   🏫 Institution: {institutions[0] if institutions else 'Not found'}")
            gpa_data = education.get('gpa', {})
            gpa_value = gpa_data.get('value', 'Not found') if isinstance(gpa_data, dict) else 'Not found'
            print(f"   🎓 GPA: {gpa_value}")
            
            print(f"\n💼 EXPERIENCE:")
            companies = experience.get('companies', [])[:3]
            print(f"   🏢 Companies: {', '.join(companies) if companies else 'Not found'}")
            
            print(f"\n💻 TECHNICAL SKILLS:")
            tech_skills = skills.get('technical_skills', [])[:10]
            print(f"   🛠️  Top Skills: {', '.join(tech_skills) if tech_skills else 'Not found'}")
            
            # Debug: Show raw personal_info structure
            print(f"\n🔍 DEBUG - Raw personal_info structure:")
            for key, value in personal_info.items():
                print(f"   {key}: {value}")
            
            # Only proceed to discovery if we have some basic info
            if email_extracted != 'Not found' or github_extracted != 'Not found':
                print(f"\n🔍 STEP 2: Proceeding with profile discovery...")
                
                discovery_request = {
                    "candidate_data": parsed_data["parsed_data"],
                    "discovery_options": {
                        "platforms": ["github", "linkedin"],
                        "max_results_per_platform": 3
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
                    
                    github_profiles = discovery_data.get('github_profiles', [])
                    linkedin_profiles = discovery_data.get('linkedin_profiles', [])
                    
                    print(f"\n🎯 DISCOVERY RESULTS:")
                    print(f"   🐙 GitHub profiles found: {len(github_profiles)}")
                    print(f"   💼 LinkedIn profiles found: {len(linkedin_profiles)}")
                    
                    # Show top results
                    for i, profile in enumerate(github_profiles[:3]):
                        print(f"   GitHub {i+1}: {profile.get('username', 'N/A')} (conf: {profile.get('confidence_score', 0):.2f})")
                    
                    for i, profile in enumerate(linkedin_profiles[:3]):
                        print(f"   LinkedIn {i+1}: {profile.get('profile_url', 'N/A')} (conf: {profile.get('confidence_score', 0):.2f})")
                        
                else:
                    print(f"❌ Profile discovery failed: {response.status_code}")
                    print(f"   Error: {response.text}")
            else:
                print(f"\n⚠️  Skipping profile discovery - insufficient personal info extracted")
                
        else:
            print(f"❌ Resume parsing failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_sachin_profile_discovery()
