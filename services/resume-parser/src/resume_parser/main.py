"""Main FastAPI application for resume parser service."""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from .api.routes import router
from .core.config import get_settings
from src.resume_parser.utils.logger import configure_logging, get_logger

# Configure logging
configure_logging()
logger = get_logger(__name__)

# Global variables for tracking
start_time = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting resume parser service")
    yield
    # Shutdown
    logger.info("Shutting down resume parser service")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="Resume Parser Service",
        description="AI-powered resume parsing microservice for extracting structured data from PDF, DOCX, and TXT files",
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Add trusted host middleware for security
    if settings.allowed_hosts:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts
        )
    
    # Add request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log incoming requests and their processing time."""
        start_time = time.time()
        
        # Log request
        logger.info("Incoming request",
                   method=request.method,
                   url=str(request.url),
                   client_ip=request.client.host if request.client else None)
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info("Request completed",
                   method=request.method,
                   url=str(request.url),
                   status_code=response.status_code,
                   process_time_ms=process_time * 1000)
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    # Include API routes
    app.include_router(router, prefix="/api/v1", tags=["resume-parser"])
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with service information."""
        return {
            "service": "Resume Parser Service",
            "version": "0.1.0",
            "status": "running",
            "uptime_seconds": time.time() - start_time,
            "docs": "/docs" if settings.debug else "Documentation disabled in production"
        }
    
    return app

# Create the application instance
app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    
    logger.info("Starting resume parser service",
                host=settings.host,
                port=settings.port,
                debug=settings.debug)
    
    uvicorn.run(
        "resume_parser.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
