"""Structured logging configuration for Data Enrichment Service."""

import sys
import logging
from typing import Any, Dict, Optional
import structlog
from structlog.stdlib import LoggerFactory
from structlog.processors import JSONRenderer, TimeStamper, add_log_level
from structlog.types import Processor

from ..core.config import settings


def configure_logging() -> None:
    """Configure structured logging for the application."""
    
    # Configure standard library logging
    logging.basicConfig(
        format=settings.log_format,
        level=getattr(logging, settings.log_level.upper()),
        stream=sys.stdout
    )
    
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
            JSONRenderer() if settings.debug else structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class EnrichmentLogger:
    """Specialized logger for enrichment operations."""
    
    def __init__(self, operation: str, candidate_id: Optional[str] = None):
        """Initialize enrichment logger."""
        self.logger = get_logger("enrichment")
        self.operation = operation
        self.candidate_id = candidate_id
        self.context = {
            "operation": operation,
            "candidate_id": candidate_id,
            "service": "data-enrichment"
        }
    
    def log_start(self, **kwargs) -> None:
        """Log the start of an enrichment operation."""
        self.logger.info(
            "Enrichment operation started",
            **self.context,
            **kwargs
        )
    
    def log_success(self, processing_time_ms: float, **kwargs) -> None:
        """Log successful completion of enrichment."""
        self.logger.info(
            "Enrichment operation completed successfully",
            **self.context,
            processing_time_ms=processing_time_ms,
            **kwargs
        )
    
    def log_error(self, error: Exception, **kwargs) -> None:
        """Log enrichment error."""
        self.logger.error(
            "Enrichment operation failed",
            **self.context,
            error_type=type(error).__name__,
            error_message=str(error),
            **kwargs
        )
    
    def log_conflict_resolution(self, field: str, resolution: str, **kwargs) -> None:
        """Log conflict resolution."""
        self.logger.info(
            "Conflict resolved",
            **self.context,
            field=field,
            resolution=resolution,
            **kwargs
        )
    
    def log_skill_analysis(self, skill: str, proficiency: str, confidence: float, **kwargs) -> None:
        """Log skill analysis results."""
        self.logger.info(
            "Skill analyzed",
            **self.context,
            skill=skill,
            proficiency=proficiency,
            confidence=confidence,
            **kwargs
        )
    
    def log_data_source_processing(self, source: str, record_count: int, **kwargs) -> None:
        """Log data source processing."""
        self.logger.info(
            "Data source processed",
            **self.context,
            source=source,
            record_count=record_count,
            **kwargs
        )
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = "ms", **kwargs) -> None:
        """Log performance metrics."""
        self.logger.info(
            "Performance metric",
            **self.context,
            metric_name=metric_name,
            value=value,
            unit=unit,
            **kwargs
        )


class DatabaseLogger:
    """Specialized logger for database operations."""
    
    def __init__(self):
        """Initialize database logger."""
        self.logger = get_logger("database")
    
    def log_connection(self, status: str, **kwargs) -> None:
        """Log database connection status."""
        self.logger.info(
            "Database connection",
            status=status,
            **kwargs
        )
    
    def log_query(self, query_type: str, table: str, duration_ms: float, **kwargs) -> None:
        """Log database query execution."""
        self.logger.info(
            "Database query executed",
            query_type=query_type,
            table=table,
            duration_ms=duration_ms,
            **kwargs
        )
    
    def log_error(self, error: Exception, operation: str, **kwargs) -> None:
        """Log database error."""
        self.logger.error(
            "Database operation failed",
            operation=operation,
            error_type=type(error).__name__,
            error_message=str(error),
            **kwargs
        )


class APILogger:
    """Specialized logger for API operations."""
    
    def __init__(self):
        """Initialize API logger."""
        self.logger = get_logger("api")
    
    def log_request(self, method: str, path: str, client_ip: str, **kwargs) -> None:
        """Log incoming API request."""
        self.logger.info(
            "API request received",
            method=method,
            path=path,
            client_ip=client_ip,
            **kwargs
        )
    
    def log_response(self, method: str, path: str, status_code: int, duration_ms: float, **kwargs) -> None:
        """Log API response."""
        self.logger.info(
            "API response sent",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            **kwargs
        )
    
    def log_error(self, error: Exception, method: str, path: str, **kwargs) -> None:
        """Log API error."""
        self.logger.error(
            "API error occurred",
            method=method,
            path=path,
            error_type=type(error).__name__,
            error_message=str(error),
            **kwargs
        )


# Initialize logging on module import
configure_logging()

# Create default loggers
logger = get_logger("data_enrichment")
db_logger = DatabaseLogger()
api_logger = APILogger() 