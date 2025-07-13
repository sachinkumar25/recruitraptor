"""Test configuration and fixtures for resume parser service."""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from resume_parser.main import app
from resume_parser.core.extractor import TextExtractor
from resume_parser.core.parser import ResumeParser

@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)

@pytest.fixture
def text_extractor():
    """Create a TextExtractor instance for testing."""
    return TextExtractor()

@pytest.fixture
def resume_parser():
    """Create a ResumeParser instance for testing."""
    with patch('resume_parser.core.parser.spacy.load') as mock_spacy:
        mock_nlp = Mock()
        mock_spacy.return_value = mock_nlp
        parser = ResumeParser()
        return parser

@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing."""
    return """
    JOHN DOE
    Software Engineer
    john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe | github.com/johndoe
    
    SUMMARY
    Experienced software engineer with 5+ years developing scalable web applications using Python, JavaScript, and React. Strong background in full-stack development, cloud platforms, and agile methodologies.
    
    EXPERIENCE
    Senior Software Engineer | TechCorp Inc. | 2022 - Present
    - Led development of microservices architecture using FastAPI and Docker
    - Implemented CI/CD pipelines with GitHub Actions and AWS
    - Mentored junior developers and conducted code reviews
    
    Software Engineer | StartupXYZ | 2020 - 2022
    - Built RESTful APIs using Python Flask and PostgreSQL
    - Developed frontend components with React and TypeScript
    - Collaborated with cross-functional teams using Agile methodologies
    
    EDUCATION
    Bachelor of Science in Computer Science | University of Technology | 2016 - 2020
    GPA: 3.8/4.0
    
    SKILLS
    Programming Languages: Python, JavaScript, TypeScript, Java, SQL
    Frameworks & Libraries: React, Node.js, FastAPI, Flask, Django
    Databases: PostgreSQL, MongoDB, Redis
    Cloud Platforms: AWS, Docker, Kubernetes
    Tools: Git, GitHub Actions, Jenkins, Jira
    Soft Skills: Leadership, Communication, Problem Solving, Teamwork
    """

@pytest.fixture
def sample_resume_text_short():
    """Short sample resume text for testing minimum word requirements."""
    return "John Doe Software Engineer Python Java React " * 75

@pytest.fixture
def mock_pdf_content():
    """Mock PDF content for testing."""
    return b"fake pdf content"

@pytest.fixture
def mock_docx_content():
    """Mock DOCX content for testing."""
    return b"fake docx content"

@pytest.fixture
def mock_txt_content():
    """Mock TXT content for testing."""
    return b"This is a test resume with more than 100 words. " * 75

@pytest.fixture
def expected_parsed_data():
    """Expected parsed data structure for testing."""
    return {
        'personal_info': {
            'name': {'value': 'John Doe', 'confidence': 0.8},
            'email': {'value': 'john.doe@email.com', 'confidence': 0.95},
            'phone': {'value': '(555) 123-4567', 'confidence': 0.9},
            'location': {'value': None, 'confidence': 0.0},
            'linkedin_url': {'value': 'linkedin.com/in/johndoe', 'confidence': 0.95},
            'github_url': {'value': 'github.com/johndoe', 'confidence': 0.95},
            'confidence': 0.76
        },
        'education': {
            'institutions': ['University of Technology'],
            'degrees': [],
            'fields_of_study': [],
            'dates': [],
            'gpa': {'value': 3.8, 'confidence': 0.9},
            'confidence': 0.8
        },
        'experience': {
            'companies': ['TechCorp Inc.', 'StartupXYZ'],
            'positions': ['Senior Software Engineer', 'Software Engineer'],
            'dates': [],
            'descriptions': [],
            'confidence': 0.7
        },
        'skills': {
            'technical_skills': ['Python', 'JavaScript', 'TypeScript', 'Java', 'SQL', 'React', 'Node.js', 'FastAPI', 'Flask', 'Django', 'PostgreSQL', 'MongoDB', 'Redis', 'AWS', 'Docker', 'Kubernetes', 'Git', 'GitHub Actions', 'Jenkins', 'Jira'],
            'soft_skills': ['Leadership', 'Communication', 'Problem Solving', 'Teamwork'],
            'categories': {
                'programming_languages': ['Python', 'JavaScript', 'TypeScript', 'Java', 'SQL'],
                'frameworks': ['React', 'Node.js', 'FastAPI', 'Flask', 'Django'],
                'databases': ['PostgreSQL', 'MongoDB', 'Redis'],
                'cloud_platforms': ['AWS', 'Docker', 'Kubernetes'],
                'tools': ['Git', 'GitHub Actions', 'Jenkins', 'Jira']
            },
            'confidence': 0.85
        },
        'metadata': {
            'total_words': 200,
            'parsing_timestamp': '2024-01-01T00:00:00',
            'confidence_overall': 0.78,
            'extraction_method': None,
            'encoding': None,
            'word_count': None,
            'extraction_errors': []
        }
    }

@pytest.fixture
def mock_extraction_metadata():
    """Mock extraction metadata for testing."""
    return {
        'file_type': 'txt',
        'file_size': 1000,
        'extraction_method': 'text-encoding-detection',
        'encoding': 'utf-8',
        'word_count': 300,
        'extraction_errors': []
    }

@pytest.fixture(autouse=True)
def mock_logger():
    """Mock logger to prevent logging during tests."""
    with patch('resume_parser.core.extractor.logger'), \
         patch('resume_parser.core.parser.logger'), \
         patch('resume_parser.api.routes.logger'), \
         patch('resume_parser.main.logger'):
        yield

@pytest.fixture
def mock_spacy_model():
    """Mock spaCy model for testing."""
    with patch('resume_parser.core.parser.spacy.load') as mock_load:
        mock_nlp = Mock()
        mock_doc = Mock()
        mock_doc.ents = []
        mock_doc.__len__ = Mock(return_value=200)
        mock_nlp.return_value = mock_doc
        mock_load.return_value = mock_nlp
        yield mock_nlp
