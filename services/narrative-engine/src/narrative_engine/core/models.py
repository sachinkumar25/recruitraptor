"""Data models for Narrative Engine Service."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class NarrativeStyle(str, Enum):
    """Supported narrative styles."""
    EXECUTIVE = "executive"
    TECHNICAL = "technical"
    COMPREHENSIVE = "comprehensive"
    CONCISE = "concise"


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class JobRequirement(BaseModel):
    """Job requirement specification."""
    title: str = Field(..., description="Job title")
    department: Optional[str] = Field(None, description="Department or team")
    required_skills: List[str] = Field(default_factory=list, description="Required technical skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Preferred skills")
    experience_level: Optional[str] = Field(None, description="Experience level (junior, mid, senior)")
    responsibilities: List[str] = Field(default_factory=list, description="Key responsibilities")
    company_context: Optional[str] = Field(None, description="Company context and culture")


class EnrichedProfile(BaseModel):
    """Enriched candidate profile from Data Enrichment Service."""
    candidate_id: str = Field(..., description="Unique candidate identifier")
    name: str = Field(..., description="Candidate name")
    email: Optional[str] = Field(None, description="Email address")
    location: Optional[str] = Field(None, description="Location")
    github_url: Optional[str] = Field(None, description="GitHub profile URL")
    
    # Skills and experience
    technical_skills: List[Dict[str, Any]] = Field(default_factory=list, description="Technical skills with confidence scores")
    programming_languages: List[str] = Field(default_factory=list, description="Programming languages")
    frameworks: List[str] = Field(default_factory=list, description="Frameworks and tools")
    experience_years: Optional[float] = Field(None, description="Years of experience")
    
    # GitHub analysis
    github_analysis: Optional[Dict[str, Any]] = Field(None, description="GitHub profile analysis")
    
    # Job relevance
    job_relevance_score: Optional[float] = Field(None, description="Overall job relevance score")
    skill_match_percentage: Optional[float] = Field(None, description="Skill match percentage")
    skill_gaps: List[str] = Field(default_factory=list, description="Identified skill gaps")
    skill_strengths: List[str] = Field(default_factory=list, description="Key skill strengths")


class NarrativeSection(BaseModel):
    """Individual narrative section."""
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")
    confidence_score: Optional[float] = Field(None, description="Confidence in this section")
    evidence_sources: List[str] = Field(default_factory=list, description="Sources of evidence")


class GeneratedNarrative(BaseModel):
    """Complete generated narrative."""
    candidate_id: str = Field(..., description="Candidate identifier")
    job_requirement: JobRequirement = Field(..., description="Job requirement context")
    narrative_style: NarrativeStyle = Field(..., description="Used narrative style")
    
    # Narrative sections
    executive_summary: NarrativeSection = Field(..., description="Executive summary section")
    technical_skills_assessment: NarrativeSection = Field(..., description="Technical skills analysis")
    experience_relevance: NarrativeSection = Field(..., description="Experience relevance to job")
    project_portfolio_analysis: Optional[NarrativeSection] = Field(None, description="Project portfolio analysis")
    growth_potential: NarrativeSection = Field(..., description="Growth potential assessment")
    
    # Metadata
    generation_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    llm_provider: LLMProvider = Field(..., description="LLM provider used")
    model_used: str = Field(..., description="Specific model used")
    generation_parameters: Dict[str, Any] = Field(default_factory=dict, description="Generation parameters")
    
    # Overall assessment
    overall_assessment: str = Field(..., description="Overall candidate assessment")
    recommendation: str = Field(..., description="Hiring recommendation")
    confidence_score: float = Field(..., description="Overall confidence score")


class NarrativeGenerationRequest(BaseModel):
    """Request for narrative generation."""
    candidate_id: str = Field(..., description="Candidate identifier")
    job_requirement: JobRequirement = Field(..., description="Job requirement specification")
    narrative_style: NarrativeStyle = Field(NarrativeStyle.COMPREHENSIVE, description="Desired narrative style")
    llm_provider: Optional[LLMProvider] = Field(None, description="Preferred LLM provider")
    custom_prompts: Optional[Dict[str, str]] = Field(None, description="Custom prompts for sections")
    generation_parameters: Optional[Dict[str, Any]] = Field(None, description="Custom generation parameters")
    
    @validator('narrative_style')
    def validate_narrative_style(cls, v):
        """Validate narrative style."""
        if v not in NarrativeStyle:
            raise ValueError(f"Unsupported narrative style: {v}")
        return v


class NarrativeGenerationResponse(BaseModel):
    """Response from narrative generation."""
    success: bool = Field(..., description="Generation success status")
    narrative: Optional[GeneratedNarrative] = Field(None, description="Generated narrative")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    llm_providers: Dict[str, bool] = Field(..., description="LLM provider availability")
    external_services: Dict[str, bool] = Field(..., description="External service availability")


class ServiceCapabilities(BaseModel):
    """Service capabilities information."""
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    supported_narrative_styles: List[str] = Field(..., description="Supported narrative styles")
    supported_llm_providers: List[str] = Field(..., description="Supported LLM providers")
    max_tokens: int = Field(..., description="Maximum tokens per generation")
    supported_languages: List[str] = Field(default_factory=list, description="Supported languages") 