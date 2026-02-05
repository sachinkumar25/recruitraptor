"""Configuration settings for Narrative Engine Service."""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Service Configuration
    version: str = "0.1.0"
    debug: bool = Field(default=False, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8003, env="PORT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # LLM Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    default_llm_provider: str = Field(default="openai", env="DEFAULT_LLM_PROVIDER")
    default_model: str = Field(default="gpt-4", env="DEFAULT_MODEL")
    
    # External Services
    data_enrichment_url: str = Field(
        default="http://localhost:8002", 
        env="DATA_ENRICHMENT_URL"
    )
    
    # Generation Configuration
    max_tokens: int = Field(default=2000, env="MAX_TOKENS")
    temperature: float = Field(default=0.7, env="TEMPERATURE")
    narrative_style: str = Field(default="comprehensive", env="NARRATIVE_STYLE")
    
    # Supported narrative styles
    supported_styles: List[str] = [
        "executive", "technical", "comprehensive", "concise"
    ]
    
    # Narrative structure templates
    narrative_sections: List[str] = [
        "executive_summary",
        "technical_skills_assessment", 
        "experience_relevance",
        "project_portfolio_analysis",
        "growth_potential"
    ]
    
    # CORS Configuration
    cors_origins: List[str] = [
        "http://localhost:3000",  # Frontend (Next.js)
        "http://localhost:3001",  # Frontend (alternate port)
        "http://localhost:8000",  # Resume Parser
        "http://localhost:8001",  # Profile Discovery
        "http://localhost:8002",  # Data Enrichment
        "*",  # Allow all origins for development
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings() 