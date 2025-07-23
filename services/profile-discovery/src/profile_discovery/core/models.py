"""Pydantic models for Profile Discovery Service."""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class PlatformType(str, Enum):
    """Supported platform types."""
    GITHUB = "github"
    LINKEDIN = "linkedin"


class DiscoveryStrategy(str, Enum):
    """Discovery strategies."""
    DIRECT_URL = "direct_url"
    EMAIL_BASED = "email_based"
    NAME_CONTEXT = "name_context"
    FUZZY_MATCHING = "fuzzy_matching"
    SEARCH_ENGINE = "search_engine"


# Resume Parser Data Models (compatible with Resume Parser output)
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


class ExtractedResumeData(BaseModel):
    """Complete resume data from Resume Parser."""
    personal_info: PersonalInfo
    education: Dict[str, Any] = Field(default_factory=dict)
    experience: Dict[str, Any] = Field(default_factory=dict)
    skills: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# GitHub Discovery Models
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
    profile_url: str = Field(description="Full GitHub profile URL")


class GitHubProfileMatch(BaseModel):
    """GitHub profile match with confidence scoring."""
    profile: GitHubProfile
    confidence: float = Field(ge=0.0, le=1.0, description="Match confidence score")
    match_reasoning: str = Field(description="Explanation of why this profile matches")
    repositories: List[GitHubRepository] = Field(default_factory=list)
    languages_used: Dict[str, int] = Field(default_factory=dict, description="Programming languages and usage count")
    frameworks_detected: List[str] = Field(default_factory=list, description="Detected frameworks and tools")
    discovery_strategy: DiscoveryStrategy = Field(description="Strategy used to discover this profile")


# LinkedIn Discovery Models
class LinkedInProfile(BaseModel):
    """LinkedIn profile information."""
    profile_url: str = Field(description="LinkedIn profile URL")
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
    confidence: float = Field(ge=0.0, le=1.0, description="Match confidence score")
    match_reasoning: str = Field(description="Explanation of why this profile matches")
    discovery_strategy: DiscoveryStrategy = Field(description="Strategy used to discover this profile")


# Request/Response Models
class DiscoveryOptions(BaseModel):
    """Options for profile discovery."""
    search_github: bool = Field(default=True, description="Whether to search GitHub")
    search_linkedin: bool = Field(default=True, description="Whether to search LinkedIn")
    max_github_results: int = Field(default=5, ge=1, le=10, description="Maximum GitHub results")
    max_linkedin_results: int = Field(default=3, ge=1, le=5, description="Maximum LinkedIn results")
    min_confidence_score: float = Field(default=0.3, ge=0.0, le=1.0, description="Minimum confidence score")
    include_repository_analysis: bool = Field(default=True, description="Include GitHub repository analysis")


class DiscoveryRequest(BaseModel):
    """Request model for profile discovery."""
    candidate_data: ExtractedResumeData = Field(description="Parsed resume data from Resume Parser")
    discovery_options: Optional[DiscoveryOptions] = Field(default_factory=DiscoveryOptions, description="Discovery options")


class DiscoveryMetadata(BaseModel):
    """Metadata about the discovery process."""
    total_processing_time_ms: float = Field(description="Total processing time in milliseconds")
    github_search_time_ms: float = Field(default=0.0, description="GitHub search time")
    linkedin_search_time_ms: float = Field(default=0.0, description="LinkedIn search time")
    strategies_used: List[DiscoveryStrategy] = Field(default_factory=list, description="Discovery strategies used")
    cache_hits: int = Field(default=0, description="Number of cache hits")
    api_calls_made: int = Field(default=0, description="Number of external API calls made")
    errors_encountered: List[str] = Field(default_factory=list, description="Errors encountered during discovery")


class DiscoveryResponse(BaseModel):
    """Response model for profile discovery."""
    success: bool = Field(description="Whether discovery was successful")
    github_profiles: List[GitHubProfileMatch] = Field(default_factory=list, description="Discovered GitHub profiles")
    linkedin_profiles: List[LinkedInProfileMatch] = Field(default_factory=list, description="Discovered LinkedIn profiles")
    discovery_metadata: DiscoveryMetadata = Field(description="Discovery process metadata")
    processing_time_ms: float = Field(description="Total processing time in milliseconds")
    error_message: Optional[str] = Field(default=None, description="Error message if discovery failed")


# Health Check Models
class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = Field(description="Service status")
    timestamp: str = Field(description="Current timestamp")
    version: str = Field(description="Service version")
    uptime_seconds: float = Field(description="Service uptime in seconds")
    external_services: Dict[str, str] = Field(default_factory=dict, description="External service status")


class SupportedPlatformsResponse(BaseModel):
    """Supported platforms response."""
    platforms: List[PlatformType] = Field(description="Supported platform types")
    discovery_strategies: List[DiscoveryStrategy] = Field(description="Available discovery strategies")
    rate_limits: Dict[str, Dict[str, Any]] = Field(description="Rate limit information")


# Error Models
class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(description="Error type")
    message: str = Field(description="Error message")
    timestamp: str = Field(description="Error timestamp")
    request_id: Optional[str] = Field(default=None, description="Request ID for tracking")


# Utility Functions
def create_error_response(error_type: str, message: str, request_id: Optional[str] = None) -> ErrorResponse:
    """Create a standardized error response."""
    return ErrorResponse(
        error=error_type,
        message=message,
        timestamp=datetime.now().isoformat(),
        request_id=request_id
    )


def create_health_response(version: str, uptime_seconds: float, external_services: Dict[str, str]) -> HealthCheckResponse:
    """Create a health check response."""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version=version,
        uptime_seconds=uptime_seconds,
        external_services=external_services
    )
