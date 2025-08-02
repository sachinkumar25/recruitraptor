#!/bin/bash

# Data Enrichment Service Test Script
# Tests all endpoints using curl commands

BASE_URL="http://localhost:8002"
API_PREFIX="/api/v1"

echo "🚀 Data Enrichment Service - Curl Tests"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Test 1: Health Check
echo -e "\n${YELLOW}1. Testing Health Check...${NC}"
curl -s -o /tmp/health.json "$BASE_URL/health"
if [ $? -eq 0 ]; then
    echo "Response:"
    cat /tmp/health.json | jq '.' 2>/dev/null || cat /tmp/health.json
    print_status 0 "Health check successful"
else
    print_status 1 "Health check failed"
fi

# Test 2: Root Endpoint
echo -e "\n${YELLOW}2. Testing Root Endpoint...${NC}"
curl -s -o /tmp/root.json "$BASE_URL/"
if [ $? -eq 0 ]; then
    echo "Response:"
    cat /tmp/root.json | jq '.' 2>/dev/null || cat /tmp/root.json
    print_status 0 "Root endpoint successful"
else
    print_status 1 "Root endpoint failed"
fi

# Test 3: Capabilities
echo -e "\n${YELLOW}3. Testing Capabilities...${NC}"
curl -s -o /tmp/capabilities.json "$BASE_URL$API_PREFIX/capabilities"
if [ $? -eq 0 ]; then
    echo "Response:"
    cat /tmp/capabilities.json | jq '.' 2>/dev/null || cat /tmp/capabilities.json
    print_status 0 "Capabilities successful"
else
    print_status 1 "Capabilities failed"
fi

# Test 4: Configuration
echo -e "\n${YELLOW}4. Testing Configuration...${NC}"
curl -s -o /tmp/config.json "$BASE_URL$API_PREFIX/config"
if [ $? -eq 0 ]; then
    echo "Response:"
    cat /tmp/config.json | jq '.' 2>/dev/null || cat /tmp/config.json
    print_status 0 "Configuration successful"
else
    print_status 1 "Configuration failed"
fi

# Test 5: Statistics
echo -e "\n${YELLOW}5. Testing Statistics...${NC}"
curl -s -o /tmp/stats.json "$BASE_URL$API_PREFIX/statistics"
if [ $? -eq 0 ]; then
    echo "Response:"
    cat /tmp/stats.json | jq '.' 2>/dev/null || cat /tmp/stats.json
    print_status 0 "Statistics successful"
else
    print_status 1 "Statistics failed"
fi

# Test 6: Basic Enrichment
echo -e "\n${YELLOW}6. Testing Basic Enrichment...${NC}"

# Create sample request data
cat > /tmp/enrichment_request.json << 'EOF'
{
  "resume_data": {
    "personal_info": {
      "name": {"value": "John Doe", "confidence": 0.95},
      "email": {"value": "john.doe@email.com", "confidence": 0.90},
      "phone": {"value": "+1-555-123-4567", "confidence": 0.85},
      "location": {"value": "San Francisco, CA", "confidence": 0.80},
      "confidence": 0.85
    },
    "skills": {
      "technical_skills": ["Python", "JavaScript", "React", "Node.js"],
      "categories": {
        "programming_languages": ["Python", "JavaScript"],
        "frameworks": ["React", "Node.js"]
      }
    }
  },
  "github_profiles": [{
    "profile": {
      "username": "johndoe",
      "name": "John Doe",
      "bio": "Full-stack developer",
      "location": "San Francisco, CA",
      "public_repos": 25,
      "profile_url": "https://github.com/johndoe"
    },
    "confidence": 0.90,
    "match_reasoning": "Name and location match",
    "repositories": [{
      "name": "awesome-project",
      "language": "Python",
      "stars": 45,
      "topics": ["python", "django"]
    }],
    "languages_used": {"Python": 60, "JavaScript": 40},
    "frameworks_detected": ["Django", "React"]
  }]
}
EOF

