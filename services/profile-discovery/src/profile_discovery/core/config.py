"""Configuration management for Profile Discovery Service."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Service Settings
    service_name: str = Field(default="profile-discovery", description="Service name")
    service_version: str = Field(default="0.1.0", description="Service version")
    host: str = Field(default="0.0.0.0", description="Service host")
    port: int = Field(default=8001, description="Service port")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # External API Keys
    github_token: Optional[str] = Field(default=None, description="GitHub API token")
    serpapi_key: Optional[str] = Field(default=None, description="SerpAPI key")
    
    # Redis Configuration
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=1, description="Redis database")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    redis_cache_ttl: int = Field(default=86400, description="Cache TTL in seconds (24h)")
    
    # Resume Parser Service
    resume_parser_url: str = Field(default="http://localhost:8000", description="Resume Parser service URL")
    
    # Rate Limiting
    github_rate_limit: int = Field(default=5000, description="GitHub API rate limit per hour")
    serpapi_rate_limit: int = Field(default=100, description="SerpAPI rate limit per month")
    request_timeout: int = Field(default=30, description="Request timeout in seconds")
    
    # Discovery Settings
    max_github_results: int = Field(default=5, description="Maximum GitHub results to return")
    max_linkedin_results: int = Field(default=3, description="Maximum LinkedIn results to return")
    min_confidence_score: float = Field(default=0.3, description="Minimum confidence score")
    max_search_attempts: int = Field(default=3, description="Maximum search attempts")
    
    # Logging
    log_format: str = Field(default="json", description="Log format")
    log_correlation_id: bool = Field(default=True, description="Enable correlation ID logging")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
