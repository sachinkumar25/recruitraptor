# Data Enrichment Service Testing Guide

## Overview

The **Data Enrichment Service** is the final component of the AI Recruiter Agent that combines data from multiple sources (Resume Parser and Profile Discovery) to create comprehensive, enriched candidate profiles.

**Service Details:**
- **Port**: 8002
- **Base URL**: `http://localhost:8002`
- **API Prefix**: `/api/v1`
- **Main Endpoint**: `/api/v1/enrich`

## What the Service Does

1. **Data Integration**: Combines resume data with GitHub and LinkedIn profiles
2. **Conflict Resolution**: Resolves conflicts between different data sources
3. **Skill Analysis**: Analyzes and categorizes technical skills
4. **Job Matching**: Calculates job relevance scores when job context is provided
5. **Confidence Scoring**: Provides confidence scores for all enriched data

## Testing Options

### Option 1: Quick Python Test (Recommended)
```bash
cd ai-recruiter-agent/services/data-enrichment
python quick_test.py
```

### Option 2: Comprehensive Python Test
```bash
cd ai-recruiter-agent/services/data-enrichment
python test_enrichment_service.py
```

### Option 3: Curl Commands
```bash
cd ai-recruiter-agent/services/data-enrichment
./curl_tests.sh
```

### Option 4: Manual Testing with curl
```bash
# Health check
curl http://localhost:8002/health

# Root endpoint
curl http://localhost:8002/

# Capabilities
curl http://localhost:8002/api/v1/capabilities

# Basic enrichment
curl -X POST http://localhost:8002/api/v1/enrich \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```

## Test Scenarios

### 1. Basic Functionality Tests
- ✅ Health check endpoint
- ✅ Root endpoint
- ✅ Service capabilities
- ✅ Configuration retrieval
- ✅ Statistics endpoint

### 2. Core Enrichment Tests
- ✅ Basic enrichment (resume + GitHub profile)
- ✅ Enrichment with job context
- ✅ Request validation
- ✅ Error handling

### 3. Data Integration Tests
- ✅ Resume data integration
- ✅ GitHub profile integration
- ✅ LinkedIn profile integration
- ✅ Conflict resolution

### 4. Skill Analysis Tests
- ✅ Technical skill categorization
- ✅ Proficiency level calculation
- ✅ Skill matching with job requirements
- ✅ Skill gap analysis

## Sample Request Structure

### Basic Enrichment Request
```json
{
  "resume_data": {
    "personal_info": {
      "name": {"value": "John Doe", "confidence": 0.95},
      "email": {"value": "john.doe@email.com", "confidence": 0.90},
      "confidence": 0.85
    },
    "skills": {
      "technical_skills": ["Python", "JavaScript", "React"],
      "categories": {
        "programming_languages": ["Python", "JavaScript"],
        "frameworks": ["React"]
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
    "languages_used": {"Python": 60, "JavaScript": 40},
    "frameworks_detected": ["React"]
  }]
}
```

### Enrichment with Job Context
```json
{
  "resume_data": { /* same as above */ },
  "github_profiles": [ /* same as above */ ],
  "job_context": {
    "required_skills": ["Python", "JavaScript", "React", "PostgreSQL"],
    "preferred_skills": ["Django", "Node.js", "AWS"],
    "experience_level": "senior",
    "role_type": "fullstack"
  }
}
```

## Expected Response Structure

### Successful Enrichment Response
```json
{
  "success": true,
  "enriched_profile": {
    "candidate_id": "uuid-string",
    "personal_info": {
      "name": "John Doe",
      "email": "john.doe@email.com",
      "overall_confidence": 0.85,
      "data_sources": ["resume", "github"]
    },
    "skills": {
      "technical_skills": [
        {
          "skill_name": "Python",
          "proficiency_level": "advanced",
          "confidence_score": 0.9,
          "evidence_sources": ["resume", "github"]
        }
      ],
      "overall_confidence": 0.85,
      "skill_gaps": ["AWS"],
      "skill_strengths": ["Python", "React"]
    },
    "github_analysis": {
      "total_repositories": 25,
      "languages_distribution": {"Python": 60, "JavaScript": 40},
      "recent_activity_score": 0.8
    },
    "overall_confidence": 0.85,
    "job_relevance_score": 0.9,
    "skill_match_percentage": 0.9
  },
  "enrichment_metadata": {
    "processing_time_ms": 150.5,
    "data_sources_used": ["resume", "github"],
    "algorithms_used": ["data_integration", "skill_analysis", "conflict_resolution"]
  },
  "processing_time_ms": 150.5
}
```

