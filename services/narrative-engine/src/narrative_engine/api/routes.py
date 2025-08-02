"""API routes for Narrative Engine Service."""

import time
import httpx
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse

from ..core.config import settings
from ..core.models import (
    NarrativeGenerationRequest, NarrativeGenerationResponse,
    HealthCheckResponse, ServiceCapabilities, LLMProvider, NarrativeStyle
)
from ..services.narrative_service import narrative_service
from ..services.llm_service import llm_service
from ..utils.logger import api_logger, log_api_request, log_api_response, log_error

router = APIRouter(prefix="/api/v1", tags=["narrative"])


async def get_request_id(request: Request) -> str:
    """Extract request ID from headers or generate one."""
    return request.headers.get("X-Request-ID", f"req_{int(time.time() * 1000)}")


@router.post("/generate", response_model=NarrativeGenerationResponse)
async def generate_narrative(
    request: NarrativeGenerationRequest,
    http_request: Request,
    request_id: str = Depends(get_request_id)
):
    """Generate AI-powered candidate narrative."""
    
    start_time = time.time()
    
    # Log incoming request
    log_api_request(
        method=http_request.method,
        path=str(http_request.url.path),
        request_id=request_id,
        user_agent=http_request.headers.get("User-Agent")
    )
    
    try:
        # Fetch enriched profile from Data Enrichment Service
        enriched_profile = await _fetch_enriched_profile(request.candidate_id)
        
        # Generate narrative
        narrative = await narrative_service.generate_narrative(
            request=request,
            enriched_profile=enriched_profile
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        # Log successful response
        log_api_response(
            method=http_request.method,
            path=str(http_request.url.path),
            status_code=200,
            request_id=request_id,
            processing_time_ms=processing_time
        )
        
        return NarrativeGenerationResponse(
            success=True,
            narrative=narrative,
            processing_time_ms=processing_time
        )
        
    except httpx.HTTPStatusError as e:
        processing_time = (time.time() - start_time) * 1000
        error_msg = f"External service error: {e.response.status_code}"
        
        log_error(
            "external_service_error",
            error_msg,
            context={
                "request_id": request_id,
                "status_code": e.response.status_code,
                "processing_time_ms": processing_time
            }
        )
        
        log_api_response(
            method=http_request.method,
            path=str(http_request.url.path),
            status_code=503,
            request_id=request_id,
            processing_time_ms=processing_time
        )
        
        raise HTTPException(
            status_code=503,
            detail=f"Data Enrichment Service unavailable: {error_msg}"
        )
        
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        error_msg = f"Narrative generation failed: {str(e)}"
        
        log_error(
            "narrative_generation_error",
            error_msg,
            context={
                "request_id": request_id,
                "candidate_id": request.candidate_id,
                "processing_time_ms": processing_time
            }
        )
        
        log_api_response(
            method=http_request.method,
            path=str(http_request.url.path),
            status_code=500,
            request_id=request_id,
            processing_time_ms=processing_time
        )
        
        return NarrativeGenerationResponse(
            success=False,
            error_message=error_msg,
            processing_time_ms=processing_time
        )


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    
    # Check LLM providers
    llm_providers = {}
    for provider in LLMProvider:
        llm_providers[provider.value] = llm_service.test_provider_connectivity(provider)
    
    # Check external services
    external_services = {}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.data_enrichment_url}/health")
            external_services["data_enrichment"] = response.status_code == 200
    except Exception:
        external_services["data_enrichment"] = False
    
    # Determine overall status
    all_llm_available = any(llm_providers.values())
    all_external_available = all(external_services.values())
    
    status = "healthy" if (all_llm_available and all_external_available) else "degraded"
    
    return HealthCheckResponse(
        status=status,
        service="Narrative Engine Service",
        version=settings.version,
        llm_providers=llm_providers,
        external_services=external_services
    )


@router.get("/capabilities", response_model=ServiceCapabilities)
async def get_capabilities():
    """Get service capabilities."""
    
    return ServiceCapabilities(
        service="Narrative Engine Service",
        version=settings.version,
        supported_narrative_styles=[style.value for style in NarrativeStyle],
        supported_llm_providers=[provider.value for provider in LLMProvider],
        max_tokens=settings.max_tokens,
        supported_languages=["English"]  # Can be extended for multi-language support
    )


@router.get("/styles")
async def get_narrative_styles():
    """Get available narrative styles with descriptions."""
    
    styles = {
        "executive": {
            "description": "High-level executive summary for C-suite audience",
            "focus": ["strategic impact", "leadership potential", "business value"],
            "length": "concise",
            "audience": "executive leadership"
        },
        "technical": {
            "description": "Detailed technical assessment for engineering managers",
            "focus": ["technical depth", "problem-solving", "technical leadership"],
            "length": "detailed",
            "audience": "engineering managers"
        },
        "comprehensive": {
            "description": "Balanced assessment covering technical skills, cultural fit, and growth potential",
            "focus": ["technical skills", "cultural fit", "growth potential"],
            "length": "comprehensive",
            "audience": "talent acquisition specialists"
        },
        "concise": {
            "description": "Brief assessment for initial screening",
            "focus": ["key qualifications", "red flags", "next steps"],
            "length": "brief",
            "audience": "recruiters"
        }
    }
    
    return {
        "styles": styles,
        "default_style": settings.narrative_style
    }


@router.get("/providers")
async def get_llm_providers():
    """Get available LLM providers and their status."""
    
    providers = {}
    for provider in LLMProvider:
        is_available = llm_service.test_provider_connectivity(provider)
        providers[provider.value] = {
            "available": is_available,
            "default_model": settings.default_model if provider.value == settings.default_llm_provider else None
        }
    
    return {
        "providers": providers,
        "default_provider": settings.default_llm_provider
    }


async def _fetch_enriched_profile(candidate_id: str) -> Dict[str, Any]:
    """Fetch enriched profile from Data Enrichment Service."""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{settings.data_enrichment_url}/api/v1/profiles/{candidate_id}"
        )
        response.raise_for_status()
        return response.json()


# Note: Exception handling is done at the app level in main.py 