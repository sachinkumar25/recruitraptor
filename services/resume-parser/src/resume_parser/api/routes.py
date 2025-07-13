"""FastAPI routes for resume parser service."""

import time
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse

from ..core.extractor import TextExtractor
from ..core.parser import ResumeParser
from ..core.models import (
    ResumeUploadResponse, HealthCheckResponse, ErrorResponse,
    create_error_response, create_health_response, FileType
)
from ..utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Initialize components
text_extractor = TextExtractor()
resume_parser = ResumeParser()

def get_request_id() -> str:
    """Generate a unique request ID for tracking."""
    return str(uuid.uuid4())

@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    request_id: str = Depends(get_request_id)
) -> ResumeUploadResponse:
    """
    Upload and parse a resume file.
    
    Args:
        file: Uploaded resume file (PDF, DOCX, or TXT)
        request_id: Unique request identifier
        
    Returns:
        Parsed resume data with confidence scores
        
    Raises:
        HTTPException: For validation or processing errors
    """
    start_time = time.time()
    
    logger.info("Resume upload request received", 
                filename=file.filename, 
                content_type=file.content_type,
                request_id=request_id)
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Determine file type from extension
        file_extension = file.filename.lower().split('.')[-1]
        if file_extension not in ['pdf', 'docx', 'txt']:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_extension}. Supported types: pdf, docx, txt"
            )
        
        # Read file content
        file_content = await file.read()
        if not file_content:
            raise HTTPException(status_code=400, detail="Empty file")
        
        logger.info("File validation passed", 
                   file_size=len(file_content), 
                   file_type=file_extension,
                   request_id=request_id)
        
        # Extract text from file
        extracted_text, extraction_metadata = text_extractor.extract(file_content, file_extension)
        
        logger.info("Text extraction completed", 
                   word_count=extraction_metadata['word_count'],
                   request_id=request_id)
        
        # Parse resume text
        parsed_data = resume_parser.parse(extracted_text)
        
        # Merge extraction metadata with parsing metadata
        parsed_data['metadata'].update({
            'extraction_method': extraction_metadata.get('extraction_method'),
            'encoding': extraction_metadata.get('encoding'),
            'word_count': extraction_metadata.get('word_count')
        })
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        logger.info("Resume parsing completed successfully", 
                   processing_time_ms=processing_time_ms,
                   overall_confidence=parsed_data['metadata']['confidence_overall'],
                   request_id=request_id)
        
        return ResumeUploadResponse(
            success=True,
            parsed_data=parsed_data,
            processing_time_ms=processing_time_ms,
            file_metadata=extraction_metadata
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        # Validation errors
        logger.error("Validation error during resume processing", 
                    error=str(e), 
                    request_id=request_id)
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # Processing errors
        logger.error("Processing error during resume parsing", 
                    error=str(e), 
                    request_id=request_id)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        # Unexpected errors
        logger.error("Unexpected error during resume processing", 
                    error=str(e), 
                    request_id=request_id)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint for the resume parser service.
    
    Returns:
        Service health status and metadata
    """
    try:
        # Check if spaCy model is loaded
        if not hasattr(resume_parser, 'nlp') or resume_parser.nlp is None:
            raise RuntimeError("spaCy model not loaded")
        
        # Calculate uptime (simplified - in production, track start time)
        uptime_seconds = 0.0  # TODO: Implement proper uptime tracking
        
        return create_health_response(
            version="0.1.0",
            uptime_seconds=uptime_seconds
        )
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")

@router.get("/supported-types")
async def get_supported_types():
    """
    Get supported file types and their MIME types.
    
    Returns:
        Dictionary of supported file types
    """
    return {
        "supported_types": text_extractor.get_supported_types(),
        "max_file_size_mb": text_extractor.MAX_FILE_SIZE / (1024 * 1024),
        "min_word_count": text_extractor.MIN_WORD_COUNT
    }

async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    error_response = create_error_response(
        error_type="http_error",
        message=exc.detail,
        request_id=getattr(request.state, 'request_id', None)
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )

async def general_exception_handler(request, exc):
    """General exception handler for unexpected errors."""
    logger.error("Unhandled exception", error=str(exc))
    error_response = create_error_response(
        error_type="internal_error",
        message="An unexpected error occurred",
        request_id=getattr(request.state, 'request_id', None)
    )
    return JSONResponse(
        status_code=500,
        content=error_response.dict()
    )
