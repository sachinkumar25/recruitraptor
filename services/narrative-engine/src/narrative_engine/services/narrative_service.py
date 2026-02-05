"""Core narrative generation service."""

import time
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..core.config import settings
from ..core.models import (
    EnrichedProfile, JobRequirement, NarrativeStyle, LLMProvider,
    GeneratedNarrative, NarrativeSection, NarrativeGenerationRequest,
    BioNarrativeRequest, BioNarrativeResponse
)
from ..services.llm_service import llm_service
from ..utils.logger import service_logger, log_narrative_generation, log_error


class NarrativeService:
    """Service for generating AI-powered candidate narratives."""
    
    def __init__(self):
        """Initialize narrative service."""
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def generate_narrative(
        self,
        request: NarrativeGenerationRequest,
        enriched_profile: EnrichedProfile
    ) -> GeneratedNarrative:
        """Generate comprehensive narrative for candidate."""
        
        start_time = time.time()
        
        try:
            # Build context-aware prompt
            prompt = self._build_narrative_prompt(
                enriched_profile=enriched_profile,
                job_requirement=request.job_requirement,
                narrative_style=request.narrative_style,
                custom_prompts=request.custom_prompts
            )
            
            # Generate narrative with LLM
            llm_response = llm_service.generate_narrative(
                prompt=prompt,
                provider=request.llm_provider or LLMProvider(settings.default_llm_provider),
                model=settings.default_model,
                max_tokens=request.generation_parameters.get("max_tokens", settings.max_tokens),
                temperature=request.generation_parameters.get("temperature", settings.temperature)
            )
            
            # Parse and structure the response
            narrative = self._parse_narrative_response(
                llm_response=llm_response,
                request=request,
                enriched_profile=enriched_profile
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            log_narrative_generation(
                candidate_id=request.candidate_id,
                narrative_style=request.narrative_style.value,
                llm_provider=llm_response["provider"].value,
                model=llm_response["model"],
                processing_time_ms=processing_time,
                success=True
            )
            
            return narrative
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            log_error(
                "narrative_generation_failed",
                str(e),
                context={
                    "candidate_id": request.candidate_id,
                    "narrative_style": request.narrative_style.value,
                    "processing_time_ms": processing_time
                }
            )
            raise
    
    def _build_narrative_prompt(
        self,
        enriched_profile: EnrichedProfile,
        job_requirement: JobRequirement,
        narrative_style: NarrativeStyle,
        custom_prompts: Optional[Dict[str, str]] = None
    ) -> str:
        """Build context-aware prompt for narrative generation."""
        
        # Base prompt template
        base_prompt = self._get_base_prompt_template(narrative_style)
        
        # Candidate information
        candidate_info = self._format_candidate_info(enriched_profile)
        
        # Job requirements
        job_info = self._format_job_requirements(job_requirement)
        
        # Skills analysis
        skills_analysis = self._format_skills_analysis(enriched_profile, job_requirement)
        
        # GitHub analysis (if available)
        github_analysis = self._format_github_analysis(enriched_profile)
        
        # Custom prompts (if provided)
        custom_instructions = ""
        if custom_prompts:
            custom_instructions = "\n\nCustom Instructions:\n" + "\n".join([
                f"- {section}: {prompt}" for section, prompt in custom_prompts.items()
            ])
        
        # Combine all components
        prompt = f"""{base_prompt}

CANDIDATE INFORMATION:
{candidate_info}

JOB REQUIREMENTS:
{job_info}

SKILLS ANALYSIS:
{skills_analysis}

GITHUB ANALYSIS:
{github_analysis}{custom_instructions}

Please generate a comprehensive narrative assessment following the specified structure and style. Focus on providing actionable insights and evidence-based recommendations."""
        
        return prompt
    
    def _get_base_prompt_template(self, narrative_style: NarrativeStyle) -> str:
        """Get base prompt template based on narrative style."""
        
        templates = {
            NarrativeStyle.EXECUTIVE: """You are an expert executive recruiter. Generate a high-level executive summary for a C-suite audience. Focus on strategic impact, leadership potential, and business value. Keep it concise and business-focused.""",
            
            NarrativeStyle.TECHNICAL: """You are a senior technical recruiter specializing in engineering roles. Generate a detailed technical assessment for engineering managers. Focus on technical depth, problem-solving abilities, and technical leadership potential. Include specific technical evidence and project analysis.""",
            
            NarrativeStyle.COMPREHENSIVE: """You are a senior talent acquisition specialist. Generate a comprehensive candidate assessment that balances technical skills, cultural fit, and growth potential. Provide detailed analysis with evidence from their background and projects.""",
            
            NarrativeStyle.CONCISE: """You are a talent acquisition specialist. Generate a concise candidate assessment for initial screening. Focus on key qualifications, red flags, and immediate next steps. Keep it brief but informative."""
        }
        
        return templates.get(narrative_style, templates[NarrativeStyle.COMPREHENSIVE])
    
    def _format_candidate_info(self, profile: EnrichedProfile) -> str:
        """Format candidate information for prompt."""
        info = f"""
Name: {profile.name}
Email: {profile.email or 'Not provided'}
Location: {profile.location or 'Not provided'}
GitHub: {profile.github_url or 'Not provided'}
Years of Experience: {profile.experience_years or 'Not specified'}
"""
        return info
    
    def _format_job_requirements(self, job: JobRequirement) -> str:
        """Format job requirements for prompt."""
        requirements = f"""
Title: {job.title}
Department: {job.department or 'Not specified'}
Experience Level: {job.experience_level or 'Not specified'}
Required Skills: {', '.join(job.required_skills) if job.required_skills else 'Not specified'}
Preferred Skills: {', '.join(job.preferred_skills) if job.preferred_skills else 'Not specified'}
Responsibilities: {'; '.join(job.responsibilities) if job.responsibilities else 'Not specified'}
Company Context: {job.company_context or 'Not provided'}
"""
        return requirements
    
    def _format_skills_analysis(self, profile: EnrichedProfile, job: JobRequirement) -> str:
        """Format skills analysis for prompt."""
        skills_info = f"""
Technical Skills: {len(profile.technical_skills)} skills identified
Programming Languages: {', '.join(profile.programming_languages) if profile.programming_languages else 'None identified'}
Frameworks: {', '.join(profile.frameworks) if profile.frameworks else 'None identified'}
Job Relevance Score: {profile.job_relevance_score or 'Not calculated'}
Skill Match Percentage: {profile.skill_match_percentage or 'Not calculated'}
Skill Strengths: {', '.join(profile.skill_strengths) if profile.skill_strengths else 'None identified'}
Skill Gaps: {', '.join(profile.skill_gaps) if profile.skill_gaps else 'None identified'}
"""
        return skills_info
    
    def _format_github_analysis(self, profile: EnrichedProfile) -> str:
        """Format GitHub analysis for prompt."""
        if not profile.github_analysis:
            return "GitHub Analysis: Not available"
        
        github = profile.github_analysis
        analysis = f"""
GitHub Analysis:
- Total Repositories: {github.get('total_repositories', 'Unknown')}
- Total Stars: {github.get('total_stars', 'Unknown')}
- Languages: {', '.join(github.get('languages', [])) if github.get('languages') else 'None identified'}
- Recent Activity Score: {github.get('recent_activity_score', 'Unknown')}
- Profile URL: {profile.github_url or 'Not provided'}
"""
        return analysis
    
    def _parse_narrative_response(
        self,
        llm_response: Dict[str, Any],
        request: NarrativeGenerationRequest,
        enriched_profile: EnrichedProfile
    ) -> GeneratedNarrative:
        """Parse LLM response into structured narrative."""
        
        content = llm_response["content"]
        
        # Extract sections from the response
        sections = self._extract_narrative_sections(content)
        
        # Create narrative sections
        executive_summary = NarrativeSection(
            title="Executive Summary",
            content=sections.get("executive_summary", "Executive summary not generated."),
            confidence_score=0.8,
            evidence_sources=["resume", "github_analysis"]
        )
        
        technical_assessment = NarrativeSection(
            title="Technical Skills Assessment",
            content=sections.get("technical_skills_assessment", "Technical assessment not generated."),
            confidence_score=0.9,
            evidence_sources=["technical_skills", "programming_languages", "frameworks"]
        )
        
        experience_relevance = NarrativeSection(
            title="Experience Relevance",
            content=sections.get("experience_relevance", "Experience relevance not analyzed."),
            confidence_score=0.7,
            evidence_sources=["experience_years", "job_relevance_score"]
        )
        
        project_analysis = None
        if sections.get("project_portfolio_analysis"):
            project_analysis = NarrativeSection(
                title="Project Portfolio Analysis",
                content=sections["project_portfolio_analysis"],
                confidence_score=0.6,
                evidence_sources=["github_analysis"]
            )
        
        growth_potential = NarrativeSection(
            title="Growth Potential",
            content=sections.get("growth_potential", "Growth potential not assessed."),
            confidence_score=0.7,
            evidence_sources=["skill_strengths", "github_analysis"]
        )
        
        # Calculate overall confidence
        confidence_scores = [
            executive_summary.confidence_score,
            technical_assessment.confidence_score,
            experience_relevance.confidence_score,
            growth_potential.confidence_score
        ]
        if project_analysis:
            confidence_scores.append(project_analysis.confidence_score)
        
        overall_confidence = sum(confidence_scores) / len(confidence_scores)
        
        # Generate overall assessment and recommendation
        overall_assessment = self._generate_overall_assessment(sections, enriched_profile)
        recommendation = self._generate_recommendation(sections, enriched_profile)
        
        return GeneratedNarrative(
            candidate_id=request.candidate_id,
            job_requirement=request.job_requirement,
            narrative_style=request.narrative_style,
            executive_summary=executive_summary,
            technical_skills_assessment=technical_assessment,
            experience_relevance=experience_relevance,
            project_portfolio_analysis=project_analysis,
            growth_potential=growth_potential,
            llm_provider=llm_response["provider"],
            model_used=llm_response["model"],
            generation_parameters={
                "max_tokens": llm_response.get("tokens_used"),
                "temperature": request.generation_parameters.get("temperature", settings.temperature)
            },
            overall_assessment=overall_assessment,
            recommendation=recommendation,
            confidence_score=overall_confidence
        )
    
    def _extract_narrative_sections(self, content: str) -> Dict[str, str]:
        """Extract narrative sections from LLM response."""
        sections = {}
        
        # Simple section extraction (can be enhanced with more sophisticated parsing)
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            lower_line = line.lower()
            if any(keyword in lower_line for keyword in ["executive summary", "summary"]):
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = "executive_summary"
                current_content = []
            elif any(keyword in lower_line for keyword in ["technical", "skills", "assessment"]):
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = "technical_skills_assessment"
                current_content = []
            elif any(keyword in lower_line for keyword in ["experience", "relevance"]):
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = "experience_relevance"
                current_content = []
            elif any(keyword in lower_line for keyword in ["project", "portfolio", "github"]):
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = "project_portfolio_analysis"
                current_content = []
            elif any(keyword in lower_line for keyword in ["growth", "potential", "development"]):
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = "growth_potential"
                current_content = []
            else:
                if current_section:
                    current_content.append(line)
        
        # Add the last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _generate_overall_assessment(self, sections: Dict[str, str], profile: EnrichedProfile) -> str:
        """Generate overall assessment based on sections and profile."""
        if profile.job_relevance_score and profile.job_relevance_score >= 0.7:
            return "Strong candidate with excellent technical skills and relevant experience."
        elif profile.job_relevance_score and profile.job_relevance_score >= 0.5:
            return "Good candidate with solid technical background and potential for growth."
        else:
            return "Candidate may require additional training or experience for this role."
    
    def _generate_recommendation(self, sections: Dict[str, str], profile: EnrichedProfile) -> str:
        """Generate hiring recommendation."""
        if profile.job_relevance_score and profile.job_relevance_score >= 0.7:
            return "Recommend proceeding to technical interview."
        elif profile.job_relevance_score and profile.job_relevance_score >= 0.5:
            return "Recommend initial screening call to assess fit."
        else:
            return "Consider for future opportunities or different roles."
    
    async def generate_bio_narrative(
        self,
        request: BioNarrativeRequest
    ) -> BioNarrativeResponse:
        """Generate a professional bio narrative for a candidate."""

        start_time = time.time()

        try:
            profile = request.enriched_profile

            # Build bio-specific prompt
            prompt = self._build_bio_prompt(
                profile=profile,
                bio_style=request.bio_style,
                max_length=request.max_length
            )

            # Generate bio with LLM
            llm_response = llm_service.generate_narrative(
                prompt=prompt,
                provider=request.llm_provider or LLMProvider(settings.default_llm_provider),
                model=settings.default_model,
                max_tokens=min(request.max_length * 2, settings.max_tokens),
                temperature=0.7
            )

            processing_time = (time.time() - start_time) * 1000

            log_narrative_generation(
                candidate_id=request.candidate_id,
                narrative_style=f"bio_{request.bio_style}",
                llm_provider=llm_response["provider"].value,
                model=llm_response["model"],
                processing_time_ms=processing_time,
                success=True
            )

            return BioNarrativeResponse(
                success=True,
                bio=llm_response["content"].strip(),
                processing_time_ms=processing_time
            )

        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            log_error(
                "bio_narrative_generation_failed",
                str(e),
                context={
                    "candidate_id": request.candidate_id,
                    "bio_style": request.bio_style,
                    "processing_time_ms": processing_time
                }
            )
            return BioNarrativeResponse(
                success=False,
                error_message=str(e),
                processing_time_ms=processing_time
            )

    def _build_bio_prompt(
        self,
        profile: EnrichedProfile,
        bio_style: str,
        max_length: int
    ) -> str:
        """Build prompt for bio narrative generation."""

        style_instructions = {
            "professional": "Write a formal, professional bio suitable for LinkedIn or a company website. Focus on achievements, expertise, and career trajectory.",
            "casual": "Write a friendly, approachable bio suitable for team introductions or personal websites. Keep it warm and personable while highlighting key skills.",
            "technical": "Write a detailed technical bio suitable for engineering blogs or technical conferences. Emphasize technical skills, projects, and problem-solving abilities."
        }

        style_instruction = style_instructions.get(bio_style, style_instructions["professional"])

        # Build skills summary
        skills_text = ""
        if profile.programming_languages:
            skills_text += f"Programming Languages: {', '.join(profile.programming_languages[:5])}\n"
        if profile.frameworks:
            skills_text += f"Frameworks: {', '.join(profile.frameworks[:5])}\n"
        if profile.technical_skills:
            skill_names = [s.get('name', '') if isinstance(s, dict) else str(s) for s in profile.technical_skills[:10]]
            skills_text += f"Technical Skills: {', '.join(skill_names)}\n"

        # Build GitHub summary
        github_text = ""
        if profile.github_analysis:
            github = profile.github_analysis
            github_text = f"""
GitHub Activity:
- Repositories: {github.get('total_repositories', 'N/A')}
- Languages: {', '.join(github.get('languages', [])[:5]) if github.get('languages') else 'N/A'}
- Recent Activity Score: {github.get('recent_activity_score', 'N/A')}
"""

        prompt = f"""You are a professional bio writer. {style_instruction}

Generate a compelling bio narrative (maximum {max_length} words) for the following candidate:

CANDIDATE PROFILE:
Name: {profile.name}
Location: {profile.location or 'Not specified'}
Years of Experience: {profile.experience_years or 'Not specified'}

SKILLS AND EXPERTISE:
{skills_text if skills_text else 'Skills not specified'}

{github_text if github_text else ''}

STRENGTHS:
{', '.join(profile.skill_strengths) if profile.skill_strengths else 'Not specified'}

INSTRUCTIONS:
1. Write in third person
2. Start with an engaging hook about the candidate
3. Highlight their key technical expertise
4. Mention notable projects or achievements if available from GitHub
5. End with their professional interests or what they bring to a team
6. Keep it under {max_length} words
7. Do not include placeholder text or ask for more information

Write the bio now:"""

        return prompt

    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()


# Global narrative service instance
narrative_service = NarrativeService() 