"""Main FastAPI application for Data Enrichment Service."""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from .api.routes import router
from .core.config import settings
from .utils.logger import logger, api_logger


# Service start time
service_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info(
        "Starting Data Enrichment Service",
        version=settings.version,
        host=settings.host,
        port=settings.port,
        debug=settings.debug
    )
    
    # Initialize services here if needed
    # await initialize_database()
    # await initialize_cache()
    
    logger.info("Data Enrichment Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Data Enrichment Service")
    
    # Cleanup services here if needed
    # await cleanup_database()
    # await cleanup_cache()
    
    logger.info("Data Enrichment Service shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Data Enrichment Service",
    description="AI Recruiter Agent - Data Enrichment Service for combining and enriching candidate data",
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
        "service": "Data Enrichment Service",
        "version": settings.version,
        "status": "running",
        "uptime_seconds": uptime_seconds,
        "docs_url": "/docs" if settings.debug else None,
        "health_check": "/api/v1/health",
        "capabilities": "/api/v1/capabilities"
    }


# Health check endpoint (basic)
@app.get("/health")
async def basic_health_check():
    """Basic health check endpoint."""
    
    uptime_seconds = time.time() - service_start_time
    
    return {
        "status": "healthy",
        "service": "Data Enrichment Service",
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
        "service": "Data Enrichment Service",
        "version": settings.version,
        "uptime_seconds": uptime_seconds,
        "start_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(service_start_time)),
        "current_time": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "configuration": {
            "debug": settings.debug,
            "log_level": settings.log_level,
            "min_confidence_threshold": settings.min_confidence_threshold,
            "skill_weighting_factor": settings.skill_weighting_factor,
            "github_analysis_enabled": settings.github_analysis_enabled,
            "linkedin_analysis_enabled": settings.linkedin_analysis_enabled,
            "job_context_enabled": settings.job_context_enabled
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "data_enrichment.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    ) 