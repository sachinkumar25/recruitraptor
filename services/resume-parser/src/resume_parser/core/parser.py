"""Resume parsing using LLMs to extract structured data from text."""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import structlog
from pydantic import BaseModel, Field
from openai import OpenAI

from ..utils.logger import get_logger

logger = get_logger(__name__)

# --- Pydantic Models for Structured Output ---

class PersonalInfo(BaseModel):
    name: Optional[str] = Field(None, description="Full name of the candidate")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="City, State, or Country")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    github_url: Optional[str] = Field(None, description="GitHub profile URL")

class EducationItem(BaseModel):
    institution: str = Field(..., description="Name of the university or school")
    degree: Optional[str] = Field(None, description="Degree obtained (e.g., BS, MS)")
    field_of_study: Optional[str] = Field(None, description="Major or field of study")
    start_date: Optional[str] = Field(None, description="Start date (e.g., 'Aug 2020')")
    end_date: Optional[str] = Field(None, description="End date (e.g., 'May 2024') or 'Present'")
    gpa: Optional[float] = Field(None, description="GPA if available")

class WorkExperienceItem(BaseModel):
    company: str = Field(..., description="Name of the company or organization. Do NOT include job titles here.")
    position: str = Field(..., description="Job title (e.g., 'Software Engineer', 'Architect')")
    start_date: Optional[str] = Field(None, description="Start date")
    end_date: Optional[str] = Field(None, description="End date or 'Present'")
    description: Optional[str] = Field(None, description="Summary of responsibilities and achievements")

class Skills(BaseModel):
    technical_skills: List[str] = Field(default_factory=list, description="List of technical skills (languages, frameworks, tools)")
    soft_skills: List[str] = Field(default_factory=list, description="List of soft skills (e.g., Leadership, Communication)")

class Resume(BaseModel):
    personal_info: PersonalInfo
    education: List[EducationItem] = Field(default_factory=list)
    work_experience: List[WorkExperienceItem] = Field(default_factory=list)
    skills: Skills
    summary: Optional[str] = Field(None, description="Professional summary or objective")

# --- LLM Parser Implementation ---

class ResumeParser:
    """Extracts structured data from resume text using OpenAI's LLM."""

    def __init__(self):
        """Initialize the ResumeParser with OpenAI client."""
        self.logger = logger
        
        # Load environment variables
        from dotenv import load_dotenv
        
        # Try loading from current directory first, then root
        load_dotenv()
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..'))
        load_dotenv(os.path.join(project_root, '.env'))
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.logger.error("OPENAI_API_KEY not found in environment variables.")
            
            # Additional debug info
            self.logger.error(f"Current working directory: {os.getcwd()}")
            self.logger.error(f"Project root calculated as: {project_root}")
            
            raise ValueError("OPENAI_API_KEY is required for LLM parsing.")
            
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini" 
        self.logger.info(f"Initialized LLM Parser with model: {self.model}")

    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parse resume text and extract structured data using LLM.

        Args:
            text: Clean resume text

        Returns:
            Dictionary containing extracted fields matching the legacy structure.
        """
        self.logger.info("Starting LLM resume parsing", text_length=len(text))
        
        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": f"Extract information from this resume:\n\n{text}"},
                ],
                response_format=Resume,
            )

            parsed_resume = completion.choices[0].message.parsed
            
            # Convert Pydantic model to dict and normalize to match legacy output format
            return self._normalize_output(parsed_resume, text)

        except Exception as e:
            self.logger.error(f"LLM parsing failed: {str(e)}")
            # Fallback or empty return? For now, re-raise or return empty structure
            raise e

    def _get_system_prompt(self) -> str:
        """Returns the system prompt for the LLM."""
        return """
        You are an expert Resume Parser. Your job is to extract structured data from resume text.
        
        CRITICAL RULES:
        1. **Company vs. Position:** accurately distinguish between Company Names and Job Titles. 
           - 'Architect', 'Developer', 'Engineer' are POSITIONS, not Companies.
           - If a line says "Architect \n Languages...", 'Architect' is the position.
        2. **Education vs. Experience:** 
           - Do NOT put Universities or Degrees in Work Experience.
           - Do NOT put Work Experience in Education.
        3. **Dates:** Extract dates exactly as they appear (e.g., "May 2024", "2020 - 2024").
        4. **Skills:** Categorize skills intelligently.
        5. **Contact Info:** Extract email, phone, and links from the header/top of the text.
           - **URLS:** For LinkedIn and GitHub, extract the FULL URL (e.g., "https://linkedin.com/in/username"). If only a username is present, construct the likely URL.

        Output must be valid JSON matching the schema provided.
        """

    def _normalize_output(self, resume: Resume, original_text: str) -> Dict[str, Any]:
        """
        Convert the Pydantic 'Resume' object into the dictionary format 
        expected by the rest of the application (legacy format).
        """
        
        # Transform Education
        education_data = {
            'institutions': [edu.institution for edu in resume.education],
            'degrees': [edu.degree for edu in resume.education if edu.degree],
            'fields_of_study': [edu.field_of_study for edu in resume.education if edu.field_of_study],
            'dates': [f"{edu.start_date} - {edu.end_date}" if edu.start_date and edu.end_date else (edu.end_date or edu.start_date or "") for edu in resume.education],
            'gpa': {'value': resume.education[0].gpa if resume.education and resume.education[0].gpa else None, 'confidence': 1.0},
            'confidence': 1.0
        }

        # Transform Experience
        experience_data = {
            'companies': [exp.company for exp in resume.work_experience],
            'positions': [exp.position for exp in resume.work_experience],
            'dates': [f"{exp.start_date} - {exp.end_date}" if exp.start_date and exp.end_date else (exp.end_date or exp.start_date or "") for exp in resume.work_experience],
            'descriptions': [exp.description for exp in resume.work_experience if exp.description],
            'confidence': 1.0
        }

        # Transform Personal Info
        personal_info_data = {
            'name': {'value': resume.personal_info.name, 'confidence': 1.0},
            'email': {'value': resume.personal_info.email, 'confidence': 1.0},
            'phone': {'value': resume.personal_info.phone, 'confidence': 1.0},
            'location': {'value': resume.personal_info.location, 'confidence': 1.0},
            'linkedin_url': {'value': resume.personal_info.linkedin_url, 'confidence': 1.0},
            'github_url': {'value': resume.personal_info.github_url, 'confidence': 1.0},
            'confidence': 1.0
        }
        
        # Transform Skills
        skills_data = {
            'technical_skills': resume.skills.technical_skills,
            'soft_skills': resume.skills.soft_skills,
            'confidence': 1.0
        }

        return {
            'personal_info': personal_info_data,
            'education': education_data,
            'experience': experience_data,
            'skills': skills_data,
            'metadata': {
                'total_words': len(original_text.split()),
                'parsing_timestamp': datetime.now().isoformat(),
                'confidence_overall': 1.0,
                'extraction_method': 'llm-gpt-4o-mini',
                'extraction_errors': []
            }
        }
