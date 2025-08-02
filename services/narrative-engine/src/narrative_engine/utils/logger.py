"""Logging configuration for Narrative Engine Service."""

import sys
import structlog
from typing import Any, Dict


def setup_logging(log_level: str = "INFO") -> None:
    """Setup structured logging configuration."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


# Create logger instances
logger = get_logger("narrative_engine")
api_logger = get_logger("narrative_engine.api")
llm_logger = get_logger("narrative_engine.llm")
service_logger = get_logger("narrative_engine.service")


def log_api_request(
    method: str,
    path: str,
    request_id: str,
    user_agent: str = None,
    **kwargs: Any
) -> None:
    """Log API request details."""
    api_logger.info(
        "API request received",
        method=method,
        path=path,
        request_id=request_id,
        user_agent=user_agent,
        **kwargs
    )


def log_api_response(
    method: str,
    path: str,
    status_code: int,
    request_id: str,
    processing_time_ms: float = None,
    **kwargs: Any
) -> None:
    """Log API response details."""
    api_logger.info(
        "API response sent",
        method=method,
        path=path,
        status_code=status_code,
        request_id=request_id,
        processing_time_ms=processing_time_ms,
        **kwargs
    )


def log_llm_request(
    provider: str,
    model: str,
    prompt_length: int,
    max_tokens: int,
    temperature: float,
    **kwargs: Any
) -> None:
    """Log LLM request details."""
    llm_logger.info(
        "LLM request sent",
        provider=provider,
        model=model,
        prompt_length=prompt_length,
        max_tokens=max_tokens,
        temperature=temperature,
        **kwargs
    )


def log_llm_response(
    provider: str,
    model: str,
    response_length: int,
    tokens_used: int = None,
    processing_time_ms: float = None,
    **kwargs: Any
) -> None:
    """Log LLM response details."""
    llm_logger.info(
        "LLM response received",
        provider=provider,
        model=model,
        response_length=response_length,
        tokens_used=tokens_used,
        processing_time_ms=processing_time_ms,
        **kwargs
    )


def log_narrative_generation(
    candidate_id: str,
    narrative_style: str,
    llm_provider: str,
    model: str,
    processing_time_ms: float,
    success: bool,
    **kwargs: Any
) -> None:
    """Log narrative generation details."""
    service_logger.info(
        "Narrative generation completed",
        candidate_id=candidate_id,
        narrative_style=narrative_style,
        llm_provider=llm_provider,
        model=model,
        processing_time_ms=processing_time_ms,
        success=success,
        **kwargs
    )


def log_error(
    error_type: str,
    error_message: str,
    context: Dict[str, Any] = None,
    **kwargs: Any
) -> None:
    """Log error details."""
    logger.error(
        "Error occurred",
        error_type=error_type,
        error_message=error_message,
        context=context or {},
        **kwargs
    ) 