curl -s -X POST \
  -H "Content-Type: application/json" \
  -d @/tmp/enrichment_request.json \
  -o /tmp/enrichment_response.json \
  "$BASE_URL$API_PREFIX/enrich"

if [ $? -eq 0 ]; then
    echo "Response:"
    cat /tmp/enrichment_response.json | jq '.' 2>/dev/null || cat /tmp/enrichment_response.json
    print_status 0 "Basic enrichment successful"
else
    print_status 1 "Basic enrichment failed"
fi

# Test 7: Enrichment with Job Context
echo -e "\n${YELLOW}7. Testing Enrichment with Job Context...${NC}"

cat > /tmp/enrichment_job_request.json << 'EOF'
{
  "resume_data": {
    "personal_info": {
      "name": {"value": "John Doe", "confidence": 0.95},
      "email": {"value": "john.doe@email.com", "confidence": 0.90},
      "confidence": 0.85
    },
    "skills": {
      "technical_skills": ["Python", "JavaScript", "React", "PostgreSQL"],
      "categories": {
        "programming_languages": ["Python", "JavaScript"],
        "frameworks": ["React"],
        "databases": ["PostgreSQL"]
      }
    }
  },
  "github_profiles": [{
    "profile": {
      "username": "johndoe",
      "name": "John Doe",
      "public_repos": 25,
      "profile_url": "https://github.com/johndoe"
    },
    "confidence": 0.90,
    "match_reasoning": "Name match",
    "repositories": [],
    "languages_used": {"Python": 60, "JavaScript": 40},
    "frameworks_detected": ["React"]
  }],
  "job_context": {
    "required_skills": ["Python", "JavaScript", "React", "PostgreSQL"],
    "preferred_skills": ["Django", "Node.js", "AWS"],
    "experience_level": "senior",
    "role_type": "fullstack"
  }
}
EOF

curl -s -X POST \
  -H "Content-Type: application/json" \
  -d @/tmp/enrichment_job_request.json \
  -o /tmp/enrichment_job_response.json \
  "$BASE_URL$API_PREFIX/enrich"

if [ $? -eq 0 ]; then
    echo "Response:"
    cat /tmp/enrichment_job_response.json | jq '.' 2>/dev/null || cat /tmp/enrichment_job_response.json
    print_status 0 "Job context enrichment successful"
else
    print_status 1 "Job context enrichment failed"
fi

# Test 8: Validation
echo -e "\n${YELLOW}8. Testing Request Validation...${NC}"

curl -s -X POST \
  -H "Content-Type: application/json" \
  -d @/tmp/enrichment_request.json \
  -o /tmp/validation_response.json \
  "$BASE_URL$API_PREFIX/validate"

if [ $? -eq 0 ]; then
    echo "Response:"
    cat /tmp/validation_response.json | jq '.' 2>/dev/null || cat /tmp/validation_response.json
    print_status 0 "Validation successful"
else
    print_status 1 "Validation failed"
fi

# Test 9: Error Handling (Invalid Request)
echo -e "\n${YELLOW}9. Testing Error Handling...${NC}"

cat > /tmp/invalid_request.json << 'EOF'
{
  "github_profiles": [{
    "profile": {
      "username": "johndoe",
      "profile_url": "https://github.com/johndoe"
    },
    "confidence": 0.90,
    "match_reasoning": "Test"
  }]
}
EOF

curl -s -X POST \
  -H "Content-Type: application/json" \
  -d @/tmp/invalid_request.json \
  -o /tmp/error_response.json \
  "$BASE_URL$API_PREFIX/enrich"

if [ $? -eq 0 ]; then
    echo "Response:"
    cat /tmp/error_response.json | jq '.' 2>/dev/null || cat /tmp/error_response.json
    print_status 0 "Error handling test completed"
else
    print_status 1 "Error handling test failed"
fi

# Cleanup
rm -f /tmp/*.json

echo -e "\n${YELLOW}========================================"
echo "🎉 All curl tests completed!"
echo "Check the responses above for results."
echo "========================================${NC}" 