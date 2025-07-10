"""Resume parsing using NLP to extract structured data from text."""

import re
import spacy
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import structlog

from shared.utils.logger import get_logger

logger = get_logger(__name__)

class ResumeParser:
    """Extracts structured data from resume text using NLP and pattern matching."""
    
    def __init__(self):
        """Initialize the ResumeParser with spaCy model."""
        self.logger = logger
        try:
            # Load spaCy model for English
            self.nlp = spacy.load("en_core_web_sm")
            self.logger.info("spaCy model loaded successfully")
        except OSError:
            self.logger.error("spaCy model 'en_core_web_sm' not found. Please install with: python -m spacy download en_core_web_sm")
            raise RuntimeError("spaCy model not available")
        
        # Initialize patterns
        self._init_patterns()
    
    def _init_patterns(self):
        """Initialize regex patterns for field extraction."""
        # Email pattern
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        
        # Phone pattern (various formats)
        self.phone_pattern = re.compile(r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})')
        
        # URL patterns
        self.linkedin_pattern = re.compile(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9-]+/?', re.IGNORECASE)
        self.github_pattern = re.compile(r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9-]+/?', re.IGNORECASE)
        
        # Date patterns
        self.date_patterns = [
            re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b', re.IGNORECASE),
            re.compile(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b'),
            re.compile(r'\b\d{4}-\d{1,2}-\d{1,2}\b'),
            re.compile(r'\b(?:Present|Current|Now)\b', re.IGNORECASE)
        ]
        
        # GPA pattern
        self.gpa_pattern = re.compile(r'\bGPA[:\s]*(\d+\.\d+)\b', re.IGNORECASE)
        
        # Skills patterns
        self.skill_patterns = [
            re.compile(r'\b(?:Python|Java|JavaScript|C\+\+|C#|Go|Rust|Swift|Kotlin|TypeScript|PHP|Ruby|Scala|R|MATLAB)\b', re.IGNORECASE),
            re.compile(r'\b(?:React|Angular|Vue|Node\.js|Django|Flask|Spring|Express|Laravel|ASP\.NET|FastAPI)\b', re.IGNORECASE),
            re.compile(r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Jenkins|GitLab|GitHub|CI/CD|DevOps)\b', re.IGNORECASE),
            re.compile(r'\b(?:SQL|PostgreSQL|MySQL|MongoDB|Redis|Elasticsearch|Cassandra|DynamoDB)\b', re.IGNORECASE),
            re.compile(r'\b(?:Machine Learning|AI|Deep Learning|TensorFlow|PyTorch|Scikit-learn|Pandas|NumPy)\b', re.IGNORECASE)
        ]
    
    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parse resume text and extract structured data.
        
        Args:
            text: Clean resume text
            
        Returns:
            Dictionary containing extracted fields with confidence scores
        """
        self.logger.info("Starting resume parsing", text_length=len(text))
        
        # Process text with spaCy
        doc = self.nlp(text)
        
        # Extract different sections
        result = {
            'personal_info': self._extract_personal_info(doc, text),
            'education': self._extract_education(doc, text),
            'experience': self._extract_experience(doc, text),
            'skills': self._extract_skills(doc, text),
            'metadata': {
                'total_words': len(doc),
                'parsing_timestamp': datetime.now().isoformat(),
                'confidence_overall': 0.0
            }
        }
        
        # Calculate overall confidence
        confidences = []
        for section in ['personal_info', 'education', 'experience', 'skills']:
            if result[section].get('confidence', 0) > 0:
                confidences.append(result[section]['confidence'])
        
        if confidences:
            result['metadata']['confidence_overall'] = sum(confidences) / len(confidences)
        
        self.logger.info("Resume parsing completed", 
                        overall_confidence=result['metadata']['confidence_overall'])
        
        return result
    
    def _extract_personal_info(self, doc: spacy.tokens.Doc, text: str) -> Dict[str, Any]:
        """Extract personal information from resume text."""
        personal_info = {
            'name': {'value': None, 'confidence': 0.0},
            'email': {'value': None, 'confidence': 0.0},
            'phone': {'value': None, 'confidence': 0.0},
            'location': {'value': None, 'confidence': 0.0},
            'linkedin_url': {'value': None, 'confidence': 0.0},
            'github_url': {'value': None, 'confidence': 0.0},
            'confidence': 0.0
        }
        
        # Extract email
        email_match = self.email_pattern.search(text)
        if email_match:
            personal_info['email']['value'] = email_match.group()
            personal_info['email']['confidence'] = 0.95
        
        # Extract phone
        phone_match = self.phone_pattern.search(text)
        if phone_match:
            phone_parts = phone_match.groups()
            phone = ''.join(filter(None, phone_parts))
            personal_info['phone']['value'] = phone
            personal_info['phone']['confidence'] = 0.9
        
        # Extract LinkedIn URL
        linkedin_match = self.linkedin_pattern.search(text)
        if linkedin_match:
            personal_info['linkedin_url']['value'] = linkedin_match.group()
            personal_info['linkedin_url']['confidence'] = 0.95
        
        # Extract GitHub URL
        github_match = self.github_pattern.search(text)
        if github_match:
            personal_info['github_url']['value'] = github_match.group()
            personal_info['github_url']['confidence'] = 0.95
        
        # Extract name (first person entity)
        for ent in doc.ents:
            if ent.label_ == "PERSON" and ent.start < 50:  # Assume name is near the beginning
                personal_info['name']['value'] = ent.text
                personal_info['name']['confidence'] = 0.8
                break
        
        # Extract location
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:
                personal_info['location']['value'] = ent.text
                personal_info['location']['confidence'] = 0.7
                break
        
        # Calculate section confidence
        confidences = [info['confidence'] for info in personal_info.values() 
                      if isinstance(info, dict) and 'confidence' in info]
        if confidences:
            personal_info['confidence'] = sum(confidences) / len(confidences)
        
        return personal_info
    
    def _extract_education(self, doc: spacy.tokens.Doc, text: str) -> Dict[str, Any]:
        """Extract education information from resume text."""
        education = {
            'institutions': [],
            'degrees': [],
            'fields_of_study': [],
            'dates': [],
            'gpa': {'value': None, 'confidence': 0.0},
            'confidence': 0.0
        }
        
        # Extract GPA
        gpa_match = self.gpa_pattern.search(text)
        if gpa_match:
            education['gpa']['value'] = float(gpa_match.group(1))
            education['gpa']['confidence'] = 0.9
        
        # Extract education entities
        education_keywords = ['university', 'college', 'school', 'institute', 'academy']
        education_entities = []
        
        for ent in doc.ents:
            if ent.label_ == "ORG":
                # Check if it's likely an educational institution
                for keyword in education_keywords:
                    if keyword.lower() in ent.text.lower():
                        education_entities.append(ent.text)
                        break
        
        education['institutions'] = education_entities
        
        # Extract dates (likely graduation dates)
        dates = []
        for pattern in self.date_patterns:
            matches = pattern.findall(text)
            dates.extend(matches)
        
        education['dates'] = dates[:3]  # Limit to first 3 dates
        
        # Calculate section confidence
        confidences = [education['gpa']['confidence']]
        if education['institutions']:
            confidences.append(0.7)
        if education['dates']:
            confidences.append(0.6)
        
        if confidences:
            education['confidence'] = sum(confidences) / len(confidences)
        
        return education
    
    def _extract_experience(self, doc: spacy.tokens.Doc, text: str) -> Dict[str, Any]:
        """Extract work experience information from resume text."""
        experience = {
            'companies': [],
            'positions': [],
            'dates': [],
            'descriptions': [],
            'confidence': 0.0
        }
        
        # Extract company names (organizations)
        companies = []
        for ent in doc.ents:
            if ent.label_ == "ORG" and ent.text not in experience['companies']:
                companies.append(ent.text)
        
        experience['companies'] = companies[:5]  # Limit to first 5 companies
        
        # Extract job titles (common patterns)
        job_title_patterns = [
            r'\b(?:Software Engineer|Developer|Programmer|Architect|Manager|Lead|Senior|Junior|Full Stack|Frontend|Backend|DevOps|Data Scientist|ML Engineer)\b',
            r'\b(?:Engineer|Developer|Analyst|Consultant|Specialist|Coordinator|Assistant|Director|VP|CTO|CEO)\b'
        ]
        
        positions = []
        for pattern in job_title_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            positions.extend(matches)
        
        experience['positions'] = list(set(positions))[:5]  # Remove duplicates, limit to 5
        
        # Extract dates
        dates = []
        for pattern in self.date_patterns:
            matches = pattern.findall(text)
            dates.extend(matches)
        
        experience['dates'] = dates[:6]  # Limit to first 6 dates
        
        # Calculate section confidence
        confidences = []
        if experience['companies']:
            confidences.append(0.7)
        if experience['positions']:
            confidences.append(0.6)
        if experience['dates']:
            confidences.append(0.5)
        
        if confidences:
            experience['confidence'] = sum(confidences) / len(confidences)
        
        return experience
    
    def _extract_skills(self, doc: spacy.tokens.Doc, text: str) -> Dict[str, Any]:
        """Extract skills from resume text."""
        skills = {
            'technical_skills': [],
            'soft_skills': [],
            'categories': {
                'programming_languages': [],
                'frameworks': [],
                'databases': [],
                'cloud_platforms': [],
                'tools': []
            },
            'confidence': 0.0
        }
        
        # Extract technical skills using patterns
        all_skills = set()
        for pattern in self.skill_patterns:
            matches = pattern.findall(text)
            all_skills.update(matches)
        
        # Categorize skills
        programming_languages = ['Python', 'Java', 'JavaScript', 'C++', 'C#', 'Go', 'Rust', 'Swift', 'Kotlin', 'TypeScript', 'PHP', 'Ruby', 'Scala', 'R', 'MATLAB']
        frameworks = ['React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Spring', 'Express', 'Laravel', 'ASP.NET', 'FastAPI']
        databases = ['SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Cassandra', 'DynamoDB']
        cloud_platforms = ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'GitLab', 'GitHub', 'CI/CD', 'DevOps']
        
        for skill in all_skills:
            if skill in programming_languages:
                skills['categories']['programming_languages'].append(skill)
            elif skill in frameworks:
                skills['categories']['frameworks'].append(skill)
            elif skill in databases:
                skills['categories']['databases'].append(skill)
            elif skill in cloud_platforms:
                skills['categories']['cloud_platforms'].append(skill)
            else:
                skills['categories']['tools'].append(skill)
        
        skills['technical_skills'] = list(all_skills)
        
        # Extract soft skills (common patterns)
        soft_skill_patterns = [
            r'\b(?:Leadership|Communication|Teamwork|Problem Solving|Critical Thinking|Creativity|Adaptability|Time Management|Collaboration|Presentation)\b',
            r'\b(?:Project Management|Agile|Scrum|Kanban|Waterfall|Risk Management|Strategic Planning|Negotiation|Mentoring|Training)\b'
        ]
        
        soft_skills = set()
        for pattern in soft_skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            soft_skills.update(matches)
        
        skills['soft_skills'] = list(soft_skills)
        
        # Calculate section confidence
        confidences = []
        if skills['technical_skills']:
            confidences.append(0.8)
        if skills['soft_skills']:
            confidences.append(0.6)
        
        if confidences:
            skills['confidence'] = sum(confidences) / len(confidences)
        
        return skills
    
    def get_confidence_score(self, extracted_data: Dict[str, Any]) -> float:
        """
        Calculate overall confidence score for extracted data.
        
        Args:
            extracted_data: Parsed resume data
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not extracted_data:
            return 0.0
        
        confidences = []
        
        # Personal info confidence
        if 'personal_info' in extracted_data:
            confidences.append(extracted_data['personal_info'].get('confidence', 0.0))
        
        # Education confidence
        if 'education' in extracted_data:
            confidences.append(extracted_data['education'].get('confidence', 0.0))
        
        # Experience confidence
        if 'experience' in extracted_data:
            confidences.append(extracted_data['experience'].get('confidence', 0.0))
        
        # Skills confidence
        if 'skills' in extracted_data:
            confidences.append(extracted_data['skills'].get('confidence', 0.0))
        
        if not confidences:
            return 0.0
        
        return sum(confidences) / len(confidences)
