"""Main enrichment service for Data Enrichment Service."""

import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..core.models import (
    EnrichmentRequest,
    EnrichmentResponse,
    EnrichmentMetadata,
    EnrichedCandidateProfile,
    ExtractedResumeData,
    GitHubProfileMatch,
    LinkedInProfileMatch,
    JobContext,
    DataSource,
    ConflictResolutionResult
)
from ..core.data_integrator import DataIntegrator
from ..core.skill_analyzer import SkillAnalyzer
from ..core.conflict_resolver import ConflictResolver
from ..core.config import settings
from ..utils.logger import EnrichmentLogger, logger


class EnrichmentService:
    """Main service for enriching candidate data."""
    
    def __init__(self):
        """Initialize the enrichment service."""
        self.logger = EnrichmentLogger("enrichment_service")
        self.data_integrator = DataIntegrator()
        self.skill_analyzer = SkillAnalyzer()
        self.conflict_resolver = ConflictResolver()
    
    async def enrich_candidate_data(
        self,
        request: EnrichmentRequest
    ) -> EnrichmentResponse:
        """Enrich candidate data by combining and analyzing multiple sources."""
        
        start_time = time.time()
        enrichment_logger = EnrichmentLogger("enrich_candidate", request.resume_data.personal_info.name.value if request.resume_data.personal_info.name.value else "unknown")
        
        try:
            enrichment_logger.log_start(
                resume_data_present=bool(request.resume_data),
                github_profiles_count=len(request.github_profiles),
                linkedin_profiles_count=len(request.linkedin_profiles),
                job_context_present=bool(request.job_context)
            )
            
            # Step 1: Resolve conflicts between data sources
            conflicts_resolved = await self._resolve_data_conflicts(request)
            
            # Step 2: Integrate data from multiple sources
            enriched_profile = await self._integrate_candidate_data(request)
            
            # Step 3: Perform advanced skill analysis
            enriched_profile = await self._analyze_skills(enriched_profile, request)
            
            # Step 4: Calculate job relevance if job context is provided
            if request.job_context:
                enriched_profile = await self._calculate_job_relevance(enriched_profile, request.job_context)
            
            # Step 5: Calculate processing time
            processing_time_ms = (time.time() - start_time) * 1000
            
            # Step 6: Create enrichment metadata
            enrichment_metadata = self._create_enrichment_metadata(
                processing_time_ms, conflicts_resolved, request
            )
            
            enrichment_logger.log_success(
                processing_time_ms=processing_time_ms,
                overall_confidence=enriched_profile.overall_confidence,
                data_sources_count=len(enriched_profile.data_sources)
            )
            
            return EnrichmentResponse(
                success=True,
                enriched_profile=enriched_profile,
                enrichment_metadata=enrichment_metadata,
                processing_time_ms=processing_time_ms
            )
            
        except Exception as e:
            processing_time_ms = (time.time() - start_time) * 1000
            enrichment_logger.log_error(e, processing_time_ms=processing_time_ms)
            
            logger.error(
                "Enrichment failed",
                error_type=type(e).__name__,
                error_message=str(e),
                processing_time_ms=processing_time_ms
            )
            
            return EnrichmentResponse(
                success=False,
                enriched_profile=None,
                enrichment_metadata=self._create_error_metadata(processing_time_ms),
                processing_time_ms=processing_time_ms,
                error_message=str(e)
            )
    
    async def _resolve_data_conflicts(self, request: EnrichmentRequest) -> List[ConflictResolutionResult]:
        """Resolve conflicts between data from different sources."""
        
        # Prepare data by source
        data_by_source = {}
        
        # Add resume data
        if request.resume_data:
            data_by_source[DataSource.RESUME] = {
                "personal_info": request.resume_data.personal_info,
                "education": request.resume_data.education,
                "experience": request.resume_data.experience,
                "skills": request.resume_data.skills
            }
        
        # Add GitHub data
        if request.github_profiles:
            best_github = max(request.github_profiles, key=lambda p: p.confidence)
            data_by_source[DataSource.GITHUB] = {
                "personal_info": {
                    "name": best_github.profile.name,
                    "email": best_github.profile.email,
                    "location": best_github.profile.location,
                    "bio": best_github.profile.bio
                },
                "skills": {
                    "technical_skills": list(best_github.languages_used.keys()) + best_github.frameworks_detected,
                    "categories": {
                        "programming_languages": list(best_github.languages_used.keys()),
                        "frameworks": best_github.frameworks_detected
                    }
                }
            }
        
        # Add LinkedIn data
        if request.linkedin_profiles:
            best_linkedin = max(request.linkedin_profiles, key=lambda p: p.confidence)
            data_by_source[DataSource.LINKEDIN] = {
                "personal_info": {
                    "name": best_linkedin.profile.name,
                    "location": best_linkedin.profile.location,
                    "headline": best_linkedin.profile.headline
                }
            }
        
        # Resolve conflicts
        resolved_data, conflicts_resolved = self.conflict_resolver.resolve_conflicts(data_by_source)
        
        return conflicts_resolved
    
    async def _integrate_candidate_data(self, request: EnrichmentRequest) -> EnrichedCandidateProfile:
        """Integrate candidate data from multiple sources."""
        
        return self.data_integrator.integrate_data(
            resume_data=request.resume_data,
            github_profiles=request.github_profiles,
            linkedin_profiles=request.linkedin_profiles,
            job_context=request.job_context
        )
    
    async def _analyze_skills(
        self,
        enriched_profile: EnrichedCandidateProfile,
        request: EnrichmentRequest
    ) -> EnrichedCandidateProfile:
        """Perform advanced skill analysis."""
        
        # Get the best GitHub profile for skill analysis
        best_github_profile = None
        if request.github_profiles:
            best_github_profile = max(request.github_profiles, key=lambda p: p.confidence)
        
        # Analyze skills
        skill_proficiencies = self.skill_analyzer.analyze_skills(
            resume_skills=request.resume_data.skills,
            github_profile=best_github_profile
        )
        
        # Update the enriched profile with skill analysis
        enriched_profile.skills.technical_skills = skill_proficiencies
        
        # Categorize skills
        all_skills = [skill.skill_name for skill in skill_proficiencies]
        categorized_skills = self.skill_analyzer.categorize_skills(all_skills)
        
        # Update skill categories with integer values
        enriched_profile.skills.programming_languages = {
            skill: int(1) for skill in categorized_skills.get("programming_languages", [])
        }
        enriched_profile.skills.frameworks = {
            skill: int(1) for skill in categorized_skills.get("frameworks", [])
        }
        enriched_profile.skills.databases = {
            skill: int(1) for skill in categorized_skills.get("databases", [])
        }
        enriched_profile.skills.cloud_platforms = {
            skill: int(1) for skill in categorized_skills.get("cloud_platforms", [])
        }
        enriched_profile.skills.tools = {
            skill: int(1) for skill in categorized_skills.get("tools", [])
        }
        
        return enriched_profile
    
    async def _calculate_job_relevance(
        self,
        enriched_profile: EnrichedCandidateProfile,
        job_context: JobContext
    ) -> EnrichedCandidateProfile:
        """Calculate job relevance score and skill match percentage."""
        
        # Calculate skill match
        skill_match_result = self.skill_analyzer.calculate_skill_match(
            candidate_skills=enriched_profile.skills.technical_skills,
            required_skills=job_context.required_skills,
            preferred_skills=job_context.preferred_skills
        )
        
        # Update profile with job relevance metrics
        enriched_profile.job_relevance_score = skill_match_result["match_percentage"]
        enriched_profile.skill_match_percentage = skill_match_result["match_percentage"]
        
        # Update skill gaps and strengths
        enriched_profile.skills.skill_gaps = skill_match_result["missing_skills"]
        enriched_profile.skills.skill_strengths = skill_match_result["strength_skills"]
        
        return enriched_profile
    
    def _create_enrichment_metadata(
        self,
        processing_time_ms: float,
        conflicts_resolved: List[ConflictResolutionResult],
        request: EnrichmentRequest
    ) -> EnrichmentMetadata:
        """Create enrichment metadata."""
        
        # Determine data sources used
        data_sources = [DataSource.RESUME]
        if request.github_profiles:
            data_sources.append(DataSource.GITHUB)
        if request.linkedin_profiles:
            data_sources.append(DataSource.LINKEDIN)
        
        # Determine algorithms used
        algorithms_used = [
            "data_integration",
            "skill_analysis",
            "conflict_resolution"
        ]
        
        if request.job_context:
            algorithms_used.append("job_matching")
        
        return EnrichmentMetadata(
            processing_time_ms=processing_time_ms,
            data_sources_used=data_sources,
            conflicts_resolved=conflicts_resolved,
            confidence_threshold=settings.min_confidence_threshold,
            skill_weighting_factor=settings.skill_weighting_factor,
            enrichment_version=settings.version,
            algorithms_used=algorithms_used
        )
    
    def _create_error_metadata(self, processing_time_ms: float) -> EnrichmentMetadata:
        """Create error metadata."""
        
        return EnrichmentMetadata(
            processing_time_ms=processing_time_ms,
            data_sources_used=[],
            conflicts_resolved=[],
            confidence_threshold=settings.min_confidence_threshold,
            skill_weighting_factor=settings.skill_weighting_factor,
            enrichment_version=settings.version,
            algorithms_used=[]
        )
    
    async def get_enrichment_statistics(self) -> Dict[str, Any]:
        """Get enrichment service statistics."""
        
        return {
            "service_name": settings.service_name,
            "version": settings.version,
            "uptime_seconds": 0,  # Would be calculated from service start time
            "total_enrichments": 0,  # Would be tracked in a real implementation
            "average_processing_time_ms": 0,  # Would be calculated from historical data
            "success_rate": 1.0,  # Would be calculated from historical data
            "active_data_sources": [
                DataSource.RESUME.value,
                DataSource.GITHUB.value,
                DataSource.LINKEDIN.value
            ],
            "supported_algorithms": [
                "data_integration",
                "skill_analysis",
                "conflict_resolution",
                "job_matching"
            ]
        }
    
    async def validate_enrichment_request(self, request: EnrichmentRequest) -> List[str]:
        """Validate enrichment request and return any validation errors."""
        
        errors = []
        
        # Check if resume data is provided
        if not request.resume_data:
            errors.append("Resume data is required")
        
        # Check if at least one profile source is provided
        if not request.github_profiles and not request.linkedin_profiles:
            errors.append("At least one profile source (GitHub or LinkedIn) is required")
        
        # Validate resume data structure
        if request.resume_data:
            if not request.resume_data.personal_info:
                errors.append("Personal information is required in resume data")
            
            if not request.resume_data.skills:
                errors.append("Skills information is required in resume data")
        
        # Validate GitHub profiles
        for i, profile in enumerate(request.github_profiles):
            if not profile.profile.username:
                errors.append(f"GitHub profile {i+1} must have a username")
            
            if profile.confidence < 0 or profile.confidence > 1:
                errors.append(f"GitHub profile {i+1} confidence must be between 0 and 1")
        
        # Validate LinkedIn profiles
        for i, profile in enumerate(request.linkedin_profiles):
            if not profile.profile.profile_url:
                errors.append(f"LinkedIn profile {i+1} must have a profile URL")
            
            if profile.confidence < 0 or profile.confidence > 1:
                errors.append(f"LinkedIn profile {i+1} confidence must be between 0 and 1")
        
        # Validate job context if provided
        if request.job_context:
            if not request.job_context.required_skills:
                errors.append("Job context must specify required skills")
        
        return errors 