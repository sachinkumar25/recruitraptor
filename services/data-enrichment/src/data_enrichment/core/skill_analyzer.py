"""Skill analysis and proficiency calculation for Data Enrichment Service."""

import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date, timedelta
from collections import Counter, defaultdict
from dataclasses import dataclass

from .models import (
    SkillProficiencyLevel,
    SkillProficiency,
    GitHubRepository,
    GitHubProfileMatch,
    DataSource
)
from .config import settings
from ..utils.logger import EnrichmentLogger


@dataclass
class SkillEvidence:
    """Evidence for a skill with metadata."""
    skill_name: str
    source: DataSource
    confidence: float
    usage_count: int = 1
    last_used: Optional[date] = None
    years_experience: Optional[float] = None
    context: Optional[str] = None


class SkillAnalyzer:
    """Analyzes skills and calculates proficiency levels."""
    
    def __init__(self):
        """Initialize the skill analyzer."""
        self.logger = EnrichmentLogger("skill_analysis")
        
        # Skill categorization mappings
        self.programming_languages = {
            "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", "php", "ruby",
            "swift", "kotlin", "scala", "r", "matlab", "perl", "bash", "shell", "powershell",
            "html", "css", "sql", "dart", "elixir", "clojure", "haskell", "erlang"
        }
        
        self.frameworks = {
            "react", "angular", "vue", "django", "flask", "spring", "express", "fastapi",
            "laravel", "rails", "asp.net", "node.js", "next.js", "nuxt.js", "svelte",
            "bootstrap", "tailwind", "material-ui", "antd", "jquery", "lodash"
        }
        
        self.databases = {
            "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra",
            "dynamodb", "sqlite", "oracle", "sql server", "mariadb", "neo4j",
            "influxdb", "couchdb", "firebase", "supabase"
        }
        
        self.cloud_platforms = {
            "aws", "azure", "gcp", "heroku", "digitalocean", "linode", "vultr",
            "kubernetes", "docker", "terraform", "ansible", "jenkins", "gitlab",
            "github actions", "circleci", "travis ci", "netlify", "vercel"
        }
        
        self.tools = {
            "git", "github", "gitlab", "bitbucket", "jira", "confluence", "slack",
            "discord", "teams", "zoom", "figma", "sketch", "adobe", "postman",
            "insomnia", "swagger", "openapi", "graphql", "rest", "soap"
        }
    
    def analyze_skills(
        self,
        resume_skills: Dict[str, Any],
        github_profile: Optional[GitHubProfileMatch]
    ) -> List[SkillProficiency]:
        """Analyze skills from multiple sources and calculate proficiency levels."""
        
        self.logger.log_start(
            resume_skills_count=len(self._extract_resume_skills(resume_skills)),
            github_repos_count=len(github_profile.repositories) if github_profile else 0
        )
        
        # Collect skill evidence from all sources
        skill_evidence = self._collect_skill_evidence(resume_skills, github_profile)
        
        # Calculate proficiency levels
        proficiencies = []
        for skill_name, evidence_list in skill_evidence.items():
            proficiency = self._calculate_skill_proficiency(skill_name, evidence_list)
            if proficiency:
                proficiencies.append(proficiency)
                self.logger.log_skill_analysis(
                    skill=skill_name,
                    proficiency=proficiency.proficiency_level.value,
                    confidence=proficiency.confidence_score
                )
        
        # Sort by confidence and proficiency level
        proficiencies.sort(key=lambda x: (x.confidence_score, x.proficiency_level.value), reverse=True)
        
        self.logger.log_success(
            processing_time_ms=0,
            skills_analyzed=len(proficiencies),
            average_confidence=sum(p.confidence_score for p in proficiencies) / len(proficiencies) if proficiencies else 0
        )
        
        return proficiencies
    
    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills into different types."""
        categories = {
            "programming_languages": [],
            "frameworks": [],
            "databases": [],
            "cloud_platforms": [],
            "tools": []
        }
        
        for skill in skills:
            skill_lower = skill.lower()
            
            if skill_lower in self.programming_languages:
                categories["programming_languages"].append(skill)
            elif skill_lower in self.frameworks:
                categories["frameworks"].append(skill)
            elif skill_lower in self.databases:
                categories["databases"].append(skill)
            elif skill_lower in self.cloud_platforms:
                categories["cloud_platforms"].append(skill)
            elif skill_lower in self.tools:
                categories["tools"].append(skill)
            else:
                # Default to tools for unknown skills
                categories["tools"].append(skill)
        
        return categories
    
    def calculate_skill_match(
        self,
        candidate_skills: List[SkillProficiency],
        required_skills: List[str],
        preferred_skills: List[str] = None
    ) -> Dict[str, float]:
        """Calculate skill match percentage for job requirements."""
        
        if not required_skills:
            return {"match_percentage": 0.0, "missing_skills": [], "strength_skills": []}
        
        candidate_skill_names = {skill.skill_name.lower() for skill in candidate_skills}
        required_skill_names = {skill.lower() for skill in required_skills}
        preferred_skill_names = {skill.lower() for skill in (preferred_skills or [])}
        
        # Calculate required skills match
        matched_required = candidate_skill_names.intersection(required_skill_names)
        required_match_percentage = len(matched_required) / len(required_skill_names)
        
        # Calculate preferred skills match
        preferred_match_percentage = 0.0
        if preferred_skill_names:
            matched_preferred = candidate_skill_names.intersection(preferred_skill_names)
            preferred_match_percentage = len(matched_preferred) / len(preferred_skill_names)
        
        # Overall match percentage (weighted)
        overall_match = (required_match_percentage * 0.7) + (preferred_match_percentage * 0.3)
        
        # Identify missing and strength skills
        missing_skills = list(required_skill_names - candidate_skill_names)
        strength_skills = [
            skill.skill_name for skill in candidate_skills 
            if skill.proficiency_level in [SkillProficiencyLevel.ADVANCED, SkillProficiencyLevel.EXPERT]
        ]
        
        return {
            "match_percentage": overall_match,
            "required_match_percentage": required_match_percentage,
            "preferred_match_percentage": preferred_match_percentage,
            "missing_skills": missing_skills,
            "strength_skills": strength_skills,
            "matched_required_skills": list(matched_required),
            "matched_preferred_skills": list(candidate_skill_names.intersection(preferred_skill_names))
        }
    
    def identify_skill_gaps(
        self,
        candidate_skills: List[SkillProficiency],
        job_requirements: List[str],
        industry_trends: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Identify skill gaps for career development."""
        
        candidate_skill_names = {skill.skill_name.lower() for skill in candidate_skills}
        required_skill_names = {skill.lower() for skill in job_requirements}
        trend_skill_names = {skill.lower() for skill in (industry_trends or [])}
        
        gaps = []
        
        # Missing required skills
        missing_required = required_skill_names - candidate_skill_names
        for skill in missing_required:
            gaps.append({
                "skill": skill,
                "type": "required",
                "priority": "high",
                "recommendation": f"Learn {skill} to meet job requirements"
            })
        
        # Missing trending skills
        missing_trends = trend_skill_names - candidate_skill_names
        for skill in missing_trends:
            gaps.append({
                "skill": skill,
                "type": "trending",
                "priority": "medium",
                "recommendation": f"Consider learning {skill} for career growth"
            })
        
        # Skills that need improvement
        for skill in candidate_skills:
            if skill.proficiency_level in [SkillProficiencyLevel.BEGINNER, SkillProficiencyLevel.INTERMEDIATE]:
                if skill.skill_name.lower() in required_skill_names:
                    gaps.append({
                        "skill": skill.skill_name,
                        "type": "improvement",
                        "priority": "high",
                        "current_level": skill.proficiency_level.value,
                        "recommendation": f"Improve {skill.skill_name} proficiency from {skill.proficiency_level.value} to advanced"
                    })
        
        return gaps
    
    def _collect_skill_evidence(
        self,
        resume_skills: Dict[str, Any],
        github_profile: Optional[GitHubProfileMatch]
    ) -> Dict[str, List[SkillEvidence]]:
        """Collect skill evidence from all sources."""
        evidence = defaultdict(list)
        
        # Collect from resume
        resume_evidence = self._extract_resume_skill_evidence(resume_skills)
        for skill_evidence in resume_evidence:
            evidence[skill_evidence.skill_name.lower()].append(skill_evidence)
        
        # Collect from GitHub
        if github_profile:
            github_evidence = self._extract_github_skill_evidence(github_profile)
            for skill_evidence in github_evidence:
                evidence[skill_evidence.skill_name.lower()].append(skill_evidence)
        
        return dict(evidence)
    
    def _extract_resume_skill_evidence(self, resume_skills: Dict[str, Any]) -> List[SkillEvidence]:
        """Extract skill evidence from resume data."""
        evidence = []
        
        # Extract from technical skills
        technical_skills = resume_skills.get("technical_skills", [])
        for skill in technical_skills:
            evidence.append(SkillEvidence(
                skill_name=skill,
                source=DataSource.RESUME,
                confidence=0.8,  # Resume skills are generally reliable
                context="resume_technical_skills"
            ))
        
        # Extract from categorized skills
        categories = resume_skills.get("categories", {})
        for category_name, skills in categories.items():
            for skill in skills:
                evidence.append(SkillEvidence(
                    skill_name=skill,
                    source=DataSource.RESUME,
                    confidence=0.7,  # Slightly lower confidence for categorized skills
                    context=f"resume_{category_name}"
                ))
        
        return evidence
    
    def _extract_github_skill_evidence(self, github_profile: GitHubProfileMatch) -> List[SkillEvidence]:
        """Extract skill evidence from GitHub profile."""
        evidence = []
        
        # From languages used
        for language, count in github_profile.languages_used.items():
            evidence.append(SkillEvidence(
                skill_name=language,
                source=DataSource.GITHUB,
                confidence=0.9,  # High confidence for actual code
                usage_count=count,
                context="github_language"
            ))
        
        # From frameworks detected
        for framework in github_profile.frameworks_detected:
            evidence.append(SkillEvidence(
                skill_name=framework,
                source=DataSource.GITHUB,
                confidence=0.8,
                context="github_framework"
            ))
        
        # From repository topics
        for repo in github_profile.repositories:
            for topic in repo.topics:
                evidence.append(SkillEvidence(
                    skill_name=topic,
                    source=DataSource.GITHUB,
                    confidence=0.6,  # Lower confidence for topics
                    context="github_topic"
                ))
        
        # From repository descriptions and names
        for repo in github_profile.repositories:
            repo_skills = self._extract_skills_from_text(
                f"{repo.name} {repo.description or ''}"
            )
            for skill in repo_skills:
                evidence.append(SkillEvidence(
                    skill_name=skill,
                    source=DataSource.GITHUB,
                    confidence=0.5,  # Lower confidence for text extraction
                    context="github_repo_text"
                ))
        
        return evidence
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from text using pattern matching."""
        if not text:
            return []
        
        text_lower = text.lower()
        found_skills = set()
        
        # Check for programming languages
        for lang in self.programming_languages:
            if lang in text_lower:
                found_skills.add(lang)
        
        # Check for frameworks
        for framework in self.frameworks:
            if framework in text_lower:
                found_skills.add(framework)
        
        # Check for databases
        for db in self.databases:
            if db in text_lower:
                found_skills.add(db)
        
        # Check for cloud platforms
        for platform in self.cloud_platforms:
            if platform in text_lower:
                found_skills.add(platform)
        
        # Check for tools
        for tool in self.tools:
            if tool in text_lower:
                found_skills.add(tool)
        
        return list(found_skills)
    
    def _calculate_skill_proficiency(self, skill_name: str, evidence_list: List[SkillEvidence]) -> Optional[SkillProficiency]:
        """Calculate proficiency level for a skill based on evidence."""
        
        if not evidence_list:
            return None
        
        # Calculate weighted confidence
        total_weight = 0
        weighted_confidence = 0
        
        for evidence in evidence_list:
            weight = evidence.usage_count
            weighted_confidence += evidence.confidence * weight
            total_weight += weight
        
        if total_weight == 0:
            return None
        
        average_confidence = weighted_confidence / total_weight
        
        # Calculate years of experience estimate
        years_experience = self._estimate_years_experience(evidence_list)
        
        # Determine proficiency level
        proficiency_level = self._determine_proficiency_level(average_confidence, years_experience, evidence_list)
        
        # Calculate usage frequency
        usage_frequency = self._calculate_usage_frequency(evidence_list)
        
        # Count projects and repositories
        project_count = len([e for e in evidence_list if e.context and "repo" in e.context])
        repository_count = len([e for e in evidence_list if e.source == DataSource.GITHUB])
        
        # Get last used date
        last_used = self._get_last_used_date(evidence_list)
        
        return SkillProficiency(
            skill_name=skill_name,
            proficiency_level=proficiency_level,
            confidence_score=average_confidence,
            years_experience=years_experience,
            evidence_sources=[e.source for e in evidence_list],
            last_used=last_used,
            usage_frequency=usage_frequency,
            project_count=project_count,
            repository_count=repository_count
        )
    
    def _estimate_years_experience(self, evidence_list: List[SkillEvidence]) -> Optional[float]:
        """Estimate years of experience for a skill."""
        # This is a simplified estimation
        # In a real implementation, you would analyze:
        # - Repository creation dates
        # - Commit history
        # - Resume experience dates
        # - Skill mentions over time
        
        total_usage = sum(e.usage_count for e in evidence_list)
        
        if total_usage == 0:
            return None
        
        # Rough estimation based on usage count
        if total_usage >= 50:
            return min(10.0, total_usage / 10)  # Cap at 10 years
        elif total_usage >= 20:
            return min(5.0, total_usage / 5)
        elif total_usage >= 10:
            return min(3.0, total_usage / 3)
        else:
            return min(1.0, total_usage / 2)
    
    def _determine_proficiency_level(
        self,
        confidence: float,
        years_experience: Optional[float],
        evidence_list: List[SkillEvidence]
    ) -> SkillProficiencyLevel:
        """Determine proficiency level based on confidence and evidence."""
        
        # Get thresholds from settings
        thresholds = settings.skill_proficiency_thresholds
        
        # Count evidence sources
        source_count = len(set(e.source for e in evidence_list))
        
        # Adjust confidence based on evidence diversity
        adjusted_confidence = confidence * (1 + (source_count - 1) * 0.1)
        
        # Determine level based on adjusted confidence and years
        if adjusted_confidence >= thresholds.get("expert", 0.9) and (years_experience or 0) >= 5:
            return SkillProficiencyLevel.EXPERT
        elif adjusted_confidence >= thresholds.get("advanced", 0.8) and (years_experience or 0) >= 3:
            return SkillProficiencyLevel.ADVANCED
        elif adjusted_confidence >= thresholds.get("intermediate", 0.6) and (years_experience or 0) >= 1:
            return SkillProficiencyLevel.INTERMEDIATE
        else:
            return SkillProficiencyLevel.BEGINNER
    
    def _calculate_usage_frequency(self, evidence_list: List[SkillEvidence]) -> Optional[str]:
        """Calculate usage frequency based on evidence."""
        # This would be implemented with more sophisticated analysis
        # For now, return a simple estimation
        
        total_usage = sum(e.usage_count for e in evidence_list)
        
        if total_usage >= 100:
            return "daily"
        elif total_usage >= 50:
            return "weekly"
        elif total_usage >= 20:
            return "monthly"
        else:
            return "rarely"
    
    def _get_last_used_date(self, evidence_list: List[SkillEvidence]) -> Optional[date]:
        """Get the most recent usage date from evidence."""
        dates = [e.last_used for e in evidence_list if e.last_used]
        return max(dates) if dates else None
    
    def _extract_resume_skills(self, resume_skills: Dict[str, Any]) -> List[str]:
        """Extract all skills from resume data."""
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