## Testing Checklist

### Pre-Testing Setup
- [ ] Ensure Resume Parser service is running (port 8000)
- [ ] Ensure Profile Discovery service is running (port 8001)
- [ ] Ensure Data Enrichment service is running (port 8002)
- [ ] Check all services are healthy

### Basic Tests
- [ ] Health check returns 200 OK
- [ ] Root endpoint returns service info
- [ ] Capabilities endpoint lists supported features
- [ ] Configuration endpoint returns settings

### Core Functionality Tests
- [ ] Basic enrichment works with resume + GitHub data
- [ ] Enrichment with job context calculates relevance scores
- [ ] Request validation catches invalid requests
- [ ] Error handling returns proper error messages

### Data Quality Tests
- [ ] Conflict resolution works correctly
- [ ] Skill analysis produces meaningful results
- [ ] Confidence scores are reasonable (0.0-1.0)
- [ ] Job matching provides accurate scores

### Performance Tests
- [ ] Response time is under 5 seconds
- [ ] Memory usage is reasonable
- [ ] No memory leaks during repeated requests

## Troubleshooting

### Common Issues

1. **Service not starting**
   ```bash
   # Check if port 8002 is available
   lsof -i :8002
   
   # Check service logs
   tail -f logs/data-enrichment.log
   ```

2. **Import errors**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   # or
   poetry install
   ```

3. **Database connection issues**
   ```bash
   # Check database configuration
   cat .env | grep DATABASE
   ```

4. **Validation errors**
   - Check request format matches expected schema
   - Ensure all required fields are present
   - Verify confidence scores are between 0.0 and 1.0

### Debug Mode

Enable debug mode for detailed logging:
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
```

## Integration Testing

### End-to-End Workflow
1. **Parse Resume**: Use Resume Parser service
2. **Discover Profiles**: Use Profile Discovery service
3. **Enrich Data**: Use Data Enrichment service
4. **Verify Results**: Check enriched profile quality

### Sample Integration Test
```bash
# 1. Parse a resume
curl -X POST http://localhost:8000/api/v1/parse \
  -F "file=@sample_resume.pdf"

# 2. Discover GitHub profiles
curl -X POST http://localhost:8001/api/v1/discover \
  -H "Content-Type: application/json" \
  -d '{"resume_data": {...}}'

# 3. Enrich the combined data
curl -X POST http://localhost:8002/api/v1/enrich \
  -H "Content-Type: application/json" \
  -d '{"resume_data": {...}, "github_profiles": [...]}'
```

## Performance Benchmarks

### Expected Performance
- **Health Check**: < 100ms
- **Basic Enrichment**: < 2 seconds
- **Job Context Enrichment**: < 3 seconds
- **Memory Usage**: < 512MB
- **CPU Usage**: < 50% during processing

### Load Testing
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test health endpoint
ab -n 100 -c 10 http://localhost:8002/health

# Test enrichment endpoint (with sample data)
ab -n 50 -c 5 -p sample_request.json -T application/json \
  http://localhost:8002/api/v1/enrich
```

## Success Criteria

A successful test run should show:
- ✅ All basic endpoints responding correctly
- ✅ Enrichment producing meaningful results
- ✅ Job context analysis working
- ✅ Error handling functioning properly
- ✅ Response times within acceptable limits
- ✅ No critical errors in logs

## Next Steps

After successful testing:
1. **Monitor Performance**: Watch response times and resource usage
2. **Validate Results**: Check enriched data quality manually
3. **Integration Testing**: Test with other services
4. **Production Deployment**: Deploy to production environment 