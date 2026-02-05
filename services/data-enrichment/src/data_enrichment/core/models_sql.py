from sqlalchemy import Column, String, DateTime, Float, JSON
from sqlalchemy.sql import func
from .database import Base
import uuid

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    candidate_id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True)
    email = Column(String, index=True, nullable=True)
    
    # Store complete enriched profile as JSONB for flexibility
    # This allows us to evolve the Pydantic models without heavy SQL migrations
    profile_data = Column(JSON)
    
    # Metadata for queries
    overall_confidence = Column(Float, default=0.0)
    job_relevance_score = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
