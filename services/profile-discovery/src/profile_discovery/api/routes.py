"""API routes for Profile Discovery Service."""

import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
import structlog

from ..core.models import (
    DiscoveryRequest, DiscoveryResponse, HealthCheckResponse,
    SupportedPlatformsResponse, PlatformType, DiscoveryStrategy,
    create_error_response, create_health_response
)
from ..core.config import settings
from ..services.discovery_service import DiscoveryService
from ..utils.logger import get_logger, add_correlation_id, log_request_start, log_request_end

logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["profile-discovery"])

# Global service instance
discovery_service = None


def get_discovery_service() -> DiscoveryService:
    """Get or create discovery service instance."""
    global discovery_service
    if discovery_service is None:
        discovery_service = DiscoveryService()
    return discovery_service


@router.post("/discover", response_model=DiscoveryResponse)
async def discover_profiles(
    request: DiscoveryRequest,
    discovery_service: DiscoveryService = Depends(get_discovery_service)
) -> DiscoveryResponse:
    """
    Discover GitHub and LinkedIn profiles for a candidate.
    
    Args:
        request: Discovery request with candidate data
        discovery_service: Discovery service instance
        
    Returns:
        Discovery response with found profiles
    """
    start_time = time.time()
    request_id = add_correlation_id()
    
    try:
        log_request_start(logger, request_id, 
                         candidate_name=request.candidate_data.personal_info.name.value)
        
        # Validate request
        if not request.candidate_data.personal_info.name.value:
            raise HTTPException(status_code=400, detail="Candidate name is required")
        
        # Perform discovery
        response = await discovery_service.discover_profiles(request)
        
        # Log completion
        processing_time = (time.time() - start_time) * 1000
        log_request_end(logger, request_id, processing_time,
                       github_count=len(response.github_profiles),
                       linkedin_count=len(response.linkedin_profiles))
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Profile discovery failed", 
                    request_id=request_id,
                    error=str(e))
        # Return 400 for validation-like errors to help debugging
        if "required" in str(e).lower() or "validation" in str(e).lower():
             raise HTTPException(status_code=400, detail=f"Validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Discovery failed: {str(e)}")


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(
    discovery_service: DiscoveryService = Depends(get_discovery_service)
) -> HealthCheckResponse:
    """
    Health check endpoint.
    
    Returns:
        Health status of the service and external dependencies
    """
    try:
        # Get external service health
        external_services = await discovery_service.get_health_status()
        
        # Calculate uptime (simplified)
        uptime_seconds = 0.0  # In production, track actual uptime
        
        return create_health_response(
            version=settings.service_version,
            uptime_seconds=uptime_seconds,
            external_services=external_services
        )
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=500, detail="Health check failed")


@router.get("/supported-platforms", response_model=SupportedPlatformsResponse)
async def get_supported_platforms() -> SupportedPlatformsResponse:
    """
    Get supported platforms and discovery strategies.
    
    Returns:
        Information about supported platforms and strategies
    """
    return SupportedPlatformsResponse(
        platforms=[PlatformType.GITHUB, PlatformType.LINKEDIN],
        discovery_strategies=[
            DiscoveryStrategy.EMAIL_BASED,
            DiscoveryStrategy.NAME_CONTEXT,
            DiscoveryStrategy.FUZZY_MATCHING,
            DiscoveryStrategy.SEARCH_ENGINE
        ],
        rate_limits={
            "github": {
                "requests_per_hour": settings.github_rate_limit,
                "description": "GitHub API rate limit"
            },
            "linkedin": {
                "requests_per_month": settings.serpapi_rate_limit,
                "description": "SerpAPI monthly search limit"
            }
        }
    )


@router.get("/")
async def root() -> Dict[str, Any]:
    """
    Root endpoint with service information.
    
    Returns:
        Service information and available endpoints
    """
    return {
        "service": "Profile Discovery Service",
        "version": settings.service_version,
        "description": "Discovers and validates GitHub and LinkedIn profiles using candidate data",
        "endpoints": {
            "discover": "/api/v1/discover",
            "health": "/api/v1/health",
            "supported_platforms": "/api/v1/supported-platforms"
        },
        "documentation": "/docs"
    }


# Note: Exception handlers should be added to the main FastAPI app, not the router
