"""API routes for Data Enrichment Service."""

import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse

from ..core.models import (
    EnrichmentRequest,
    EnrichmentResponse,
    HealthCheckResponse,
    ErrorResponse,
    create_error_response,
    create_health_response
)
from ..services.enrichment_service import EnrichmentService
from ..core.config import settings
from ..utils.logger import api_logger, logger

# Create router
router = APIRouter(prefix=settings.api_prefix)

# Service instance
enrichment_service = EnrichmentService()

# Service start time for uptime calculation
service_start_time = time.time()


@router.post("/enrich", response_model=EnrichmentResponse)
async def enrich_candidate_data(
    request: EnrichmentRequest,
    http_request: Request
):
    """Enrich candidate data by combining resume and profile discovery data."""
    
    start_time = time.time()
    
    # Log incoming request
    api_logger.log_request(
        method=http_request.method,
        path=str(http_request.url.path),
        client_ip=http_request.client.host if http_request.client else "unknown"
    )
    
    try:
        # Validate request
        validation_errors = await enrichment_service.validate_enrichment_request(request)
        if validation_errors:
            error_response = create_error_response(
                error_type="validation_error",
                message="Request validation failed",
                request_id=str(http_request.url)
            )
            api_logger.log_error(
                error=Exception("Validation failed"),
                method=http_request.method,
                path=str(http_request.url.path)
            )
            raise HTTPException(status_code=400, detail=error_response.dict())
        
        # Perform enrichment
        response = await enrichment_service.enrich_candidate_data(request)
        
        # Log response
        processing_time_ms = (time.time() - start_time) * 1000
        api_logger.log_response(
            method=http_request.method,
            path=str(http_request.url.path),
            status_code=200 if response.success else 500,
            duration_ms=processing_time_ms
        )
        
        if not response.success:
            raise HTTPException(status_code=500, detail=response.error_message)
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors
        processing_time_ms = (time.time() - start_time) * 1000
        api_logger.log_error(
            error=e,
            method=http_request.method,
            path=str(http_request.url.path)
        )
        
        logger.error(
            "Unexpected error in enrichment endpoint",
            error_type=type(e).__name__,
            error_message=str(e),
            processing_time_ms=processing_time_ms
        )
        
        error_response = create_error_response(
            error_type="internal_error",
            message="An unexpected error occurred during enrichment",
            request_id=str(http_request.url)
        )
        
        raise HTTPException(status_code=500, detail=error_response.dict())


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    
    try:
        # Calculate uptime
        uptime_seconds = time.time() - service_start_time
        
        # Check database status (would be implemented with actual database check)
        database_status = "healthy"  # Placeholder
        
        # Check external services
        external_services = {
            "resume_parser": "healthy",  # Would check actual service
            "profile_discovery": "healthy",  # Would check actual service
            "database": database_status
        }
        
        health_response = create_health_response(
            version=settings.version,
            uptime_seconds=uptime_seconds,
            database_status=database_status,
            external_services=external_services
        )
        
        return health_response
        
    except Exception as e:
        logger.error(
            "Health check failed",
            error_type=type(e).__name__,
            error_message=str(e)
        )
        
        # Return unhealthy status
        return HealthCheckResponse(
            status="unhealthy",
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            version=settings.version,
            uptime_seconds=time.time() - service_start_time,
            database_status="unknown",
            external_services={"error": str(e)}
        )


@router.get("/statistics")
async def get_statistics():
    """Get enrichment service statistics."""
    
    try:
        stats = await enrichment_service.get_enrichment_statistics()
        return stats
        
    except Exception as e:
        logger.error(
            "Failed to get statistics",
            error_type=type(e).__name__,
            error_message=str(e)
        )
        
        error_response = create_error_response(
            error_type="statistics_error",
            message="Failed to retrieve service statistics"
        )
        
        raise HTTPException(status_code=500, detail=error_response.dict())


@router.get("/config")
async def get_configuration():
    """Get service configuration (non-sensitive)."""
    
    try:
        config = {
            "service_name": settings.service_name,
            "version": settings.version,
            "min_confidence_threshold": settings.min_confidence_threshold,
            "skill_weighting_factor": settings.skill_weighting_factor,
            "recent_activity_days": settings.recent_activity_days,
            "max_skill_proficiency_years": settings.max_skill_proficiency_years,
            "github_analysis_enabled": settings.github_analysis_enabled,
            "linkedin_analysis_enabled": settings.linkedin_analysis_enabled,
            "job_context_enabled": settings.job_context_enabled,
            "default_conflict_resolution": settings.default_conflict_resolution,
            "resume_priority_weight": settings.resume_priority_weight,
            "github_priority_weight": settings.github_priority_weight
        }
        
        return config
        
    except Exception as e:
        logger.error(
            "Failed to get configuration",
            error_type=type(e).__name__,
            error_message=str(e)
        )
        
        error_response = create_error_response(
            error_type="config_error",
            message="Failed to retrieve service configuration"
        )
        
        raise HTTPException(status_code=500, detail=error_response.dict())


@router.post("/validate")
async def validate_enrichment_request(request: EnrichmentRequest):
    """Validate an enrichment request without processing it."""
    
    try:
        validation_errors = await enrichment_service.validate_enrichment_request(request)
        
        return {
            "valid": len(validation_errors) == 0,
            "errors": validation_errors,
            "error_count": len(validation_errors)
        }
        
    except Exception as e:
        logger.error(
            "Validation failed",
            error_type=type(e).__name__,
            error_message=str(e)
        )
        
        error_response = create_error_response(
            error_type="validation_error",
            message="Failed to validate request"
        )
        
        raise HTTPException(status_code=500, detail=error_response.dict())


@router.get("/capabilities")
async def get_capabilities():
    """Get service capabilities and supported features."""
    
    try:
        capabilities = {
            "service_name": settings.service_name,
            "version": settings.version,
            "supported_data_sources": [
                "resume_parser",
                "github_profiles",
                "linkedin_profiles"
            ],
            "supported_algorithms": [
                "data_integration",
                "skill_analysis",
                "conflict_resolution",
                "job_matching",
                "proficiency_calculation",
                "experience_analysis"
            ],
            "supported_skill_categories": [
                "programming_languages",
                "frameworks",
                "databases",
                "cloud_platforms",
                "tools"
            ],
            "supported_proficiency_levels": [
                "beginner",
                "intermediate",
                "advanced",
                "expert"
            ],
            "conflict_resolution_strategies": [
                "resume_priority",
                "github_priority",
                "highest_confidence",
                "merge",
                "manual_review"
            ],
            "job_matching_features": [
                "skill_match_percentage",
                "job_relevance_score",
                "skill_gap_analysis",
                "strength_identification"
            ]
        }
        
        return capabilities
        
    except Exception as e:
        logger.error(
            "Failed to get capabilities",
            error_type=type(e).__name__,
            error_message=str(e)
        )
        
        error_response = create_error_response(
            error_type="capabilities_error",
            message="Failed to retrieve service capabilities"
        )
        
        raise HTTPException(status_code=500, detail=error_response.dict())


# Note: Exception handlers are defined in main.py for the app level 