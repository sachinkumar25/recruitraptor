"""Data integration logic for combining resume and profile discovery data."""

import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date
from collections import defaultdict, Counter

from .models import (
    ExtractedResumeData,
    GitHubProfileMatch,
    LinkedInProfileMatch,
    EnrichedPersonalInfo,
    EnrichedSkillsAnalysis,
    EnrichedExperience,
    EnrichedEducation,
    GitHubRepositoryInsights,
    EnrichedCandidateProfile,
    DataSource,
    ConflictResolution,
    ConflictResolutionResult,
    JobContext
)
from .config import settings
from ..utils.logger import EnrichmentLogger


class DataIntegrator:
    """Main data integration class for combining and normalizing data from multiple sources."""
    
    def __init__(self):
        """Initialize the data integrator."""
        self.logger = EnrichmentLogger("data_integration")
        self.conflicts_resolved: List[ConflictResolutionResult] = []
    
    def integrate_data(
        self,
        resume_data: ExtractedResumeData,
        github_profiles: List[GitHubProfileMatch],
        linkedin_profiles: List[LinkedInProfileMatch],
        job_context: Optional[JobContext] = None
    ) -> EnrichedCandidateProfile:
        """Integrate data from multiple sources into an enriched candidate profile."""
        
        self.logger.log_start(
            resume_data_sources=len([resume_data]),
            github_profiles=len(github_profiles),
            linkedin_profiles=len(linkedin_profiles)
        )
        
        # Extract the best GitHub profile (highest confidence)
        best_github_profile = self._get_best_github_profile(github_profiles)
        
        # Extract the best LinkedIn profile (highest confidence)
        best_linkedin_profile = self._get_best_linkedin_profile(linkedin_profiles)
        
        # Integrate personal information
        enriched_personal_info = self._integrate_personal_info(
            resume_data.personal_info,
            best_github_profile,
            best_linkedin_profile
        )
        
        # Integrate skills
        enriched_skills = self._integrate_skills(
            resume_data.skills,
            best_github_profile
        )
        
        # Integrate experience
        enriched_experience = self._integrate_experience(
            resume_data.experience,
            best_github_profile
        )
        
        # Integrate education
        enriched_education = self._integrate_education(resume_data.education)
        
        # Analyze GitHub repositories
        github_insights = self._analyze_github_repositories(best_github_profile)
        
        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(
            enriched_personal_info,
            enriched_skills,
            enriched_experience,
            enriched_education,
            github_insights
        )
        
        # Create enriched profile
        enriched_profile = EnrichedCandidateProfile(
            personal_info=enriched_personal_info,
            skills=enriched_skills,
            experience=enriched_experience,
            education=enriched_education,
            github_analysis=github_insights,
            overall_confidence=overall_confidence,
            data_sources=self._get_data_sources(resume_data, github_profiles, linkedin_profiles)
        )
        
        # Add job relevance if job context is provided
        if job_context:
            enriched_profile.job_relevance_score = self._calculate_job_relevance(
                enriched_profile, job_context
            )
            enriched_profile.skill_match_percentage = self._calculate_skill_match(
                enriched_skills, job_context
            )
        
        self.logger.log_success(
            processing_time_ms=0,  # Will be set by the service
            overall_confidence=overall_confidence,
            conflicts_resolved=len(self.conflicts_resolved)
        )
        
        return enriched_profile
    
    def _get_best_github_profile(self, github_profiles: List[GitHubProfileMatch]) -> Optional[GitHubProfileMatch]:
        """Get the GitHub profile with the highest confidence score."""
        if not github_profiles:
            return None
        
        return max(github_profiles, key=lambda p: p.confidence)
    
    def _get_best_linkedin_profile(self, linkedin_profiles: List[LinkedInProfileMatch]) -> Optional[LinkedInProfileMatch]:
        """Get the LinkedIn profile with the highest confidence score."""
        if not linkedin_profiles:
            return None
        
        return max(linkedin_profiles, key=lambda p: p.confidence)
    
    def _integrate_personal_info(
        self,
        resume_personal_info: Any,
        github_profile: Optional[GitHubProfileMatch],
        linkedin_profile: Optional[LinkedInProfileMatch]
    ) -> EnrichedPersonalInfo:
        """Integrate personal information from multiple sources."""
        
        # Extract resume data
        resume_name = self._extract_field_value(resume_personal_info, "name")
        resume_email = self._extract_field_value(resume_personal_info, "email")
        resume_phone = self._extract_field_value(resume_personal_info, "phone")
        resume_location = self._extract_field_value(resume_personal_info, "location")
        resume_linkedin = self._extract_field_value(resume_personal_info, "linkedin_url")
        resume_github = self._extract_field_value(resume_personal_info, "github_url")
        
        # Extract GitHub data
        github_name = github_profile.profile.name if github_profile else None
        github_location = github_profile.profile.location if github_profile else None
        github_email = github_profile.profile.email if github_profile else None
        github_bio = github_profile.profile.bio if github_profile else None
        github_username = github_profile.profile.username if github_profile else None
        github_avatar = github_profile.profile.avatar_url if github_profile else None
        github_blog = github_profile.profile.blog if github_profile else None
        
        # Extract LinkedIn data
        linkedin_name = linkedin_profile.profile.name if linkedin_profile else None
        linkedin_location = linkedin_profile.profile.location if linkedin_profile else None
        linkedin_headline = linkedin_profile.profile.headline if linkedin_profile else None
        
        # Resolve conflicts and merge data
        name = self._resolve_name_conflict(resume_name, github_name, linkedin_name)
        email = self._resolve_email_conflict(resume_email, github_email)
        location = self._resolve_location_conflict(resume_location, github_location, linkedin_location)
        phone = resume_phone  # Usually only in resume
        linkedin_url = resume_linkedin or (linkedin_profile.profile.profile_url if linkedin_profile else None)
        github_url = resume_github or (f"https://github.com/{github_username}" if github_username else None)
        
        # Calculate confidence
        confidence = self._calculate_personal_info_confidence(
            resume_personal_info, github_profile, linkedin_profile
        )
        
        # Determine data sources
        data_sources = []
        if resume_personal_info:
            data_sources.append(DataSource.RESUME)
        if github_profile:
            data_sources.append(DataSource.GITHUB)
        if linkedin_profile:
            data_sources.append(DataSource.LINKEDIN)
        
        return EnrichedPersonalInfo(
            name=name or "Unknown",
            email=email,
            phone=phone,
            location=location,
            linkedin_url=linkedin_url,
            github_url=github_url,
            github_username=github_username,
            linkedin_username=self._extract_linkedin_username(linkedin_url) if linkedin_url else None,
            profile_picture=github_avatar,
            bio=github_bio,
            website=github_blog,
            overall_confidence=confidence,
            data_sources=data_sources
        )
    
    def _integrate_skills(
        self,
        resume_skills: Dict[str, Any],
        github_profile: Optional[GitHubProfileMatch]
    ) -> EnrichedSkillsAnalysis:
        """Integrate skills from resume and GitHub repositories."""
        
        # Extract resume skills
        resume_technical_skills = self._extract_resume_skills(resume_skills)
        
        # Extract GitHub skills
        github_skills = self._extract_github_skills(github_profile) if github_profile else {}
        
        # Merge and analyze skills
        merged_skills = self._merge_skills(resume_technical_skills, github_skills)
        
        # Calculate proficiency levels
        skill_proficiencies = self._calculate_skill_proficiencies(merged_skills, github_profile)
        
        # Categorize skills
        categorized_skills = self._categorize_skills(merged_skills)
        
        # Calculate overall confidence
        confidence = self._calculate_skills_confidence(resume_skills, github_profile)
        
        return EnrichedSkillsAnalysis(
            technical_skills=skill_proficiencies,
            soft_skills=self._extract_soft_skills(resume_skills),
            programming_languages=categorized_skills.get("programming_languages", {}),
            frameworks=categorized_skills.get("frameworks", {}),
            databases=categorized_skills.get("databases", {}),
            cloud_platforms=categorized_skills.get("cloud_platforms", {}),
            tools=categorized_skills.get("tools", {}),
            overall_confidence=confidence,
            skill_gaps=self._identify_skill_gaps(merged_skills),
            skill_strengths=self._identify_skill_strengths(merged_skills)
        )
    
    def _integrate_experience(
        self,
        resume_experience: Dict[str, Any],
        github_profile: Optional[GitHubProfileMatch]
    ) -> EnrichedExperience:
        """Integrate work experience from resume and GitHub."""
        
        # Extract resume experience
        companies = resume_experience.get("companies", [])
        positions = resume_experience.get("positions", [])
        dates = resume_experience.get("dates", [])
        descriptions = resume_experience.get("descriptions", [])
        
        # Analyze GitHub repositories for additional context
        github_insights = self._analyze_github_for_experience(github_profile) if github_profile else {}
        
        # Enhance experience with GitHub data
        technologies_used = self._extract_technologies_from_experience(descriptions, github_insights)
        project_complexity = self._assess_project_complexity(descriptions, github_insights)
        team_size = self._estimate_team_size(descriptions, github_insights)
        
        # Calculate career progression score
        career_progression = self._calculate_career_progression(positions, dates)
        
        # Calculate confidence
        confidence = self._calculate_experience_confidence(resume_experience, github_profile)
        
        return EnrichedExperience(
            companies=companies,
            positions=positions,
            dates=dates,
            descriptions=descriptions,
            technologies_used=technologies_used,
            project_complexity=project_complexity,
            team_size=team_size,
            impact_metrics={},  # Would need more sophisticated analysis
            overall_confidence=confidence,
            career_progression_score=career_progression
        )
    
    def _integrate_education(self, resume_education: Dict[str, Any]) -> EnrichedEducation:
        """Integrate education information from resume."""
        
        institutions = resume_education.get("institutions", [])
        degrees = resume_education.get("degrees", [])
        fields_of_study = resume_education.get("fields_of_study", [])
        dates = resume_education.get("dates", [])
        gpa = self._extract_gpa(resume_education)
        
        # Calculate confidence
        confidence = self._calculate_education_confidence(resume_education)
        
        return EnrichedEducation(
            institutions=institutions,
            degrees=degrees,
            fields_of_study=fields_of_study,
            dates=dates,
            gpa=gpa,
            relevant_courses=[],  # Would need more sophisticated extraction
            certifications=[],  # Would need more sophisticated extraction
            overall_confidence=confidence
        )
    
    def _analyze_github_repositories(self, github_profile: Optional[GitHubProfileMatch]) -> GitHubRepositoryInsights:
        """Analyze GitHub repositories for insights."""
        
        if not github_profile or not github_profile.repositories:
            return GitHubRepositoryInsights()
        
        repos = github_profile.repositories
        
        # Basic metrics
        total_repos = len(repos)
        total_stars = sum(repo.stars for repo in repos)
        total_forks = sum(repo.forks for repo in repos)
        
        # Language distribution
        languages = Counter(repo.language for repo in repos if repo.language)
        languages_distribution = dict(languages)
        
        # Framework detection
        frameworks = self._detect_frameworks_from_repos(repos)
        
        # Most active repositories
        most_active = sorted(repos, key=lambda r: (r.stars, r.forks), reverse=True)[:5]
        most_active_names = [repo.name for repo in most_active]
        
        # Recent activity score
        recent_activity = self._calculate_recent_activity_score(repos)
        
        # Code quality indicators
        code_quality = self._assess_code_quality(repos)
        
        # Collaboration patterns
        collaboration = self._analyze_collaboration_patterns(repos)
        
        # Open source contribution score
        open_source_score = self._calculate_open_source_score(repos)
        
        return GitHubRepositoryInsights(
            total_repositories=total_repos,
            total_stars=total_stars,
            total_forks=total_forks,
            languages_distribution=languages_distribution,
            frameworks_detected=frameworks,
            most_active_repos=most_active_names,
            recent_activity_score=recent_activity,
            code_quality_indicators=code_quality,
            collaboration_patterns=collaboration,
            open_source_contribution_score=open_source_score
        )
    
    # Helper methods for data extraction and conflict resolution
    def _extract_field_value(self, obj: Any, field_name: str) -> Optional[str]:
        """Extract field value from confidence field or direct field."""
        if hasattr(obj, field_name):
            field = getattr(obj, field_name)
            if hasattr(field, 'value'):
                return field.value
            return field
        return None
    
    def _resolve_name_conflict(self, resume_name: Optional[str], github_name: Optional[str], linkedin_name: Optional[str]) -> Optional[str]:
        """Resolve name conflicts between sources."""
        names = [n for n in [resume_name, github_name, linkedin_name] if n]
        if not names:
            return None
        
        # Use resume name as priority, then GitHub, then LinkedIn
        if resume_name:
            return resume_name
        elif github_name:
            return github_name
        else:
            return linkedin_name
    
    def _resolve_email_conflict(self, resume_email: Optional[str], github_email: Optional[str]) -> Optional[str]:
        """Resolve email conflicts between sources."""
        if resume_email:
            return resume_email
        return github_email
    
    def _resolve_location_conflict(self, resume_location: Optional[str], github_location: Optional[str], linkedin_location: Optional[str]) -> Optional[str]:
        """Resolve location conflicts between sources."""
        locations = [l for l in [resume_location, github_location, linkedin_location] if l]
        if not locations:
            return None
        
        # Use resume location as priority
        if resume_location:
            return resume_location
        elif github_location:
            return github_location
        else:
            return linkedin_location
    
    def _extract_linkedin_username(self, linkedin_url: str) -> Optional[str]:
        """Extract LinkedIn username from URL."""
        if not linkedin_url:
            return None
        
        # Simple regex to extract username from LinkedIn URL
        match = re.search(r'linkedin\.com/in/([^/]+)', linkedin_url)
        return match.group(1) if match else None
    
    def _extract_resume_skills(self, resume_skills: Dict[str, Any]) -> List[str]:
        """Extract technical skills from resume data."""
        skills = []
        
        # Extract from technical_skills field
        if "technical_skills" in resume_skills:
            skills.extend(resume_skills["technical_skills"])
        
        # Extract from categories
        if "categories" in resume_skills:
            categories = resume_skills["categories"]
            for category_name in ["programming_languages", "frameworks", "databases", "cloud_platforms", "tools"]:
                if category_name in categories:
                    skills.extend(categories[category_name])
        
        return list(set(skills))  # Remove duplicates
    
    def _extract_github_skills(self, github_profile: GitHubProfileMatch) -> Dict[str, int]:
        """Extract skills from GitHub repositories."""
        skills = {}
        
        # From languages used
        for language, count in github_profile.languages_used.items():
            skills[language.lower()] = count
        
        # From frameworks detected
        for framework in github_profile.frameworks_detected:
            skills[framework.lower()] = skills.get(framework.lower(), 0) + 1
        
        # From repository topics
        for repo in github_profile.repositories:
            for topic in repo.topics:
                skills[topic.lower()] = skills.get(topic.lower(), 0) + 1
        
        return skills
    
    def _merge_skills(self, resume_skills: List[str], github_skills: Dict[str, int]) -> Dict[str, int]:
        """Merge skills from resume and GitHub with weighting."""
        merged = {}
        
        # Add resume skills with base weight
        for skill in resume_skills:
            skill_lower = skill.lower()
            merged[skill_lower] = merged.get(skill_lower, 0) + settings.resume_priority_weight * 10
        
        # Add GitHub skills with their counts
        for skill, count in github_skills.items():
            skill_lower = skill.lower()
            merged[skill_lower] = merged.get(skill_lower, 0) + settings.github_priority_weight * count
        
        return merged
    
    def _calculate_skill_proficiencies(self, merged_skills: Dict[str, int], github_profile: Optional[GitHubProfileMatch]) -> List[Any]:
        """Calculate skill proficiency levels."""
        # This would be implemented with more sophisticated logic
        # For now, return a simple implementation
        proficiencies = []
        
        for skill, score in merged_skills.items():
            if score >= 8:
                level = "expert"
            elif score >= 6:
                level = "advanced"
            elif score >= 4:
                level = "intermediate"
            else:
                level = "beginner"
            
            # This would need to be converted to proper SkillProficiency objects
            proficiencies.append({
                "skill_name": skill,
                "proficiency_level": level,
                "confidence_score": min(score / 10, 1.0)
            })
        
        return proficiencies
    
    def _categorize_skills(self, skills: Dict[str, int]) -> Dict[str, Dict[str, int]]:
        """Categorize skills into different types."""
        # This would be implemented with skill categorization logic
        # For now, return all skills as programming languages with integer values
        categorized = {
            "programming_languages": {skill: int(count) for skill, count in skills.items()},
            "frameworks": {},
            "databases": {},
            "cloud_platforms": {},
            "tools": {}
        }
        return categorized
    
    def _extract_soft_skills(self, resume_skills: Dict[str, Any]) -> List[str]:
        """Extract soft skills from resume."""
        return resume_skills.get("soft_skills", [])
    
    def _identify_skill_gaps(self, skills: Dict[str, int]) -> List[str]:
        """Identify potential skill gaps."""
        # This would be implemented with gap analysis logic
        return []
    
    def _identify_skill_strengths(self, skills: Dict[str, int]) -> List[str]:
        """Identify skill strengths."""
        # Return top skills by score
        sorted_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)
        return [skill for skill, _ in sorted_skills[:5]]
    
    def _analyze_github_for_experience(self, github_profile: GitHubProfileMatch) -> Dict[str, Any]:
        """Analyze GitHub repositories for experience insights."""
        if not github_profile:
            return {}
        
        return {
            "languages": github_profile.languages_used,
            "frameworks": github_profile.frameworks_detected,
            "repo_count": len(github_profile.repositories)
        }
    
    def _extract_technologies_from_experience(self, descriptions: List[str], github_insights: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract technologies used from experience descriptions."""
        # This would be implemented with NLP/text analysis
        return {}
    
    def _assess_project_complexity(self, descriptions: List[str], github_insights: Dict[str, Any]) -> Dict[str, str]:
        """Assess project complexity from descriptions and GitHub data."""
        # This would be implemented with complexity analysis logic
        return {}
    
    def _estimate_team_size(self, descriptions: List[str], github_insights: Dict[str, Any]) -> Dict[str, str]:
        """Estimate team size from descriptions and GitHub data."""
        # This would be implemented with team size estimation logic
        return {}
    
    def _calculate_career_progression(self, positions: List[str], dates: List[str]) -> Optional[float]:
        """Calculate career progression score."""
        # This would be implemented with career progression analysis
        return 0.7  # Placeholder
    
    def _extract_gpa(self, education: Dict[str, Any]) -> Optional[float]:
        """Extract GPA from education data."""
        gpa_field = education.get("gpa")
        if gpa_field and hasattr(gpa_field, 'value'):
            return gpa_field.value
        return None
    
    def _detect_frameworks_from_repos(self, repos: List[Any]) -> List[str]:
        """Detect frameworks from repository data."""
        # This would be implemented with framework detection logic
        return []
    
    def _calculate_recent_activity_score(self, repos: List[Any]) -> float:
        """Calculate recent activity score from repositories."""
        # This would be implemented with activity analysis
        return 0.8  # Placeholder
    
    def _assess_code_quality(self, repos: List[Any]) -> Dict[str, Any]:
        """Assess code quality from repositories."""
        # This would be implemented with code quality analysis
        return {}
    
    def _analyze_collaboration_patterns(self, repos: List[Any]) -> Dict[str, Any]:
        """Analyze collaboration patterns from repositories."""
        # This would be implemented with collaboration analysis
        return {}
    
    def _calculate_open_source_score(self, repos: List[Any]) -> float:
        """Calculate open source contribution score."""
        # This would be implemented with open source analysis
        return 0.6  # Placeholder
    
    def _calculate_personal_info_confidence(self, resume_info: Any, github_profile: Optional[GitHubProfileMatch], linkedin_profile: Optional[LinkedInProfileMatch]) -> float:
        """Calculate confidence for personal information."""
        # This would be implemented with confidence calculation logic
        return 0.8  # Placeholder
    
    def _calculate_skills_confidence(self, resume_skills: Dict[str, Any], github_profile: Optional[GitHubProfileMatch]) -> float:
        """Calculate confidence for skills analysis."""
        # This would be implemented with confidence calculation logic
        return 0.7  # Placeholder
    
    def _calculate_experience_confidence(self, resume_experience: Dict[str, Any], github_profile: Optional[GitHubProfileMatch]) -> float:
        """Calculate confidence for experience analysis."""
        # This would be implemented with confidence calculation logic
        return 0.8  # Placeholder
    
    def _calculate_education_confidence(self, resume_education: Dict[str, Any]) -> float:
        """Calculate confidence for education analysis."""
        # This would be implemented with confidence calculation logic
        return 0.9  # Placeholder
    
    def _calculate_overall_confidence(self, personal_info: EnrichedPersonalInfo, skills: EnrichedSkillsAnalysis, 
                                   experience: EnrichedExperience, education: EnrichedEducation, 
                                   github_insights: GitHubRepositoryInsights) -> float:
        """Calculate overall confidence score."""
        confidences = [
            personal_info.overall_confidence,
            skills.overall_confidence,
            experience.overall_confidence,
            education.overall_confidence
        ]
        return sum(confidences) / len(confidences)
    
    def _get_data_sources(self, resume_data: ExtractedResumeData, github_profiles: List[GitHubProfileMatch], 
                         linkedin_profiles: List[LinkedInProfileMatch]) -> List[DataSource]:
        """Get list of data sources used."""
        sources = [DataSource.RESUME]
        if github_profiles:
            sources.append(DataSource.GITHUB)
        if linkedin_profiles:
            sources.append(DataSource.LINKEDIN)
        return sources
    
    def _calculate_job_relevance(self, profile: EnrichedCandidateProfile, job_context: JobContext) -> float:
        """Calculate job relevance score."""
        # This would be implemented with job matching logic
        return 0.75  # Placeholder
    
    def _calculate_skill_match(self, skills: EnrichedSkillsAnalysis, job_context: JobContext) -> float:
        """Calculate skill match percentage."""
        # This would be implemented with skill matching logic
        return 0.8  # Placeholder 