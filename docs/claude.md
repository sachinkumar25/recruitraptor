# CLAUDE.md

Rules:

##Standard Workflow
First think through the problem, read the codebase for relevant files, and write a plan to tasks/todo.md.

The plan should have a list of todo items that you can check off as you complete them

Before you begin working, check in with me and I will verify the plan.

Then, begin working on the todo items, marking them as complete as you go.

Please every step of the way just give me a high level explanation of what changes you made

Make every task and code change you do as simple as possible. We want to avoid making any massive or complex changes. Every change should impact as little code as possible. Everything is about simplicity.

Finally, add a review section to the todo.md file with a summary of the changes you made and any other relevant information.





This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# CLAUDE.md - AI Recruiter Agent Project Context

## Project Description

**AI Recruiter Agent** is a microservices-based system that automates candidate evaluation for technical recruiters. The system processes uploaded resumes, discovers candidate profiles across GitHub and LinkedIn, enriches the data with additional insights, and generates comprehensive candidate assessments using AI narrative generation.

**Core Workflow**: Resume Upload → Text Extraction → Field Parsing → Profile Discovery → Data Enrichment → LLM-Generated Assessment → Interactive Dashboard

**Target Users**: Technical recruiters who need to quickly evaluate software engineering candidates with consistent, detailed analysis.

**Business Value**: Reduces candidate screening time from 20+ minutes to under 1 minute while improving evaluation consistency and depth.

## Key Concepts and Terminology

### Domain Concepts
- **Candidate Profile**: Complete aggregated data about a job candidate from resume, GitHub, and LinkedIn
- **Confidence Scoring**: 0.0-1.0 reliability indicator for all extracted data fields
- **Profile Discovery**: Automated process of finding candidate's GitHub and LinkedIn profiles
- **Data Enrichment**: Process of combining resume data with external profile information
- **Narrative Assessment**: AI-generated candidate evaluation tailored to specific job requirements

### Technical Concepts
- **Processing Pipeline**: Sequential data flow through microservices (Parser → Discovery → Enrichment → Generation)
- **Field Extraction**: NLP-based parsing of resume text into structured data fields
- **Repository Analysis**: GitHub repository examination for technical skills and project quality
- **Skill Proficiency Estimation**: Algorithm that estimates candidate skill levels based on evidence
- **Cross-Reference Validation**: Verification of candidate data consistency across multiple sources

### Service Definitions
- **Resume Parser Service**: Extracts structured data from PDF/DOCX/TXT resume files
- **Profile Discovery Service**: Searches for and validates GitHub and LinkedIn profiles
- **Data Enrichment Service**: Combines data sources and performs skill analysis
- **Narrative Generation Service**: Creates AI-powered candidate assessments using LLMs
- **User Interface**: Web dashboard for file upload, data review, and report generation

## Project Structure

```
ai-recruiter-agent/
├── shared/                          # Common utilities and models
│   ├── models/                      # Pydantic models shared across services
│   ├── utils/                       # Common helper functions
│   └── config/                      # Shared configuration classes
├── services/                        # Microservices directory
│   ├── resume-parser/              # Service 1: Document processing
│   │   ├── src/resume_parser/      # Main service code
│   │   ├── tests/                  # Service-specific tests
│   │   ├── pyproject.toml          # Python dependencies
│   │   └── Dockerfile              # Container configuration
│   ├── profile-discovery/          # Service 2: Profile URL detection
│   ├── data-enrichment/            # Service 3: Data aggregation
│   ├── narrative-engine/           # Service 4: LLM-powered analysis
│   └── user-service/               # Service 5: Authentication & sessions
├── frontend/                       # Next.js React application
│   ├── src/                        # React components and pages
│   ├── public/                     # Static assets
│   └── package.json                # Node.js dependencies
├── infrastructure/
│   ├── docker/                     # Docker Compose configurations
│   └── scripts/                    # Deployment and setup scripts
├── tests/                          # Integration and end-to-end tests
├── docker-compose.yml              # Local development environment
├── docker-compose.prod.yml         # Production deployment configuration
└── README.md                       # Project setup and usage instructions
```

