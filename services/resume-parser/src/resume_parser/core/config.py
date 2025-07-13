"""Configuration management for resume parser service."""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")
    
    # CORS settings
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins"
    )
    allowed_hosts: Optional[List[str]] = Field(
        default=None,
        description="Allowed hosts for security"
    )
    
    # File processing settings
    max_file_size_mb: int = Field(default=5, description="Maximum file size in MB")
    min_word_count: int = Field(default=100, description="Minimum word count requirement")
    min_content_words: int = Field(default=100, description="Minimum content words requirement")
    processing_timeout_seconds: int = Field(default=300, description="Processing timeout in seconds")
    
    # Parsing settings
    confidence_threshold: float = Field(default=0.5, description="Minimum confidence threshold for extracted fields")
    
    # External API settings
    github_token: Optional[str] = Field(default=None, description="GitHub API token")
    serpapi_key: Optional[str] = Field(default=None, description="SerpAPI key for web search")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    
    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    
    # spaCy model settings
    spacy_model: str = Field(default="en_core_web_sm", description="spaCy model to use")
    
    # API settings
    api_prefix: str = Field(default="/api/v1", description="API prefix")
    docs_url: Optional[str] = Field(default="/docs", description="API documentation URL")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get application settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def reload_settings() -> Settings:
    """Reload settings from environment variables."""
    global _settings
    _settings = Settings()
    return _settings
