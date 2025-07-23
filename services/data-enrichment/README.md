# Data Enrichment Service

The Data Enrichment Service combines and enriches data from the Resume Parser and Profile Discovery services to create comprehensive candidate profiles.

## Overview

This service is responsible for:
- **Data Integration**: Combining resume data with GitHub/LinkedIn profile data
- **Skill Analysis**: Calculating skill proficiency based on evidence
- **Conflict Resolution**: Handling discrepancies between data sources
- **Database Storage**: Storing enriched profiles in PostgreSQL
- **Confidence Scoring**: Maintaining confidence throughout enrichment

## Architecture

```
Resume Parser (8000) → Profile Discovery (8001) → Data Enrichment (8002) → Narrative Generation
```

## Features

### 1. Smart Data Merging
- Combines resume data with GitHub repository analysis
- Resolves conflicts between different data sources
- Merges duplicate skills with confidence weighting

### 2. Advanced Skill Analysis
- Calculates skill proficiency based on evidence
- Analyzes programming language distribution from GitHub
- Weights recent usage more heavily than historical
- Estimates years of experience per technology

### 3. Experience Relevance Analysis
- Matches experience to job requirements
- Evaluates career progression
- Assesses project complexity from GitHub repos

## API Endpoints

### POST /api/v1/enrich
Enriches candidate data by combining resume and profile discovery data.

**Request:**
```json
{
  "resume_data": {
    "personal_info": {...},
    "education": {...},
    "experience": {...},
    "skills": {...}
  },
  "github_profiles": [...],
  "linkedin_profiles": [...],
  "job_context": {
    "required_skills": ["Python", "JavaScript"],
    "experience_level": "mid",
    "role_type": "backend"
  }
}
```

**Response:**
```json
{
  "success": true,
  "enriched_profile": {
    "candidate_id": "uuid",
    "personal_info": {...},
    "skills": {
      "technical_skills": [...],
      "proficiency_scores": {...},
      "years_experience": {...}
    },
    "experience": {...},
    "github_analysis": {...},
    "overall_confidence": 0.85
  },
  "enrichment_metadata": {...},
  "processing_time_ms": 1250
}
```

## Setup

1. **Install dependencies:**
   ```bash
   poetry install
   ```

2. **Set up environment variables:**
   ```bash
   export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/recruitraptor"
   export LOG_LEVEL="INFO"
   ```

3. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

4. **Start the service:**
   ```bash
   poetry run uvicorn data_enrichment.main:app --host 0.0.0.0 --port 8002 --reload
   ```

## Development

### Running Tests
```bash
poetry run pytest
```

### Code Formatting
```bash
poetry run black src/
poetry run isort src/
```

### Type Checking
```bash
poetry run mypy src/
```

## Configuration

The service uses the following configuration options:

- `DATABASE_URL`: PostgreSQL connection string
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `MIN_CONFIDENCE_THRESHOLD`: Minimum confidence for data inclusion (default: 0.3)
- `SKILL_WEIGHTING_FACTOR`: Weight for recent vs historical skill usage (default: 0.7)

## Data Flow

1. **Input**: Resume data + GitHub/LinkedIn profiles
2. **Integration**: Combine and normalize data
3. **Analysis**: Calculate skill proficiency and experience relevance
4. **Conflict Resolution**: Handle data discrepancies
5. **Enrichment**: Add derived insights and metrics
6. **Storage**: Save to PostgreSQL database
7. **Output**: Enriched candidate profile

## Dependencies

- **Resume Parser Service** (Port 8000): For parsed resume data
- **Profile Discovery Service** (Port 8001): For GitHub/LinkedIn profiles
- **PostgreSQL**: For storing enriched profiles
- **Redis** (optional): For caching and session management 