### Service Internal Structure (Example: Resume Parser)
```
services/resume-parser/
├── src/resume_parser/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application entry point
│   ├── api/
│   │   └── routes.py               # HTTP endpoint definitions
│   ├── core/
│   │   ├── extractor.py            # Text extraction from files
│   │   ├── parser.py               # NLP field parsing logic
│   │   └── models.py               # Request/response models
│   ├── services/
│   │   └── parsing_service.py      # Business logic orchestration
│   └── utils/
│       ├── logger.py               # Structured logging setup
│       └── exceptions.py           # Custom exception classes
├── tests/                          # Pytest test suite
├── pyproject.toml                  # Poetry dependencies and configuration
└── Dockerfile                      # Container build instructions
```

## Dependencies

### Backend Services (Python 3.11+)
```toml
# Core framework and API
fastapi = "^0.104.1"               # Web framework for REST APIs
uvicorn = "^0.24.0"                # ASGI server for FastAPI
pydantic = "^2.5.0"                # Data validation and settings

# File processing
PyPDF2 = "^3.0.1"                  # PDF text extraction
python-docx = "^1.1.0"             # DOCX file processing
python-multipart = "^0.0.6"        # File upload handling

# Natural Language Processing
spacy = "^3.7.2"                   # NLP for resume parsing
# Note: Requires: python -m spacy download en_core_web_sm

# HTTP and External APIs
httpx = "^0.25.2"                  # Async HTTP client for external APIs
requests = "^2.31.0"               # Synchronous HTTP requests
beautifulsoup4 = "^4.12.2"         # HTML parsing for web scraping

# Database and Caching
asyncpg = "^0.29.0"                # PostgreSQL async driver
redis = "^5.0.1"                   # Redis client for caching
sqlalchemy = "^2.0.23"             # Database ORM

# AI and LLM Integration
openai = "^1.3.0"                  # OpenAI API client
anthropic = "^0.7.0"               # Anthropic Claude API client

# Development and Testing
pytest = "^7.4.3"                 # Testing framework
pytest-asyncio = "^0.21.1"        # Async testing support
pytest-cov = "^4.1.0"             # Code coverage
structlog = "^23.2.0"             # Structured logging
```

### Frontend (Node.js 18+)
```json
{
  "dependencies": {
    "next": "^14.0.0",              // React framework
    "react": "^18.2.0",             // UI library
    "react-dom": "^18.2.0",         // DOM bindings
    "tailwindcss": "^3.3.0",        // CSS framework
    "@headlessui/react": "^1.7.0",  // Accessible UI components
    "lucide-react": "^0.263.1",     // Icon library
    "axios": "^1.6.0",              // HTTP client
    "react-dropzone": "^14.2.0",    // File upload component
    "recharts": "^2.8.0"            // Charts and data visualization
  },
  "devDependencies": {
    "typescript": "^5.2.0",         // Type safety
    "@types/react": "^18.2.0",      // React type definitions
    "eslint": "^8.0.0",             // Code linting
    "prettier": "^3.0.0"            // Code formatting
  }
}
```

### Infrastructure
```yaml
# Docker services (docker-compose.yml)
services:
  postgres:
    image: postgres:15              # Primary database
    environment:
      POSTGRES_DB: recruiter_agent
      
  redis:
    image: redis:7-alpine           # Caching and sessions
    
  minio:
    image: minio/minio             # S3-compatible object storage
    command: server /data --console-address ":9001"
```

## Important Files and Directories

### Configuration Files
- **docker-compose.yml**: Local development environment setup with all services
- **docker-compose.prod.yml**: Production deployment configuration
- **.env.example**: Template for environment variables (API keys, database URLs)
- **pyproject.toml**: Python dependency management and project configuration
- **package.json**: Frontend dependencies and build scripts

