"""Main FastAPI application for Profile Discovery Service."""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from .core.config import settings
from .core.models import create_error_response
from .api.routes import router
from .utils.logger import setup_logging, get_logger, add_correlation_id

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Profile Discovery Service starting up",
               version=settings.service_version,
               host=settings.host,
               port=settings.port)
    
    yield
    
    # Shutdown
    logger.info("Profile Discovery Service shutting down")


# Create FastAPI application
app = FastAPI(
    title="Profile Discovery Service",
    description="Discovers and validates GitHub and LinkedIn profiles using candidate data",
    version=settings.service_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for request logging and correlation IDs
@app.middleware("http")
async def add_correlation_id_middleware(request: Request, call_next):
    """Add correlation ID to request state."""
    correlation_id = add_correlation_id()
    request.state.request_id = correlation_id
    
    # Add correlation ID to response headers
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    
    return response


@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    """Log all requests and responses."""
    start_time = time.time()
    
    # Log request
    logger.info("Request started",
               method=request.method,
               url=str(request.url),
               client_ip=request.client.host if request.client else None)
    
    # Process request
    response = await call_next(request)
    
    # Log response
    processing_time = (time.time() - start_time) * 1000
    logger.info("Request completed",
               method=request.method,
               url=str(request.url),
               status_code=response.status_code,
               processing_time_ms=processing_time)
    
    return response


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    request_id = getattr(request.state, 'request_id', None)
    
    error_response = create_error_response(
        error_type="http_error",
        message=exc.detail,
        request_id=request_id
    )
    
    logger.error("HTTP error occurred",
                request_id=request_id,
                status_code=exc.status_code,
                detail=exc.detail)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    request_id = getattr(request.state, 'request_id', None)
    
    error_response = create_error_response(
        error_type="internal_error",
        message="An internal server error occurred",
        request_id=request_id
    )
    
    logger.error("Internal error occurred",
                request_id=request_id,
                error=str(exc))
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )


# Include API routes
app.include_router(router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Profile Discovery Service",
        "version": settings.service_version,
        "description": "Discovers and validates GitHub and LinkedIn profiles using candidate data",
        "status": "running",
        "endpoints": {
            "discover": "/api/v1/discover",
            "health": "/api/v1/health",
            "supported_platforms": "/api/v1/supported-platforms",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "profile_discovery.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
