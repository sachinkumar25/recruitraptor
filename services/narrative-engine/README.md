# Narrative Engine Service

AI-powered narrative generation for candidate assessments in the AI Recruiter Agent pipeline.

## 🎯 **Service Purpose**

The Narrative Engine Service is the **final component** in the AI Recruiter Agent pipeline, generating comprehensive, AI-powered candidate assessments tailored to specific job requirements.

**Pipeline Flow:**
```
Resume Parser (8000) → Profile Discovery (8001) → Data Enrichment (8002) → Narrative Generation (8003)
```

## 🚀 **Features**

### **Structured Narrative Generation**
- **Executive Summary** (2-3 sentences for C-suite)
- **Technical Skills Assessment** (detailed analysis with evidence)
- **Experience Relevance** (connection to job requirements)
- **Project Portfolio Analysis** (GitHub projects evaluation)
- **Growth Potential** (learning trajectory assessment)

### **Multiple Narrative Styles**
- **Executive**: High-level for C-suite leadership
- **Technical**: Detailed for engineering managers
- **Comprehensive**: Balanced assessment for talent acquisition
- **Concise**: Quick screening summary for recruiters

### **Context-Aware Generation**
- Prioritizes relevant skills for target role
- Addresses job requirements explicitly
- Highlights transferable skills
- Connects background to company needs

### **LLM Integration**
- **OpenAI GPT-4** (primary provider)
- **Anthropic Claude** (alternative provider)
- Configurable generation parameters
- Fallback mechanisms

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  Narrative       │    │   LLM Service   │
│   (Port 8003)   │───▶│  Service         │───▶│  (OpenAI/       │
│                 │    │                  │    │   Anthropic)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌──────────────────┐
│   Data          │    │   Prompt         │
│   Enrichment    │    │   Builder        │
│   Service       │    │                  │
│   (Port 8002)   │    └──────────────────┘
└─────────────────┘
```

## 📋 **API Endpoints**

### **Core Endpoints**
- `POST /api/v1/generate` - Generate candidate narrative
- `GET /api/v1/health` - Health check with LLM provider status
- `GET /api/v1/capabilities` - Service capabilities
- `GET /api/v1/styles` - Available narrative styles
- `GET /api/v1/providers` - LLM provider status

### **Utility Endpoints**
- `GET /` - Service information
- `GET /health` - Basic health check
- `GET /metrics` - Service metrics
- `GET /docs` - Interactive API documentation

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Service Configuration
DEBUG=true
LOG_LEVEL=DEBUG
HOST=0.0.0.0
PORT=8003

# LLM Configuration
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4

# External Services
DATA_ENRICHMENT_URL=http://localhost:8002

# Generation Configuration
MAX_TOKENS=2000
TEMPERATURE=0.7
NARRATIVE_STYLE=comprehensive
```

### **Supported Models**
- **OpenAI**: `gpt-4`, `gpt-3.5-turbo`, `gpt-4-turbo`
- **Anthropic**: `claude-3-opus`, `claude-3-sonnet`, `claude-3-haiku`

## 🚀 **Quick Start**

### **1. Install Dependencies**
```bash
poetry install
```

### **2. Configure Environment**
```bash
# Copy and edit .env file
cp .env.example .env
# Add your OpenAI API key
```

### **3. Run Tests**
```bash
poetry run python test_narrative_service.py
```

### **4. Start Service**
```bash
poetry run uvicorn src.narrative_engine.main:app --reload --port 8003
```

### **5. Access API Documentation**
Visit: http://localhost:8003/docs

## 📝 **Usage Examples**

### **Generate Comprehensive Narrative**
```bash
curl -X POST "http://localhost:8003/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "candidate-123",
    "job_requirement": {
      "title": "Senior Software Engineer",
      "department": "Engineering",
      "required_skills": ["Python", "React", "API Development"],
      "experience_level": "senior"
    },
    "narrative_style": "comprehensive",
    "llm_provider": "openai"
  }'
```

