"""Configuration settings for Data Enrichment Service."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""
    
    # Service Configuration
    service_name: str = "data-enrichment"
    version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8002, env="PORT")
    
    # Database Configuration
    database_url: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/recruitraptor",
        env="DATABASE_URL"
    )
    database_pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # Enrichment Configuration
    min_confidence_threshold: float = Field(default=0.3, env="MIN_CONFIDENCE_THRESHOLD")
    skill_weighting_factor: float = Field(default=0.7, env="SKILL_WEIGHTING_FACTOR")
    max_skill_proficiency_years: float = Field(default=10.0, env="MAX_SKILL_PROFICIENCY_YEARS")
    recent_activity_days: int = Field(default=365, env="RECENT_ACTIVITY_DAYS")
    
    # External Service URLs
    resume_parser_url: str = Field(
        default="http://localhost:8000",
        env="RESUME_PARSER_URL"
    )
    profile_discovery_url: str = Field(
        default="http://localhost:8001",
        env="PROFILE_DISCOVERY_URL"
    )
    narrative_engine_url: str = Field(
        default="http://localhost:8003",
        env="NARRATIVE_ENGINE_URL"
    )
    
    # API Configuration
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")
    cors_origins: list = Field(default=["*"], env="CORS_ORIGINS")
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
    
    # Cache Configuration
    cache_enabled: bool = Field(default=True, env="CACHE_ENABLED")
    cache_ttl_seconds: int = Field(default=3600, env="CACHE_TTL_SECONDS")
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=3600, env="RATE_LIMIT_WINDOW")
    
    # Security
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Monitoring
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    
    # Conflict Resolution
    default_conflict_resolution: str = Field(
        default="highest_confidence",
        env="DEFAULT_CONFLICT_RESOLUTION"
    )
    resume_priority_weight: float = Field(default=0.6, env="RESUME_PRIORITY_WEIGHT")
    github_priority_weight: float = Field(default=0.4, env="GITHUB_PRIORITY_WEIGHT")
    
    # Skill Analysis
    skill_proficiency_thresholds: dict = Field(
        default={
            "beginner": 0.3,
            "intermediate": 0.6,
            "advanced": 0.8,
            "expert": 0.9
        },
        env="SKILL_PROFICIENCY_THRESHOLDS"
    )
    
    # GitHub Analysis
    github_analysis_enabled: bool = Field(default=True, env="GITHUB_ANALYSIS_ENABLED")
    github_api_rate_limit: int = Field(default=5000, env="GITHUB_API_RATE_LIMIT")
    github_repo_analysis_depth: int = Field(default=50, env="GITHUB_REPO_ANALYSIS_DEPTH")
    
    # LinkedIn Analysis
    linkedin_analysis_enabled: bool = Field(default=True, env="LINKEDIN_ANALYSIS_ENABLED")
    
    # Job Context
    job_context_enabled: bool = Field(default=True, env="JOB_CONTEXT_ENABLED")
    skill_matching_threshold: float = Field(default=0.7, env="SKILL_MATCHING_THRESHOLD")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


def validate_settings() -> None:
    """Validate critical settings."""
    if not settings.database_url:
        raise ValueError("DATABASE_URL is required")
    
    if settings.min_confidence_threshold < 0 or settings.min_confidence_threshold > 1:
        raise ValueError("MIN_CONFIDENCE_THRESHOLD must be between 0 and 1")
    
    if settings.skill_weighting_factor < 0 or settings.skill_weighting_factor > 1:
        raise ValueError("SKILL_WEIGHTING_FACTOR must be between 0 and 1")
    
    if settings.resume_priority_weight + settings.github_priority_weight != 1.0:
        raise ValueError("Priority weights must sum to 1.0")


# Validate settings on import
try:
    validate_settings()
except ValueError as e:
    print(f"Configuration error: {e}")
    raise 