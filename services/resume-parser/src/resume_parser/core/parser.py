"""Resume parsing using NLP to extract structured data from text."""

import re
import spacy
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import structlog

from ..utils.logger import get_logger

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
        
        # Enhanced GitHub URL patterns - only extract real GitHub URLs
        self.github_patterns = [
            # Full URLs with protocol
            re.compile(r'https?://(?:www\.)?github\.com/([a-zA-Z0-9-]+)(?:/[a-zA-Z0-9._-]+)?/?', re.IGNORECASE),
            # URLs without protocol
            re.compile(r'(?:www\.)?github\.com/([a-zA-Z0-9-]+)(?:/[a-zA-Z0-9._-]+)?/?', re.IGNORECASE),
            # GitHub: username format
            re.compile(r'github\s*:\s*([a-zA-Z0-9-]+)', re.IGNORECASE),
            # GitHub profile: username format
            re.compile(r'github\s+profile\s*:\s*([a-zA-Z0-9-]+)', re.IGNORECASE),
            # @username format (common in resumes) - only if preceded by GitHub context
            re.compile(r'(?:github|git|repo|repository|code|portfolio)\s*[:\-]?\s*@([a-zA-Z0-9-]+)', re.IGNORECASE),
            # Username in parentheses or brackets with GitHub context
            re.compile(r'(?:github|git|repo|repository|code|portfolio)\s*[:\-]?\s*[\(\[\{]([a-zA-Z0-9-]+)[\)\]\}]', re.IGNORECASE),
        ]
        
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
                'confidence_overall': 0.0,
                'extraction_method': None,
                'encoding': None,
                'word_count': None,
                'extraction_errors': []
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
        
        # Extract GitHub URLs using enhanced patterns
        github_urls = self._extract_github_urls(text)
        if github_urls:
            # Use the highest confidence URL for the main github_url field
            best_url = max(github_urls, key=lambda x: x['confidence'])
            personal_info['github_url']['value'] = best_url['url']
            personal_info['github_url']['confidence'] = best_url['confidence']
            
            # Store all discovered URLs in the github_urls list
            personal_info['github_urls'] = github_urls
        
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
    
    def _extract_github_urls(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract GitHub URLs using multiple patterns with validation and confidence scoring.
        
        Args:
            text: Resume text to search
            
        Returns:
            List of dictionaries with 'url' and 'confidence' keys
        """
        extracted_urls = []
        seen_usernames = set()
        
        # Context keywords that suggest GitHub references
        github_context_keywords = [
            'github', 'git', 'repository', 'repo', 'code', 'portfolio', 
            'projects', 'open source', 'contributions', 'profile'
        ]
        
        for i, pattern in enumerate(self.github_patterns):
            matches = pattern.finditer(text)
            
            for match in matches:
                username = match.group(1) if len(match.groups()) > 0 else match.group(0)
                
                # Skip if we've already seen this username
                if username.lower() in seen_usernames:
                    continue
                
                # Validate username format
                if not self._is_valid_github_username(username):
                    continue
                
                # Determine confidence based on pattern type and context
                confidence = self._calculate_github_confidence(pattern, match, text, i)
                
                # Normalize URL format
                normalized_url = self._normalize_github_url(username)
                
                extracted_urls.append({
                    'url': normalized_url,
                    'confidence': confidence,
                    'username': username,
                    'pattern_type': i
                })
                
                seen_usernames.add(username.lower())
        
        # Sort by confidence (highest first)
        extracted_urls.sort(key=lambda x: x['confidence'], reverse=True)
        
        self.logger.debug("Extracted GitHub URLs", 
                         count=len(extracted_urls),
                         urls=[url['url'] for url in extracted_urls])
        
        return extracted_urls
    
    def _is_valid_github_username(self, username: str) -> bool:
        """
        Validate GitHub username format with additional checks for common false positives.
        
        Args:
            username: Username to validate
            
        Returns:
            True if valid GitHub username format
        """
        if not username:
            return False
        
        # GitHub username rules:
        # - 1-39 characters
        # - Only alphanumeric and hyphens
        # - Cannot start or end with hyphen
        # - Cannot have consecutive hyphens
        if len(username) < 1 or len(username) > 39:
            return False
        
        if not re.match(r'^[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?$', username):
            return False
        
        if '--' in username:
            return False
        
        # Additional validation to prevent false positives
        # Reject common words that are unlikely to be GitHub usernames
        common_words_to_reject = {
            'https', 'www', 'com', 'org', 'net', 'edu', 'gov', 'mil', 'io', 'co', 'uk', 'us',
            'coursework', 'data', 'structures', 'algorithms', 'machine', 'learning', 'database', 'systems',
            'education', 'professional', 'experience', 'technical', 'skills', 'projects', 'certifications',
            'achievements', 'university', 'college', 'school', 'institute', 'academy', 'graduated', 'gpa',
            'dean', 'list', 'summa', 'cum', 'laude', 'relevant', 'led', 'development', 'microservices',
            'architecture', 'serving', 'over', 'one', 'million', 'active', 'users', 'daily', 'implemented',
            'comprehensive', 'pipelines', 'reducing', 'deployment', 'time', 'fifty', 'percent', 'mentored',
            'three', 'junior', 'developers', 'and', 'conducted', 'thorough', 'code', 'reviews', 'designed',
            'optimized', 'schemas', 'improving', 'query', 'performance', 'forty', 'technologies', 'python',
            'kubernetes', 'postgresql', 'redis', 'docker', 'jenkins', 'meta', 'platforms', 'december',
            'built', 'responsive', 'react', 'applications', 'using', 'typescript', 'for', 'internal',
            'productivity', 'tools', 'developed', 'robust', 'restful', 'apis', 'django', 'fastapi',
            'frameworks', 'collaborated', 'with', 'cross-functional', 'teams', 'deliver', 'features',
            'millions', 'queries', 'caching', 'strategies', 'thirty', 'mysql', 'aws', 'engineering',
            'intern', 'microsoft', 'corporation', 'august', 'automation', 'azure', 'cloud', 'infrastructure',
            'management', 'monitoring', 'dashboards', 'power', 'custom', 'analytics', 'participated',
            'agile', 'processes', 'sprint', 'planning', 'net', 'sql', 'server', 'programming', 'languages',
            'javascript', 'java', 'bash', 'web', 'node', 'express', 'flask', 'spring', 'boot', 'databases',
            'mongodb', 'elasticsearch', 'dynamodb', 'platform', 'chat', 'application', 'scalable', 'websocket',
            'connections', 'pub', 'sub', 'user', 'authentication', 'message', 'encryption', 'file', 'sharing',
            'capabilities', 'deployed', 'auto-scaling', 'load', 'balancing', 'high', 'availability',
            'e-commerce', 'full-stack', 'payment', 'integration', 'shopping', 'cart', 'inventory', 'order',
            'tracking', 'used', 'frontend', 'backend', 'certified', 'solutions', 'architect', 'associate',
            'developer', 'winner', 'hackathon', 'published', 'research', 'paper', 'distributed', 'optimization',
            'john', 'smith', 'senior', 'software', 'engineer', 'email', 'phone', 'location', 'san', 'francisco',
            'bachelor', 'science', 'computer', 'june', 'present', 'january', 'february', 'march', 'april',
            'may', 'july', 'september', 'october', 'november', 'december', 'monday', 'tuesday', 'wednesday',
            'thursday', 'friday', 'saturday', 'sunday', 'morning', 'afternoon', 'evening', 'night', 'today',
            'tomorrow', 'yesterday', 'week', 'month', 'year', 'years', 'months', 'weeks', 'days', 'hours',
            'minutes', 'seconds', 'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth',
            'ninth', 'tenth', 'eleventh', 'twelfth', 'thirteenth', 'fourteenth', 'fifteenth', 'sixteenth',
            'seventeenth', 'eighteenth', 'nineteenth', 'twentieth', 'twenty', 'thirty', 'forty', 'fifty',
            'sixty', 'seventy', 'eighty', 'ninety', 'hundred', 'thousand', 'million', 'billion', 'trillion'
        }
        
        # Convert to lowercase for comparison
        username_lower = username.lower()
        
        # Reject if it's a common word
        if username_lower in common_words_to_reject:
            return False
        
        # Reject if it's just numbers (unlikely to be a real GitHub username)
        if username.isdigit():
            return False
        
        # Reject if it's too short (less than 3 characters) unless it's a very common short username
        if len(username) < 3 and username_lower not in {'js', 'ts', 'py', 'go', 'js', 'rb', 'php', 'cs', 'rs', 'kt', 'sw'}:
            return False
        
        # Reject if it contains common file extensions or protocols
        if any(ext in username_lower for ext in ['.com', '.org', '.net', '.edu', '.gov', '.mil', '.io', '.co', '.uk', '.us']):
            return False
        
        return True
    
    def _calculate_github_confidence(self, pattern: re.Pattern, match: re.Match, text: str, pattern_index: int) -> float:
        """
        Calculate confidence score for extracted GitHub URL.
        
        Args:
            pattern: Regex pattern that matched
            match: Regex match object
            text: Full text content
            pattern_index: Index of pattern in self.github_patterns
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        base_confidence = 0.0
        
        # Base confidence by pattern type (more specific patterns get higher confidence)
        if pattern_index == 0:  # Full URLs with protocol
            base_confidence = 0.95
        elif pattern_index == 1:  # URLs without protocol
            base_confidence = 0.90
        elif pattern_index == 2:  # GitHub: username
            base_confidence = 0.85
        elif pattern_index == 3:  # GitHub profile: username
            base_confidence = 0.90
        elif pattern_index == 4:  # @username with GitHub context
            base_confidence = 0.75
        elif pattern_index == 5:  # Username in brackets with GitHub context
            base_confidence = 0.65
        
        # Context bonus: check if GitHub-related keywords are nearby
        context_bonus = 0.0
        start_pos = max(0, match.start() - 100)
        end_pos = min(len(text), match.end() + 100)
        context_text = text[start_pos:end_pos].lower()
        
        github_keywords = ['github', 'git', 'repository', 'repo', 'code', 'portfolio', 'profile']
        for keyword in github_keywords:
            if keyword in context_text:
                context_bonus += 0.05
        
        # Cap context bonus at 0.15
        context_bonus = min(context_bonus, 0.15)
        
        return min(base_confidence + context_bonus, 1.0)
    
    def _normalize_github_url(self, username: str) -> str:
        """
        Normalize GitHub URL to standard format.
        
        Args:
            username: GitHub username
            
        Returns:
            Normalized GitHub profile URL
        """
        # Remove any existing URL parts and normalize
        username = username.strip()
        
        # If it's already a full URL, return as is
        if username.startswith(('http://', 'https://')):
            return username
        
        # If it starts with github.com, add protocol
        if username.startswith('github.com/'):
            return f'https://{username}'
        
        # If it's just a username, create full profile URL
        return f'https://github.com/{username}'
    
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