### **Generate Executive Summary**
```bash
curl -X POST "http://localhost:8003/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "candidate-123",
    "job_requirement": {
      "title": "CTO",
      "department": "Executive"
    },
    "narrative_style": "executive"
  }'
```

## 📊 **Response Format**

### **Successful Response**
```json
{
  "success": true,
  "narrative": {
    "candidate_id": "candidate-123",
    "job_requirement": { ... },
    "narrative_style": "comprehensive",
    "executive_summary": {
      "title": "Executive Summary",
      "content": "Sachin Kumar is a highly skilled...",
      "confidence_score": 0.8
    },
    "technical_skills_assessment": { ... },
    "experience_relevance": { ... },
    "project_portfolio_analysis": { ... },
    "growth_potential": { ... },
    "overall_assessment": "Strong candidate with excellent...",
    "recommendation": "Recommend proceeding to technical interview",
    "confidence_score": 0.75
  },
  "processing_time_ms": 2345.67
}
```

## 🔍 **Testing**

### **Run Service Tests**
```bash
poetry run python test_narrative_service.py
```

### **Test with Real Data**
1. Ensure Data Enrichment Service is running on port 8002
2. Use a real candidate ID from the enrichment service
3. Test different narrative styles and LLM providers

## 🐳 **Docker Deployment**

### **Build Image**
```bash
docker build -t narrative-engine:latest .
```

### **Run Container**
```bash
docker run -p 8003:8003 \
  -e OPENAI_API_KEY=your_key \
  -e DATA_ENRICHMENT_URL=http://data-enrichment:8002 \
  narrative-engine:latest
```

## 📈 **Monitoring**

### **Health Check**
```bash
curl http://localhost:8003/api/v1/health
```

### **Metrics**
```bash
curl http://localhost:8003/metrics
```

### **Logs**
The service uses structured logging with correlation IDs for request tracking.

## 🔗 **Integration**

### **With Data Enrichment Service**
- Fetches enriched profiles via HTTP API
- Requires candidate ID from enrichment service
- Handles service unavailability gracefully

### **With Frontend**
- CORS configured for frontend integration
- JSON API responses
- Error handling with meaningful messages

## 🛠️ **Development**

### **Project Structure**
```
narrative-engine/
├── src/narrative_engine/
│   ├── api/routes.py          # API endpoints
│   ├── core/
│   │   ├── config.py          # Configuration
│   │   └── models.py          # Data models
│   ├── services/
│   │   ├── llm_service.py     # LLM integration
│   │   └── narrative_service.py # Core logic
│   ├── utils/logger.py        # Logging
│   └── main.py               # FastAPI app
├── tests/                    # Test files
├── pyproject.toml           # Dependencies
└── README.md               # This file
```

### **Adding New Features**
1. Update models in `core/models.py`
2. Add service logic in `services/`
3. Create API endpoints in `api/routes.py`
4. Add tests in `tests/`
5. Update documentation

## 🎉 **Success Criteria**

✅ **Structured Narrative Generation** - All 5 sections implemented  
✅ **Multiple Narrative Styles** - 4 styles with context-aware prompts  
✅ **Context-Aware Generation** - Job requirement integration  
✅ **LLM Integration** - OpenAI and Anthropic support  
✅ **API Endpoints** - Complete REST API with documentation  
✅ **Error Handling** - Comprehensive error handling and logging  
✅ **Testing** - Service tests and validation  
✅ **Documentation** - Complete API and usage documentation  

## 🚀 **Next Steps**

1. **Production Deployment** - Docker containerization
2. **Database Integration** - Store generated narratives
3. **Caching** - Cache LLM responses for performance
4. **Monitoring** - Add metrics and alerting
5. **Frontend Integration** - Connect to recruiter interface

---

**The Narrative Engine Service completes the AI Recruiter Agent pipeline!** 🎯 