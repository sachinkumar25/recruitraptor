"""Logging utilities for Profile Discovery Service."""

import sys
import uuid
from typing import Any, Dict, Optional
import structlog
from structlog.stdlib import LoggerFactory

from ..core.config import settings


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured structured logger
    """
    return structlog.get_logger(name)


def setup_logging() -> None:
    """Configure structured logging for the application."""
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
            structlog.processors.JSONRenderer() if settings.log_format == "json" else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def add_correlation_id() -> str:
    """
    Generate and add correlation ID to log context.
    
    Returns:
        Generated correlation ID
    """
    correlation_id = str(uuid.uuid4())
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
    return correlation_id


def log_request_start(logger: structlog.stdlib.BoundLogger, request_id: str, **kwargs: Any) -> None:
    """Log the start of a request."""
    logger.info("Request started", request_id=request_id, **kwargs)


def log_request_end(logger: structlog.stdlib.BoundLogger, request_id: str, processing_time_ms: float, **kwargs: Any) -> None:
    """Log the end of a request."""
    logger.info("Request completed", 
               request_id=request_id, 
               processing_time_ms=processing_time_ms,
               **kwargs)


def log_discovery_start(logger: structlog.stdlib.BoundLogger, candidate_name: str, **kwargs: Any) -> None:
    """Log the start of profile discovery."""
    logger.info("Profile discovery started", candidate_name=candidate_name, **kwargs)


def log_discovery_result(logger: structlog.stdlib.BoundLogger, 
                        github_count: int, 
                        linkedin_count: int, 
                        processing_time_ms: float,
                        **kwargs: Any) -> None:
    """Log profile discovery results."""
    logger.info("Profile discovery completed",
               github_profiles_found=github_count,
               linkedin_profiles_found=linkedin_count,
               processing_time_ms=processing_time_ms,
               **kwargs)


def log_api_error(logger: structlog.stdlib.BoundLogger, 
                 error: Exception, 
                 context: Optional[Dict[str, Any]] = None) -> None:
    """Log API errors with context."""
    error_context = context or {}
    logger.error("API error occurred",
                error_type=type(error).__name__,
                error_message=str(error),
                **error_context)


def log_rate_limit_warning(logger: structlog.stdlib.BoundLogger, 
                          platform: str, 
                          remaining_requests: int) -> None:
    """Log rate limit warnings."""
    logger.warning("Rate limit approaching",
                  platform=platform,
                  remaining_requests=remaining_requests)
