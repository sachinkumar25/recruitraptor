"""Main FastAPI application for Narrative Engine Service."""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from .api.routes import router
from .core.config import settings
from .utils.logger import setup_logging, logger, api_logger
from .services.narrative_service import narrative_service


# Service start time
service_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info(
        "Starting Narrative Engine Service",
        version=settings.version,
        host=settings.host,
        port=settings.port,
        debug=settings.debug
    )
    
    # Setup logging
    setup_logging(settings.log_level)
    
    # Initialize services
    logger.info("Initializing LLM service...")
    from .services.llm_service import llm_service
    available_providers = llm_service.get_available_providers()
    logger.info(f"Available LLM providers: {available_providers}")
    
    logger.info("Narrative Engine Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Narrative Engine Service")
    
    # Cleanup services
    await narrative_service.close()
    
    logger.info("Narrative Engine Service shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Narrative Engine Service",
    description="AI Recruiter Agent - AI-powered narrative generation for candidate assessments",
    version=settings.version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure appropriately for production
    )

# Include API routes
app.include_router(router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    
    logger.error(
        "Unhandled global exception",
        error_type=type(exc).__name__,
        error_message=str(exc),
        request_path=str(request.url),
        request_method=request.method
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "An unexpected error occurred",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "request_id": str(request.url)
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    
    uptime_seconds = time.time() - service_start_time
    
    return {
        "service": "Narrative Engine Service",
        "version": settings.version,
        "status": "running",
        "uptime_seconds": uptime_seconds,
        "docs_url": "/docs" if settings.debug else None,
        "health_check": "/api/v1/health",
        "capabilities": "/api/v1/capabilities",
        "pipeline_position": "final",
        "description": "AI-powered narrative generation for candidate assessments"
    }


# Health check endpoint (basic)
@app.get("/health")
async def basic_health_check():
    """Basic health check endpoint."""
    
    uptime_seconds = time.time() - service_start_time
    
    return {
        "status": "healthy",
        "service": "Narrative Engine Service",
        "version": settings.version,
        "uptime_seconds": uptime_seconds,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }


# Metrics endpoint (basic)
@app.get("/metrics")
async def basic_metrics():
    """Basic metrics endpoint."""
    
    uptime_seconds = time.time() - service_start_time
    
    return {
        "service": "Narrative Engine Service",
        "version": settings.version,
        "uptime_seconds": uptime_seconds,
        "start_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(service_start_time)),
        "current_time": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "configuration": {
            "debug": settings.debug,
            "log_level": settings.log_level,
            "default_llm_provider": settings.default_llm_provider,
            "default_model": settings.default_model,
            "max_tokens": settings.max_tokens,
            "temperature": settings.temperature,
            "narrative_style": settings.narrative_style,
            "data_enrichment_url": settings.data_enrichment_url
        },
        "llm_providers": {
            "openai": settings.openai_api_key is not None and settings.openai_api_key != "your_openai_key_here",
            "anthropic": settings.anthropic_api_key is not None and settings.anthropic_api_key != "your_anthropic_key_here"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "narrative_engine.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    ) 