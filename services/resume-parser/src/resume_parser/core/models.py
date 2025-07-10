"""Pydantic models for resume parser API requests and responses."""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

class FileType(str, Enum):
    """Supported file types for resume parsing."""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"

class ConfidenceField(BaseModel):
    """Model for fields with confidence scoring."""
    value: Optional[Any] = None
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")

class PersonalInfo(BaseModel):
    """Personal information extracted from resume."""
    name: ConfidenceField = Field(default_factory=lambda: ConfidenceField())
    email: ConfidenceField = Field(default_factory=lambda: ConfidenceField())
    phone: ConfidenceField = Field(default_factory=lambda: ConfidenceField())
    location: ConfidenceField = Field(default_factory=lambda: ConfidenceField())
    linkedin_url: ConfidenceField = Field(default_factory=lambda: ConfidenceField())
    github_url: ConfidenceField = Field(default_factory=lambda: ConfidenceField())
    confidence: float = Field(ge=0.0, le=1.0, description="Overall confidence for personal info section")

class Education(BaseModel):
    """Education information extracted from resume."""
    institutions: List[str] = Field(default_factory=list, description="List of educational institutions")
    degrees: List[str] = Field(default_factory=list, description="List of degrees obtained")
    fields_of_study: List[str] = Field(default_factory=list, description="List of fields of study")
    dates: List[str] = Field(default_factory=list, description="List of education dates")
    gpa: ConfidenceField = Field(default_factory=lambda: ConfidenceField(), description="GPA with confidence")
    confidence: float = Field(ge=0.0, le=1.0, description="Overall confidence for education section")

class Experience(BaseModel):
    """Work experience information extracted from resume."""
    companies: List[str] = Field(default_factory=list, description="List of companies worked for")
    positions: List[str] = Field(default_factory=list, description="List of job positions")
    dates: List[str] = Field(default_factory=list, description="List of employment dates")
    descriptions: List[str] = Field(default_factory=list, description="List of job descriptions")
    confidence: float = Field(ge=0.0, le=1.0, description="Overall confidence for experience section")

class SkillCategories(BaseModel):
    """Categorized skills extracted from resume."""
    programming_languages: List[str] = Field(default_factory=list, description="Programming languages")
    frameworks: List[str] = Field(default_factory=list, description="Frameworks and libraries")
    databases: List[str] = Field(default_factory=list, description="Databases and data stores")
    cloud_platforms: List[str] = Field(default_factory=list, description="Cloud platforms and tools")
    tools: List[str] = Field(default_factory=list, description="Other tools and technologies")

class Skills(BaseModel):
    """Skills information extracted from resume."""
    technical_skills: List[str] = Field(default_factory=list, description="All technical skills found")
    soft_skills: List[str] = Field(default_factory=list, description="Soft skills and competencies")
    categories: SkillCategories = Field(default_factory=SkillCategories, description="Categorized skills")
    confidence: float = Field(ge=0.0, le=1.0, description="Overall confidence for skills section")

class ParsingMetadata(BaseModel):
    """Metadata about the parsing process."""
    total_words: int = Field(description="Total number of words in the resume")
    parsing_timestamp: str = Field(description="ISO timestamp of when parsing occurred")
    confidence_overall: float = Field(ge=0.0, le=1.0, description="Overall confidence score")
    extraction_method: Optional[str] = Field(description="Method used for text extraction")
    encoding: Optional[str] = Field(description="Text encoding detected")
    word_count: int = Field(description="Number of words extracted")
    extraction_errors: List[str] = Field(default_factory=list, description="Any errors during extraction")

class ParsedResume(BaseModel):
    """Complete parsed resume data."""
    personal_info: PersonalInfo = Field(description="Personal information section")
    education: Education = Field(description="Education information section")
    experience: Experience = Field(description="Work experience section")
    skills: Skills = Field(description="Skills section")
    metadata: ParsingMetadata = Field(description="Parsing metadata")

class ResumeUploadRequest(BaseModel):
    """Request model for resume upload endpoint."""
    file_content: bytes = Field(description="Raw file content")
    file_type: FileType = Field(description="Type of uploaded file")
    filename: Optional[str] = Field(None, description="Original filename")

class ResumeUploadResponse(BaseModel):
    """Response model for resume upload endpoint."""
    success: bool = Field(description="Whether parsing was successful")
    parsed_data: Optional[ParsedResume] = Field(None, description="Parsed resume data")
    error_message: Optional[str] = Field(None, description="Error message if parsing failed")
    processing_time_ms: float = Field(description="Time taken to process the resume in milliseconds")
    file_metadata: Optional[Dict[str, Any]] = Field(None, description="File processing metadata")

class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(description="Service status")
    timestamp: str = Field(description="Current timestamp")
    version: str = Field(description="Service version")
    uptime_seconds: float = Field(description="Service uptime in seconds")

class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str = Field(description="Error type")
    message: str = Field(description="Detailed error message")
    timestamp: str = Field(description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")

class ValidationError(BaseModel):
    """Validation error details."""
    field: str = Field(description="Field that failed validation")
    message: str = Field(description="Validation error message")
    value: Optional[Any] = Field(None, description="Value that failed validation")

class ValidationErrorResponse(BaseModel):
    """Response model for validation errors."""
    error: str = Field(default="validation_error", description="Error type")
    message: str = Field(description="Validation error summary")
    details: List[ValidationError] = Field(description="List of validation errors")
    timestamp: str = Field(description="Error timestamp")

# Validators
class ParsedResumeValidator:
    """Custom validators for ParsedResume model."""
    
    @validator('metadata')
    def validate_metadata(cls, v):
        """Validate metadata fields."""
        if v.total_words < 0:
            raise ValueError("Total words cannot be negative")
        if v.confidence_overall < 0 or v.confidence_overall > 1:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v
    
    @validator('personal_info', 'education', 'experience', 'skills')
    def validate_section_confidence(cls, v):
        """Validate section confidence scores."""
        if hasattr(v, 'confidence') and (v.confidence < 0 or v.confidence > 1):
            raise ValueError("Section confidence must be between 0.0 and 1.0")
        return v

# Utility functions
def create_error_response(error_type: str, message: str, request_id: Optional[str] = None) -> ErrorResponse:
    """Create a standardized error response."""
    return ErrorResponse(
        error=error_type,
        message=message,
        timestamp=datetime.now().isoformat(),
        request_id=request_id
    )

def create_validation_error_response(errors: List[ValidationError]) -> ValidationErrorResponse:
    """Create a validation error response."""
    return ValidationErrorResponse(
        message="Validation failed for one or more fields",
        details=errors,
        timestamp=datetime.now().isoformat()
    )

def create_health_response(version: str, uptime_seconds: float) -> HealthCheckResponse:
    """Create a health check response."""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version=version,
        uptime_seconds=uptime_seconds
    )