### Core Business Logic
- **shared/models/**: Pydantic models defining data structures used across services
  - `candidate.py`: Core candidate data models
  - `assessment.py`: AI assessment and narrative models
  - `processing.py`: Request/response models for API communication

### Service Entry Points
- **services/resume-parser/src/resume_parser/main.py**: Resume processing API
- **services/profile-discovery/src/profile_discovery/main.py**: Profile search API
- **services/data-enrichment/src/data_enrichment/main.py**: Data combination API
- **services/narrative-engine/src/narrative_engine/main.py**: AI assessment API
- **frontend/src/pages/**: Next.js page components and routing

### Key Utility Files
- **shared/utils/logger.py**: Structured logging configuration used by all services
- **shared/utils/exceptions.py**: Common exception classes for error handling
- **shared/config/settings.py**: Configuration management and environment variables
- **infrastructure/scripts/setup.py**: Development environment setup automation

### External API Integration
- **services/profile-discovery/src/profile_discovery/clients/**: External API clients
  - `github_client.py`: GitHub API integration for repository analysis
  - `search_client.py`: SerpAPI integration for LinkedIn profile discovery
- **services/narrative-engine/src/narrative_engine/llm/**: LLM provider integrations
  - `openai_client.py`: OpenAI GPT integration
  - `anthropic_client.py`: Claude API integration

### Database Schema
- **infrastructure/database/migrations/**: Database schema version control
- **shared/models/database.py**: SQLAlchemy table definitions
- **infrastructure/scripts/init_db.py**: Database initialization script

### Testing Infrastructure
- **tests/integration/**: Cross-service integration tests
- **tests/fixtures/**: Test data including sample resumes and API responses
- **tests/conftest.py**: Pytest configuration and shared fixtures
- **Each service/tests/**: Unit tests specific to individual services

### Documentation
- **README.md**: Project setup instructions and development guide
- **docs/api/**: API documentation and endpoint specifications
- **docs/deployment/**: Production deployment and scaling guides
- **instructions.md**: Detailed PRD and implementation specifications

# RecruitRaptor - Project Context & Governance

## 1. Project Overview
**Mission:** An AI-powered recruiter agent that automates candidate screening (Resume → Profile Discovery → Enrichment → Narrative) to reduce evaluation time from 20 mins to 30 seconds.
**Repo:** `sachinkumar25/recruitraptor`
**Stack:** Python 3.11, FastAPI, Docker, Pydantic v2, spaCy.

## 2. Core Service Architecture (Level 4 Breakdown)

### Service 1: Resume Parser (Port 8000)
* **1.1.1.1 Magic Bytes:** Validate PDF/DOCX headers before processing.
* **1.1.2.2 Layout Analysis:** Detect column layouts to prevent text scrambling.
* **1.2.1.2 Regex Overlays:** Strict regex for Emails/URLs overrides NLP.

### Service 2: Profile Discovery (Port 8001)
* **2.1.1.2 Email Permutation:** GitHub API search via email variants.
* **2.1.2.1 SERP Querying:** `site:linkedin.com/in/` + Name + Company.
* **2.1.2.3 Cross-Validation:** Levenshtein distance check on Headlines.

### Service 3: Data Enrichment (Port 8002)
* **3.1.1.1 Truth Hierarchy:** GitHub Code > LinkedIn Dates > Resume Claims.
* **3.1.2.1 Gap Analysis:** Auto-flag >90 day timeline gaps.
* **3.1.2.2 Skill Verification:** Correlate skill usage with repo commit history.

### Service 4: Narrative Engine (Port 8003)
* **4.1.1.2 Role Mapping:** Map Candidate Vector to Job Description Vector.
* **4.1.2.2 Schema Enforcement:** JSON output only for UI rendering.

## 3. Development Guidelines
* **Config:** Use `pydantic-settings` for all env vars.
* **Testing:** `pytest` for unit logic, `testcontainers` for DB/Service integration.
* **Error Handling:** Never fail silently. Return structured JSON errors with error codes.