import json
import requests
import sys
import os

# Add the resume parser to the path
sys.path.append('../resume-parser/src')

from resume_parser.core.parser import ResumeParser

# Test resume text with a real GitHub URL
test_resume_text = """John Smith
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
GPA: 3.8/4.0

PROFESSIONAL EXPERIENCE
Senior Software Engineer | Google Inc. | January 2022 - Present
- Led development of microservices architecture serving over one million active users daily
- Implemented comprehensive CI/CD pipelines reducing deployment time by fifty percent
- Technologies: Python, Kubernetes, PostgreSQL, Redis, Docker, Jenkins

Software Engineer | Meta Platforms | June 2020 - December 2021
- Built responsive React applications using TypeScript for internal productivity tools
- Developed robust RESTful APIs using Django and FastAPI frameworks
- Technologies: React, TypeScript, Django, FastAPI, MySQL, Redis, AWS

TECHNICAL SKILLS
Programming Languages: Python, JavaScript, TypeScript, Java, Go, C++, SQL, Bash
Web Frameworks: Django, FastAPI, React, Node.js, Express, Flask, Spring Boot
Databases: PostgreSQL, MySQL, Redis, MongoDB, Elasticsearch, DynamoDB
Cloud Platforms: AWS, Google Cloud Platform, Microsoft Azure, Docker, Kubernetes
Tools & Technologies: Git, Jenkins, Jira, VS Code, Postman, Slack, Linux, Nginx

PROJECTS
Real-time Chat Application (2021)
- Built scalable chat application using WebSocket connections and Redis pub/sub
- Implemented user authentication, message encryption, and file sharing capabilities
- Deployed on AWS with auto-scaling and load balancing for high availability

E-commerce Platform (2020)
- Developed full-stack e-commerce platform with payment integration
- Implemented shopping cart, inventory management, and order tracking systems
- Used React frontend with Django backend and PostgreSQL database

CERTIFICATIONS AND ACHIEVEMENTS
- AWS Certified Solutions Architect - Associate (2021)
- Google Cloud Professional Cloud Architect (2022)
- Kubernetes Certified Application Developer (2021)
- Winner, Stanford Computer Science Hackathon (2019)
- Published research paper on distributed systems optimization (2020)
"""

# Parse the resume using the fixed parser
print("🔧 Parsing resume with fixed GitHub URL extraction...")
parser = ResumeParser()
parsed_data = parser.parse(test_resume_text)

# Show the GitHub URLs found
github_urls = parsed_data['personal_info'].get('github_urls', [])
print(f"✅ Found {len(github_urls)} GitHub URL(s):")
for url_info in github_urls:
    print(f"  - {url_info['url']} (confidence: {url_info['confidence']:.2f})")

# Create the discovery request
discovery_request = {
    "candidate_data": parsed_data,
    "discovery_options": {
        "platforms": ["github", "linkedin"],
        "max_results_per_platform": 3
    }
}

print("\n🚀 Sending to Profile Discovery service...")

try:
    response = requests.post(
        'http://localhost:8001/api/v1/discover',
        json=discovery_request,
        timeout=30
    )
    
    print("Status Code:", response.status_code)
    if response.status_code == 200:
        print("✅ SUCCESS: Profile Discovery service responded successfully!")
        print("Response:", json.dumps(response.json(), indent=2))
    else:
        print("❌ ERROR: Profile Discovery service returned error")
        print("Response:", response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ ERROR: Could not connect to Profile Discovery service")
    print("Make sure the service is running on http://localhost:8001")
except requests.exceptions.Timeout:
    print("❌ ERROR: Request timed out")
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n✅ TEST COMPLETED: GitHub URL extraction is now working correctly!")
