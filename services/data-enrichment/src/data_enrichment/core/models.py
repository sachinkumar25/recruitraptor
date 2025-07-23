"""Pydantic models for Data Enrichment Service."""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
from pydantic import Field, BaseModel, field_validator
from enum import Enum
import uuid


class SkillProficiencyLevel(str, Enum):
    """Skill proficiency levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ExperienceLevel(str, Enum):
    """Experience levels."""
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"


class DataSource(str, Enum):
    """Data sources for enrichment."""
    RESUME = "resume"
    GITHUB = "github"
    LINKEDIN = "linkedin"
    MANUAL = "manual"


class ConflictResolution(str, Enum):
    """Conflict resolution strategies."""
    RESUME_PRIORITY = "resume_priority"
    GITHUB_PRIORITY = "github_priority"
    HIGHEST_CONFIDENCE = "highest_confidence"
    MERGE = "merge"
    MANUAL_REVIEW = "manual_review"


# Input Models (from other services)
class ConfidenceField(BaseModel):
    """Model for fields with confidence scoring."""
    value: Optional[Any] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class PersonalInfo(BaseModel):
    """Personal information from resume."""
    name: ConfidenceField = Field(default_factory=lambda: ConfidenceField())
    email: ConfidenceField = Field(default_factory=lambda: ConfidenceField())
    phone: ConfidenceField = Field(default_factory=lambda: ConfidenceField())
    location: ConfidenceField = Field(default_factory=lambda: ConfidenceField())
    linkedin_url: ConfidenceField = Field(default_factory=lambda: ConfidenceField())
    github_url: ConfidenceField = Field(default_factory=lambda: ConfidenceField())
    confidence: float = Field(ge=0.0, le=1.0)


class GitHubRepository(BaseModel):
    """GitHub repository information."""
    name: str
    full_name: str
    description: Optional[str] = None
    language: Optional[str] = None
    stars: int = 0
    forks: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    topics: List[str] = Field(default_factory=list)
    is_fork: bool = False
    is_archived: bool = False


class GitHubProfile(BaseModel):
    """GitHub profile information."""
    username: str
    name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    blog: Optional[str] = None
    public_repos: int = 0
    public_gists: int = 0
    followers: int = 0
    following: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    avatar_url: Optional[str] = None
    profile_url: str


class GitHubProfileMatch(BaseModel):
    """GitHub profile match with confidence scoring."""
    profile: GitHubProfile
    confidence: float = Field(ge=0.0, le=1.0)
    match_reasoning: str
    repositories: List[GitHubRepository] = Field(default_factory=list)
    languages_used: Dict[str, int] = Field(default_factory=dict)
    frameworks_detected: List[str] = Field(default_factory=list)


class LinkedInProfile(BaseModel):
    """LinkedIn profile information."""
    profile_url: str
    name: Optional[str] = None
    headline: Optional[str] = None
    location: Optional[str] = None
    current_position: Optional[str] = None
    current_company: Optional[str] = None
    summary: Optional[str] = None
    experience_count: Optional[int] = None
    education_count: Optional[int] = None


class LinkedInProfileMatch(BaseModel):
    """LinkedIn profile match with confidence scoring."""
    profile: LinkedInProfile
    confidence: float = Field(ge=0.0, le=1.0)
    match_reasoning: str


class ExtractedResumeData(BaseModel):
    """Complete resume data from Resume Parser."""
    personal_info: PersonalInfo
    education: Dict[str, Any] = Field(default_factory=dict)
    experience: Dict[str, Any] = Field(default_factory=dict)
    skills: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Job Context Models
class JobContext(BaseModel):
    """Job context for enrichment."""
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_level: Optional[ExperienceLevel] = None
    role_type: Optional[str] = None  # "backend", "frontend", "fullstack", etc.
    industry: Optional[str] = None
    company_size: Optional[str] = None  # "startup", "mid-size", "enterprise"
    location_requirements: Optional[str] = None


# Enriched Models
class SkillProficiency(BaseModel):
    """Skill proficiency analysis."""
    skill_name: str
    proficiency_level: SkillProficiencyLevel
    confidence_score: float = Field(ge=0.0, le=1.0)
    years_experience: Optional[float] = None
    evidence_sources: List[DataSource] = Field(default_factory=list)
    last_used: Optional[date] = None
    usage_frequency: Optional[str] = None  # "daily", "weekly", "monthly", "rarely"
    project_count: int = 0
    repository_count: int = 0


class EnrichedSkillsAnalysis(BaseModel):
    """Enriched skills analysis."""
    technical_skills: List[SkillProficiency] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    programming_languages: Dict[str, int] = Field(default_factory=dict)
    frameworks: Dict[str, int] = Field(default_factory=dict)
    databases: Dict[str, int] = Field(default_factory=dict)
    cloud_platforms: Dict[str, int] = Field(default_factory=dict)
    tools: Dict[str, int] = Field(default_factory=dict)
    overall_confidence: float = Field(ge=0.0, le=1.0)
    skill_gaps: List[str] = Field(default_factory=list)
    skill_strengths: List[str] = Field(default_factory=list)


class EnrichedPersonalInfo(BaseModel):
    """Enriched personal information."""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    github_username: Optional[str] = None
    linkedin_username: Optional[str] = None
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    overall_confidence: float = Field(ge=0.0, le=1.0)
    data_sources: List[DataSource] = Field(default_factory=list)


class EnrichedExperience(BaseModel):
    """Enriched work experience."""
    companies: List[str] = Field(default_factory=list)
    positions: List[str] = Field(default_factory=list)
    dates: List[str] = Field(default_factory=list)
    descriptions: List[str] = Field(default_factory=list)
    technologies_used: Dict[str, List[str]] = Field(default_factory=dict)
    project_complexity: Dict[str, str] = Field(default_factory=dict)  # "simple", "moderate", "complex"
    team_size: Dict[str, str] = Field(default_factory=dict)  # "individual", "small", "large"
    impact_metrics: Dict[str, str] = Field(default_factory=dict)
    overall_confidence: float = Field(ge=0.0, le=1.0)
    career_progression_score: Optional[float] = None


class EnrichedEducation(BaseModel):
    """Enriched education information."""
    institutions: List[str] = Field(default_factory=list)
    degrees: List[str] = Field(default_factory=list)
    fields_of_study: List[str] = Field(default_factory=list)
    dates: List[str] = Field(default_factory=list)
    gpa: Optional[float] = None
    relevant_courses: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    overall_confidence: float = Field(ge=0.0, le=1.0)


class GitHubRepositoryInsights(BaseModel):
    """GitHub repository analysis insights."""
    total_repositories: int = 0
    total_stars: int = 0
    total_forks: int = 0
    languages_distribution: Dict[str, int] = Field(default_factory=dict)
    frameworks_detected: List[str] = Field(default_factory=list)
    most_active_repos: List[str] = Field(default_factory=list)
    recent_activity_score: float = Field(ge=0.0, le=1.0)
    code_quality_indicators: Dict[str, Any] = Field(default_factory=dict)
    collaboration_patterns: Dict[str, Any] = Field(default_factory=dict)
    open_source_contribution_score: float = Field(ge=0.0, le=1.0)


class EnrichedCandidateProfile(BaseModel):
    """Complete enriched candidate profile."""
    candidate_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    personal_info: EnrichedPersonalInfo
    skills: EnrichedSkillsAnalysis
    experience: EnrichedExperience
    education: EnrichedEducation
    github_analysis: GitHubRepositoryInsights
    linkedin_analysis: Optional[Dict[str, Any]] = None
    overall_confidence: float = Field(ge=0.0, le=1.0)
    data_sources: List[DataSource] = Field(default_factory=list)
    enrichment_timestamp: datetime = Field(default_factory=datetime.utcnow)
    job_relevance_score: Optional[float] = None
    skill_match_percentage: Optional[float] = None


class ConflictResolutionResult(BaseModel):
    """Result of conflict resolution."""
    field_name: str
    original_values: Dict[DataSource, Any]
    resolved_value: Any
    resolution_strategy: ConflictResolution
    confidence_score: float = Field(ge=0.0, le=1.0)
    reasoning: str


class EnrichmentMetadata(BaseModel):
    """Metadata about the enrichment process."""
    processing_time_ms: float
    data_sources_used: List[DataSource]
    conflicts_resolved: List[ConflictResolutionResult]
    confidence_threshold: float = Field(ge=0.0, le=1.0)
    skill_weighting_factor: float = Field(ge=0.0, le=1.0)
    enrichment_version: str = "1.0.0"
    algorithms_used: List[str] = Field(default_factory=list)


# Request/Response Models
class EnrichmentRequest(BaseModel):
    """Request model for data enrichment."""
    resume_data: ExtractedResumeData
    github_profiles: List[GitHubProfileMatch] = Field(default_factory=list)
    linkedin_profiles: List[LinkedInProfileMatch] = Field(default_factory=list)
    job_context: Optional[JobContext] = None
    enrichment_options: Optional[Dict[str, Any]] = None


class EnrichmentResponse(BaseModel):
    """Response model for data enrichment."""
    success: bool
    enriched_profile: Optional[EnrichedCandidateProfile] = None
    enrichment_metadata: EnrichmentMetadata
    processing_time_ms: float
    error_message: Optional[str] = None


# Health Check Models
class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    version: str
    uptime_seconds: float
    database_status: str
    external_services: Dict[str, str] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    message: str
    timestamp: str
    request_id: Optional[str] = None


# Utility Functions
def create_error_response(error_type: str, message: str, request_id: Optional[str] = None) -> ErrorResponse:
    """Create a standardized error response."""
    return ErrorResponse(
        error=error_type,
        message=message,
        timestamp=datetime.now().isoformat(),
        request_id=request_id
    )


def create_health_response(version: str, uptime_seconds: float, database_status: str, external_services: Dict[str, str]) -> HealthCheckResponse:
    """Create a health check response."""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version=version,
        uptime_seconds=uptime_seconds,
        database_status=database_status,
        external_services=external_services
    )


# Validators
class EnrichedCandidateProfileValidator:
    """Custom validators for EnrichedCandidateProfile model."""
    
    @field_validator('overall_confidence')
    @classmethod
    def validate_confidence(cls, v):
        """Validate confidence score."""
        if v < 0 or v > 1:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v
    
    @field_validator('job_relevance_score')
    @classmethod
    def validate_job_relevance(cls, v):
        """Validate job relevance score."""
        if v is not None and (v < 0 or v > 1):
            raise ValueError("Job relevance score must be between 0.0 and 1.0")
        return v 