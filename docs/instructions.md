# AI Recruiter Agent - Product Requirements Document (PRD)

## 1. Document Overview / Introduction

### Purpose
This Product Requirements Document (PRD) serves as the comprehensive specification and implementation guide for an AI-powered recruiter agent system. The document provides detailed technical requirements, architectural guidance, and implementation roadmap specifically designed for AI-assisted development using tools like Cursor and Windsurf.

### Audience
- **Primary**: Development team implementing the system using AI coding assistants
- **Secondary**: Product stakeholders and future development team members
- **Technical Level**: Intermediate to advanced developers familiar with Python, FastAPI, Docker, and AI/LLM integration

### High-Level Vision
Transform the manual, time-intensive candidate evaluation process into an intelligent, automated workflow that delivers comprehensive candidate assessments in seconds rather than hours. The system will serve as a force multiplier for technical recruiters, enabling them to focus on high-value relationship building and strategic hiring decisions while the AI handles the research-intensive evaluation process.

**Core Value Proposition**: 
- Reduce candidate screening time from 20+ minutes to under 30 seconds
- Increase evaluation consistency and depth across all candidates
- Provide actionable insights that improve hiring manager decision-making quality
- Scale recruitment capacity without proportional increase in human resources

### Document Scope and Structure
This PRD covers the complete system from initial architecture through production deployment, with particular emphasis on:
- Microservices architecture optimized for AI-assisted development
- Detailed functional specifications with API contracts
- Comprehensive non-functional requirements for production readiness
- Implementation timeline and success criteria for MVP delivery

---

## 2. Problem Statement & Objectives

### Current State Analysis

**Manual Resume Screening Inefficiencies**
- **Time Investment**: Recruiters spend 6-8 minutes per resume for initial screening, processing only 30-40 candidates per day
- **Inconsistent Evaluation**: Different recruiters apply varying criteria, leading to qualified candidates being overlooked
- **Limited Technical Context**: Non-technical recruiters struggle to assess coding skills and project complexity accurately
- **Format Dependency**: Resume parsing quality varies dramatically based on formatting, leading to missed information

**Profile Discovery and Research Bottlenecks**
- **Manual Search Process**: 15-20 minutes per candidate to discover and validate GitHub, LinkedIn, and portfolio links
- **Incomplete Data Collection**: Time constraints lead to abbreviated research, missing key candidate strengths
- **No Standardized Process**: Research depth and quality varies by recruiter workload and experience level
- **Tool Fragmentation**: Multiple platforms and manual processes create workflow inefficiencies

**Assessment Quality and Consistency Issues**
- **Subjective Skill Evaluation**: Heavy reliance on recruiter's technical interpretation capabilities
- **Limited Job Relevance**: Difficulty connecting candidate experience to specific role requirements
- **Inconsistent Narrative Quality**: Candidate presentations to hiring managers vary significantly in depth and relevance
- **No Confidence Indicators**: No systematic way to communicate data reliability and assessment certainty

### Primary Objectives

**Efficiency and Speed Objectives**
- **Resume Processing**: Reduce initial resume screening from 6-8 minutes to under 30 seconds with 95%+ accuracy
- **Profile Discovery**: Automate profile discovery process, eliminating 15-20 minutes of manual research per candidate
- **End-to-End Processing**: Complete candidate evaluation pipeline from upload to final report in under 5 seconds
- **Throughput Increase**: Enable single recruiter to process 200+ candidates per day versus current 30-40

**Quality and Consistency Objectives**
- **Data Extraction Accuracy**: Achieve ≥95% accuracy in resume field extraction across diverse format types
- **Profile Discovery Success**: Maintain ≥85% success rate in discovering candidate's primary professional profiles
- **Assessment Standardization**: Deliver consistent, structured evaluations with repeatable quality metrics
- **Confidence Scoring**: Provide reliability indicators for all extracted data and generated assessments

**Business Impact Objectives**
- **Hiring Manager Satisfaction**: Improve candidate presentation quality leading to faster hiring decisions
- **Recruiter Productivity**: Triple candidate processing capacity without additional headcount
- **Quality Hire Rate**: Increase successful hire rate through more comprehensive candidate evaluation
- **Time-to-Fill Reduction**: Reduce overall hiring timeline through faster initial screening and better candidate matching

---

## 3. Scope

### In-Scope for MVP Release (Version 1.0)

**Core Processing Pipeline**
- **Resume Parsing Engine**: Support for PDF, DOCX, and TXT formats up to 5MB with intelligent field extraction
- **Profile Discovery System**: Automated GitHub and LinkedIn profile identification using search APIs
- **Data Enrichment Service**: GitHub repository analysis and LinkedIn profile data extraction
- **AI Narrative Generation**: LLM-powered candidate assessment creation tailored to job requirements
- **Confidence Scoring**: Reliability indicators for all extracted and generated data

**User Interface and Experience**
- **Web-Based Dashboard**: Responsive interface optimized for desktop and tablet usage
- **File Upload System**: Drag-and-drop interface with real-time processing feedback
- **Results Presentation**: Three-panel layout for resume data, narrative, and profile information
- **Manual Override Capabilities**: Edit and correct automatically extracted information
- **Export Functionality**: PDF and JSON export for candidate reports

**Infrastructure and Deployment**
- **Containerized Architecture**: Docker-based microservices with Docker Compose orchestration
- **Local Development Environment**: Complete setup for development and testing
- **Basic Monitoring**: Health checks, logging, and error tracking for system reliability
- **Simple Authentication**: API key-based protection for endpoint security

### Out-of-Scope for MVP Release

**Advanced Enterprise Features**
- **ATS Integration**: Direct integration with Applicant Tracking Systems (Greenhouse, Lever, Workday)
- **Enterprise Authentication**: SSO, SAML, Active Directory integration for organizational access control
- **Multi-Tenant Architecture**: Separate organizational instances with data isolation
- **Advanced Role Management**: Granular permissions and access control for different user types

**Mobile and Advanced UI**
- **Native Mobile Applications**: iOS and Android apps for mobile candidate evaluation
- **Advanced Analytics Dashboard**: Recruitment metrics, pipeline analysis, and performance tracking
- **Real-Time Collaboration**: Multiple recruiters working on same candidate simultaneously
- **Custom Branding**: White-label capabilities and organizational theming

---

## 4. Stakeholders & Roles

### Primary Stakeholder: Product Owner & Lead Developer

**Role Definition**: Single individual responsible for product vision, technical implementation, and delivery success

**Core Responsibilities**:
- **Product Strategy**: Define feature priorities, user experience requirements, and success criteria
- **Technical Leadership**: Make architectural decisions, technology choices, and implementation approaches
- **Quality Assurance**: Ensure system meets functional and non-functional requirements through testing and validation
- **User Advocacy**: Represent end-user needs and validate solutions against real recruiting workflows
- **Project Management**: Manage timeline, scope, and delivery milestones for MVP and subsequent releases

---

## 5. User Personas & Use Cases

### Primary Persona: Technical Recruiter (Sarah Chen)

**Background and Experience**
- **Role**: Senior Technical Recruiter at mid-stage technology company (100-500 employees)
- **Experience**: 4 years in technical recruiting, primarily software engineering and data science roles
- **Education**: Business degree with post-graduation recruiting certification
- **Current Tools**: LinkedIn Recruiter, Greenhouse ATS, manual GitHub profile reviews

**Pain Points and Frustrations**
- **Research Time**: Spends too much time on manual profile discovery and validation
- **Technical Translation**: Difficulty explaining technical skills and project relevance to non-technical stakeholders
- **Consistency**: Evaluation quality varies based on time pressure and candidate complexity
- **Tool Switching**: Constant context switching between multiple platforms and manual processes

### Core User Workflows

#### Workflow 1: Resume Upload and Initial Processing
**Frequency**: 25-35 times per day
**Target Time**: 30 seconds

**Steps**:
1. Receive resume via email, ATS, or direct submission
2. Navigate to AI recruiter agent dashboard
3. Drag resume file to upload area or use file browser
4. Monitor real-time processing status with progress indicators
5. Review automatically extracted personal information, education, experience, and skills
6. Correct any misidentified or missing information using inline editing

#### Workflow 2: Automated Profile Discovery and Validation
**Frequency**: 25-35 times per day
**Target Time**: 1-2 minutes (mostly automated)

**Steps**:
1. System automatically searches for GitHub and LinkedIn profiles
2. Review discovered profile links with confidence scores
3. Validate profile authenticity using cross-reference data
4. Add any missed profiles discovered through manual search
5. Initiate data enrichment process for validated profiles

#### Workflow 3: Comprehensive Assessment Generation and Review
**Frequency**: 25-35 times per day
**Target Time**: 2-3 minutes

**Steps**:
1. System analyzes GitHub repositories and LinkedIn data
2. LLM generates structured assessment and executive summary
3. Review generated narrative for accuracy and relevance
4. Edit sections requiring additional context or correction
5. Export final candidate report for hiring manager distribution

---

## 6. Functional Requirements

### 6.1 Resume Parser Service

#### 6.1.1 File Upload and Format Processing

**Requirement ID**: FR-001
**Priority**: Critical (P0)
**Component**: Resume Parser Service
**Feature**: Multi-format resume file processing with comprehensive validation

**Acceptance Criteria**:

**AC-001.1: PDF File Processing**
- Accept PDF files from version 1.4 through latest (2.0)
- Handle password-protected PDFs with appropriate error messaging
- Extract text content while preserving basic structure and formatting context
- Support embedded fonts and unicode character sets
- Maximum file size: 5MB with clear error messaging for oversized files
- Minimum content requirement: 100 words of extractable text

**AC-001.2: DOCX File Processing**
- Support Microsoft Word 2007+ format (.docx) with full compatibility
- Preserve table structure, bullet points, and basic formatting during text extraction
- Handle embedded objects (images, charts) gracefully without processing errors
- Extract header and footer content when relevant to candidate information
- Support documents with multiple sections, columns, and complex layouts

**AC-001.3: TXT File Processing**
- Auto-detect character encoding (UTF-8, Latin-1, CP1252, ASCII)
- Handle various line ending formats (Unix, Windows, Mac)
- Process structured text with section headers and bullet points
- Support international characters and accented letters
- Maximum file size: 1MB for plain text files

**API Specification**:
```python
# POST /api/v1/resume/upload
# Content-Type: multipart/form-data

class FileUploadRequest:
    file: UploadFile  # Required - Resume file
    job_title: Optional[str]  # Optional - Target position context
    company: Optional[str]  # Optional - Hiring company context

class FileUploadResponse:
    success: bool
    file_id: str  # Unique identifier for tracking
    metadata: FileMetadata
    processing_status: ProcessingStatus
    error_details: Optional[ErrorDetails]
```

#### 6.1.2 Advanced Field Extraction and Structuring

**Requirement ID**: FR-002
**Priority**: Critical (P0)
**Component**: Resume Parser Service
**Feature**: Intelligent resume field extraction with confidence scoring and validation

**Acceptance Criteria**:

**AC-002.1: Personal Information Extraction**
- Extract full names from resume headers, footers, or document metadata
- Handle various name formats: "First Last", "Last, First", "First Middle Last"
- Detect and preserve name prefixes (Dr., Prof.) and suffixes (Jr., Sr., PhD)
- Extract and validate email addresses, phone numbers, and locations
- Support international phone number formats with country code detection
- Detect and extract LinkedIn, GitHub, and personal website URLs

**AC-002.2: Education History Extraction**
- Recognize universities, colleges, and educational institutions
- Handle institution name variations and abbreviations
- Parse degree types, majors, and academic specializations
- Support various degree formats (B.S., Bachelor of Science, BS Computer Science)
- Extract graduation dates, expected graduation, and date ranges
- Extract GPA, honors, and academic achievements

**AC-002.3: Professional Experience Extraction**
- Extract employer names and job titles with company name variations
- Identify job title variations and normalize common positions
- Extract employment dates with support for "Present", "Current", and ongoing positions
- Parse job responsibilities and achievements from bullet points
- Detect quantified accomplishments (numbers, percentages, metrics)
- Calculate employment duration and identify career gaps

**AC-002.4: Skills and Technology Extraction**
- Extract programming languages, frameworks, and tools
- Maintain comprehensive technology taxonomy with synonyms and variations
- Categorize skills by domain (programming languages, frameworks, databases, cloud platforms)
- Detect skill proficiency indicators (years, certification levels, project usage)
- Extract soft skills from experience descriptions and dedicated sections
- Identify professional certifications and completed training

**Data Schema**:
```python
class ExtractedResumeData:
    personal_info: PersonalInfo
    education: List[EducationEntry]
    experience: List[ExperienceEntry]
    skills: List[SkillEntry]
    certifications: List[CertificationEntry]
    raw_text: str
    file_type: FileType
    overall_confidence: float  # 0.0-1.0
    processing_time_ms: int

class PersonalInfo:
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    linkedin_url: Optional[str]
    github_url: Optional[str]
    website: Optional[str]
    confidence_scores: Dict[str, float]

class EducationEntry:
    institution: str
    degree: Optional[str]
    field_of_study: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    gpa: Optional[str]
    honors: List[str]
    confidence: float

class ExperienceEntry:
    company: str
    position: str
    start_date: Optional[str]
    end_date: Optional[str]
    location: Optional[str]
    description: Optional[str]
    is_current: bool
    achievements: List[str]
    technologies_used: List[str]
    confidence: float

class SkillEntry:
    name: str
    category: str  # "programming", "framework", "database", "cloud", "soft_skill"
    proficiency_level: Optional[str]  # "beginner", "intermediate", "advanced", "expert"
    years_experience: Optional[int]
    evidence_source: str  # "skills_section", "experience", "projects"
    confidence: float
```

### 6.2 Profile Discovery Service

#### 6.2.1 GitHub Profile Discovery and Analysis

**Requirement ID**: FR-003
**Priority**: High (P1)
**Component**: Profile Discovery Service
**Feature**: Automated GitHub profile identification, validation, and repository analysis

**Acceptance Criteria**:

**AC-003.1: Multi-Strategy Profile Search**
- **Email-Based Discovery**: Primary search method using candidate email address
- **Name and Context Search**: Secondary search using name combined with contextual information
- **Fuzzy Matching**: Handle name variations and edge cases with different name orderings

**AC-003.2: Profile Validation and Confidence Scoring**
- Cross-reference validation using available data points (bio, location, company information)
- Validate based on repository content relevance to stated experience
- Check profile creation date against career timeline consistency

**AC-003.3: Repository Analysis and Insights**
- Extract comprehensive repository information (stars, forks, creation date, last update)
- Identify and categorize technologies used across repositories
- Programming language distribution analysis
- Framework and library usage detection through dependency analysis

**API Specification**:
```python
# POST /api/v1/profiles/discover/github

class GitHubDiscoveryRequest:
    candidate_data: CandidateSearchData
    search_options: GitHubSearchOptions

class GitHubDiscoveryResponse:
    success: bool
    profiles_found: List[GitHubProfileMatch]
    search_metadata: SearchMetadata
    processing_time_ms: int

class GitHubProfileMatch:
    username: str
    profile_url: str
    confidence_score: float
    match_reasoning: str
    profile_data: GitHubProfileData
    repository_analysis: RepositoryAnalysis
```

#### 6.2.2 LinkedIn Profile Discovery and Data Extraction

**Requirement ID**: FR-004
**Priority**: High (P1)
**Component**: Profile Discovery Service
**Feature**: LinkedIn profile search and basic information extraction

**Acceptance Criteria**:

**AC-004.1: Search Engine-Based Profile Discovery**
- Multi-parameter search strategy using various search combinations
- Search result processing and validation with LinkedIn domain filtering
- Result validation with profile accessibility and relevance checks

**AC-004.2: Profile Data Extraction**
- Extract basic profile information (name, headline, location, summary)
- Extract work experience information with employment date ranges
- Extract education information with institutions and degrees

**AC-004.3: Respectful Data Collection**
- Implement responsible scraping practices with rate limiting
- Use appropriate identification for web requests with descriptive user agent
- Graceful handling of various failure scenarios

### 6.3 Data Enrichment Service

#### 6.3.1 Comprehensive Data Integration and Analysis

**Requirement ID**: FR-005
**Priority**: High (P1)
**Component**: Data Enrichment Service
**Feature**: Multi-source data integration with intelligent analysis and skill assessment

**Acceptance Criteria**:

**AC-005.1: Data Integration and Normalization**
- Intelligently combine information from multiple sources (resume, GitHub, LinkedIn)
- Resolve conflicts between resume data and profile information
- Merge duplicate skills and experiences with confidence weighting
- Normalize date formats and standardize company/institution names

**AC-005.2: Advanced Skill Analysis and Proficiency Assessment**
- Calculate skill levels based on evidence from years of experience and project complexity
- Analyze programming language distribution across all repositories
- Evaluate project complexity and technical challenges solved
- Weight recent usage more heavily than historical experience

**AC-005.3: Experience Relevance Analysis**
- Match experience descriptions to job requirements
- Evaluate skill alignment and technology overlap
- Assess career progression and leadership experience
- Consider industry and domain expertise relevance

### 6.4 Narrative Generation Service

#### 6.4.1 LLM-Powered Assessment Creation

**Requirement ID**: FR-006
**Priority**: Critical (P0)
**Component**: Narrative Generation Service
**Feature**: Intelligent candidate narrative generation with job-specific customization

**Acceptance Criteria**:

**AC-006.1: Structured Narrative Generation**
- Generate comprehensive assessments with distinct sections:
  - **Executive Summary**: 2-3 sentence overview highlighting key strengths and fit
  - **Technical Skills Assessment**: Detailed analysis of technical capabilities with evidence
  - **Experience Relevance**: Connection between candidate background and job requirements
  - **Project Portfolio Analysis**: Evaluation of technical projects and their significance
  - **Growth Potential**: Assessment of learning trajectory and development opportunities

**AC-006.2: Context-Aware Content Generation**
- Prioritize skills and experiences most relevant to the target role
- Address required qualifications explicitly with supporting evidence
- Highlight transferable skills when direct experience is limited
- Connect candidate background to company/industry-specific needs

**AC-006.3: Multiple Narrative Styles and Audiences**
- **Executive Style**: High-level overview focusing on business impact and leadership
- **Technical Style**: Detailed technical analysis for engineering managers
- **Comprehensive Style**: Balanced assessment covering all aspects thoroughly
- **Concise Style**: Brief summary for initial screening and rapid review

**API Specification**:
```python
# POST /api/v1/narrative/generate

class NarrativeGenerationRequest:
    candidate_profile: EnrichedCandidateProfile
    job_context: JobContext
    narrative_preferences: NarrativePreferences

class NarrativeGenerationResponse:
    success: bool
    narrative: CandidateNarrative
    generation_metadata: GenerationMetadata
    quality_report: QualityReport
    processing_time_ms: int

class CandidateNarrative:
    executive_summary: NarrativeSection
    technical_assessment: NarrativeSection
    experience_analysis: NarrativeSection
    project_portfolio: NarrativeSection
    growth_potential: NarrativeSection
    overall_recommendation: RecommendationSection
```

### 6.5 User Interface and Dashboard

#### 6.5.1 Resume Upload and Processing Interface

**Requirement ID**: FR-008
**Priority**: High (P1)
**Component**: Frontend Application
**Feature**: Intuitive file upload with real-time processing feedback

**Acceptance Criteria**:

**AC-008.1: File Upload Interface Design**
- Large, visually prominent drop zone with clear instructions
- Visual feedback during drag operations (hover state, highlight border)
- Support for clicking to open file browser as alternative method
- Real-time file format validation with clear error messaging

**AC-008.2: Real-Time Processing Feedback**
- Detailed progress indicators for multi-stage processing
- WebSocket connection for live updates without page refresh
- Estimated completion time based on file size and processing queue
- Error handling with retry options and detailed error explanations

#### 6.5.2 Data Review and Editing Interface

**Requirement ID**: FR-009
**Priority**: High (P1)
**Component**: Frontend Application
**Feature**: Comprehensive data review and manual correction capabilities

**Acceptance Criteria**:

**AC-009.1: Extracted Data Display and Editing**
- Organized presentation of extracted resume fields with collapsible sections
- Inline editing with click-to-edit functionality for immediate corrections
- Auto-save functionality with visual confirmation of saved changes
- Confidence indicators with visual representation of extraction confidence

#### 6.5.3 Results Dashboard and Report Viewing

**Requirement ID**: FR-010
**Priority**: Critical (P0)
**Component**: Frontend Application
**Feature**: Comprehensive results presentation with interactive elements

**Acceptance Criteria**:

**AC-010.1: Three-Panel Dashboard Layout**
- **Left Panel (30% width)**: Resume data with personal information, education, experience, and skills
- **Center Panel (45% width)**: Generated narrative with executive summary and assessment sections
- **Right Panel (25% width)**: Profile discovery with GitHub and LinkedIn information

**AC-010.2: Interactive Assessment Controls**
- Regeneration interface with dynamic content regeneration and customization
- Feedback collection with thumbs up/down rating and detailed feedback options
- Export functionality with multiple format options (PDF, JSON, email sharing)

---

## 7. Non-Functional Requirements

### 7.1 Performance Requirements

#### 7.1.1 Response Time and Latency Standards

**Requirement ID**: NFR-001
**Priority**: Critical (P0)
**Category**: Performance - User Experience

**Performance Targets**:
- **File Upload and Processing**: Complete upload for files up to 5MB within 10 seconds
- **Resume Text Extraction**: Process PDF/DOCX files and extract text within 2 seconds
- **Field Parsing and Extraction**: Complete resume field parsing within 3 seconds
- **GitHub Profile Discovery**: Complete profile search and validation within 4 seconds
- **LinkedIn Profile Search**: Complete search engine queries and basic extraction within 3 seconds
- **LLM Narrative Generation**: Generate complete candidate assessment within 8 seconds
- **End-to-End Processing**: Complete pipeline from upload to final report in 35-45 seconds

#### 7.1.2 Throughput and Concurrency Standards

**Requirement ID**: NFR-002
**Priority**: High (P1)
**Category**: Performance - Scalability

**Concurrency Targets**:
- **Simultaneous Resume Processing**: Handle 10 concurrent resume uploads without queue delays
- **API Request Handling**: Support 50 requests per second across all endpoints during peak usage
- **Database Connections**: Maintain connection pool of 20 connections with sub-100ms query performance
- **External API Coordination**: Manage 25 concurrent external API calls with proper rate limiting

### 7.2 Reliability and Availability

#### 7.2.1 System Uptime and Fault Tolerance

**Requirement ID**: NFR-003
**Priority**: High (P1)
**Category**: Reliability - Service Availability

**Availability Targets**:
- **Service Uptime**: 99.0% availability during business hours (Monday-Friday, 8 AM - 6 PM)
- **Recovery Time Objective (RTO)**: Restore service within 5 minutes of failure detection
- **Recovery Point Objective (RPO)**: Maximum 15 minutes of data loss in worst-case scenarios

**Fault Tolerance Strategies**:
- Retry logic with exponential backoff for transient failures
- Fallback mechanisms for external service unavailability
- Service isolation preventing cascade failures across microservices

### 7.3 Security and Data Protection

#### 7.3.1 Data Privacy and Protection

**Requirement ID**: NFR-005
**Priority**: Critical (P0)
**Category**: Security - Data Protection

**Data Protection Implementation**:
- **Encryption Standards**: AES-256 encryption for data at rest, TLS 1.3 for data in transit
- **Access Control**: Role-based permissions with principle of least privilege
- **Data Retention**: Automatic deletion of candidate data after 90 days unless explicitly retained
- **Audit Logging**: Complete audit trail for all data access and modification operations

#### 7.3.2 Application and Infrastructure Security

**Requirement ID**: NFR-006
**Priority**: High (P1)
**Category**: Security - System Protection

**Security Measures**:
- **API Authentication**: JWT-based authentication with configurable token expiration
- **Rate Limiting**: API rate limits per user/IP to prevent abuse
- **Input Validation**: Comprehensive input sanitization and validation for all user inputs
- **Infrastructure Security**: Container security, network isolation, and secrets management

---

## 8. UI/UX & Design Specifications

### 8.1 Design Philosophy and Visual Identity

**Design Principles**:
- **Professional Efficiency**: Clean, business-appropriate interface that accelerates recruiting workflows
- **Data-Driven Clarity**: Information hierarchy that highlights confidence levels and data quality
- **Intelligent Assistance**: UI that clearly communicates AI-generated content and allows easy human override
- **Scalable Interaction**: Design patterns that work for both novice and expert users

### 8.2 Core Interface Layouts

#### 8.2.1 Upload Screen Design

**Layout Structure**: Single-panel centered design with clear visual hierarchy

**Components**:
- **Primary Upload Zone**: Large drag-and-drop area with file icon and instructional text
- **File Selection Button**: Secondary upload method with file browser integration
- **Progress Indicator**: Multi-stage progress bar showing processing stages
- **Processing Status**: Real-time updates with estimated completion times

#### 8.2.2 Dashboard Layout Architecture

**Three-Panel Horizontal Layout** (optimized for 1440px+ displays):
- **Left Panel (30% width)**: Resume data with personal info, education, experience, skills
- **Center Panel (45% width)**: Generated narrative with executive summary and assessments
- **Right Panel (25% width)**: Profile discovery with GitHub and LinkedIn information

**Responsive Breakpoints**:
- **Desktop (1200px+)**: Three-panel horizontal layout
- **Tablet (768px-1199px)**: Two-panel stacked layout
- **Mobile (<768px)**: Single-column accordion layout

---

## 9. Data & Integration Requirements

### 9.1 Input Data Specifications

#### 9.1.1 Resume File Requirements

**Supported Formats**:
- **PDF Files**: Version 1.4+ compatibility, password protection detection, embedded text extraction
- **DOCX Files**: Microsoft Word 2007+ format, table and formatting preservation
- **TXT Files**: UTF-8, Latin-1, CP1252 encoding support, structured text recognition

**File Size and Content Limits**:
- **Maximum File Size**: 5MB per upload with compression optimization
- **Minimum Content**: 100 words minimum for processing viability
- **Content Types**: Text-based resumes only, image-only documents rejected

#### 9.1.2 External API Dependencies

**GitHub API Integration**:
- **Authentication**: Personal Access Token with user and repository read permissions
- **Rate Limits**: 5,000 requests per hour, graceful degradation with caching
- **Required Endpoints**: User search, repository listing, language statistics, commit history

**Search API Requirements**:
- **SerpAPI Integration**: Google Custom Search for LinkedIn profile discovery
- **Rate Limits**: 100 searches per month on free tier, upgrade path for higher volume
- **Search Parameters**: Name + company/education combinations for targeted results

**LLM Service Dependencies**:
- **OpenAI API**: GPT-4 or GPT-3.5-turbo for narrative generation
- **Alternative Providers**: Anthropic Claude, Google Gemini as fallback options
- **Token Management**: Efficient prompt engineering and response caching

### 9.2 Output Data Formats

#### 9.2.1 Structured Data Schemas

**Candidate Profile JSON Schema**:
```json
{
  "candidate_id": "string(uuid)",
  "processing_metadata": {
    "processed_at": "string(date-time)",
    "processing_time_ms": "integer",
    "confidence_score": "number(0-1)"
  },
  "resume_data": "object(ResumeData)",
  "github_profile": "object(GitHubProfile)",
  "linkedin_profile": "object(LinkedInProfile)",
  "generated_narrative": "object(NarrativeAssessment)"
}
```

#### 9.2.2 Export Format Specifications

**PDF Report Generation**:
- **Template Engine**: HTML-to-PDF conversion with CSS styling support
- **Layout**: Professional letterhead format with company branding placeholders
- **Content Sections**: Executive summary, technical assessment, experience analysis

**Integration-Ready Outputs**:
- **ATS JSON**: Standardized format for Applicant Tracking System integration
- **CSV Export**: Bulk data export for spreadsheet analysis and reporting

### 9.3 Caching and Data Storage Strategy

#### 9.3.1 Redis Caching Implementation

**Cache Categories and TTL**:
- **Profile Discovery Results**: 24-hour TTL for GitHub/LinkedIn search results
- **Repository Analysis Data**: 6-hour TTL for GitHub repository metadata
- **LLM Generated Content**: 1-hour TTL for narrative assessment caching
- **Session Data**: 30-minute TTL for user interface state persistence

#### 9.3.2 Database Storage Requirements

**PostgreSQL Schema Design**:
- **Candidates Table**: Core candidate information with full-text search capabilities
- **Processing_History Table**: Audit trail for all processing activities and results
- **User_Sessions Table**: Session management and user preference storage

**Data Retention Policies**:
- **Active Candidate Data**: 90-day automatic retention with extension options
- **Processing Logs**: 30-day retention for debugging and performance analysis
- **System Metrics**: 1-year retention for trend analysis and capacity planning

---

## 10. Assumptions & Constraints

### 10.1 Technical Assumptions

#### 10.1.1 Resume Format and Content Assumptions

**Document Structure Assumptions**:
- Resumes follow standard Western formatting conventions with clear section delineation
- Contact information appears in header or first section of document
- Experience and education sections use consistent date formatting
- Technical skills are explicitly listed rather than embedded only in experience descriptions

**Content Quality Assumptions**:
- Candidate names are provided in standard "First Last" or "First Middle Last" format
- Email addresses follow standard formatting and are currently active
- Company and institution names use standard spellings and recognizable formats

#### 10.1.2 External Service Availability Assumptions

**API Reliability Assumptions**:
- GitHub API maintains 99.9% uptime with predictable rate limiting
- SerpAPI provides consistent search result quality and format stability
- LinkedIn public profiles remain accessible through search engine indexing
- LLM service providers maintain stable API endpoints with consistent response formatting

### 10.2 Business and Operational Constraints

#### 10.2.1 Resource and Budget Constraints

**Infrastructure Limitations**:
- Development budget supports moderate AWS/GCP usage with cost monitoring
- External API costs limited to free tiers initially with upgrade path for production
- Processing power constrained to 4-core/8GB instances for service deployment

**Development Timeline Constraints**:
- MVP delivery timeline of 4 weeks requires focus on core functionality only
- Single developer implementation requiring AI-assisted development tools
- Limited manual testing resources necessitating automated testing emphasis

#### 10.2.2 Legal and Compliance Constraints

**Data Privacy Limitations**:
- Cannot store personal information without explicit consent and purpose limitation
- Must implement right-to-deletion capabilities for GDPR compliance consideration
- Limited to publicly available information processing to avoid privacy violations

**Service Usage Constraints**:
- LinkedIn scraping must respect robots.txt and terms of service limitations
- GitHub API usage must comply with acceptable use policies and rate limiting
- Cannot guarantee profile discovery success due to privacy settings and data availability

### 10.3 Scope and Feature Constraints

#### 10.3.1 MVP Feature Limitations

**Excluded Advanced Features**:
- Real-time collaboration features for multiple recruiters working on same candidate
- Advanced machine learning models for custom skill extraction and candidate ranking
- Integration with enterprise authentication systems (SSO, Active Directory)
- Mobile native applications and offline processing capabilities

**Simplified Implementation Choices**:
- Basic web scraping instead of authenticated API access for LinkedIn data
- Template-based report generation instead of fully customizable report builder
- Manual profile validation instead of automated confidence-based validation
- Single-tenant architecture instead of multi-tenant enterprise deployment

---

## 11. Dependencies

### 11.1 External Service Dependencies

#### 11.1.1 Critical External APIs

**GitHub API Dependency**:
- **Service**: GitHub REST API v4 and GraphQL API
- **Authentication**: Personal Access Token with appropriate scopes
- **Required Permissions**: Read access to public repositories, user profiles, and organization data
- **Rate Limits**: 5,000 requests per hour authenticated, 60 requests per hour unauthenticated
- **Backup Strategy**: Cache repository data with 24-hour TTL, graceful degradation to basic profile information

**Search API Dependency**:
- **Service**: SerpAPI for Google Custom Search integration
- **Authentication**: API key with sufficient monthly search quota
- **Required Quota**: Minimum 100 searches per month for development, 1000+ for production usage
- **Rate Limits**: 1 search per second, burst capability for multiple concurrent searches
- **Backup Strategy**: Fallback to direct Google search parsing or alternative search providers

**LLM Service Dependency**:
- **Service**: OpenAI GPT-4 API or compatible alternative (Anthropic Claude, Google Gemini)
- **Authentication**: API key with sufficient token quota and usage permissions
- **Required Quota**: Estimated 1000-2000 tokens per candidate assessment generation
- **Rate Limits**: Varies by provider, typically 10,000 requests per minute for paid accounts
- **Backup Strategy**: Multiple LLM provider support with automatic failover capabilities

#### 11.1.2 Infrastructure Service Dependencies

**Database Services**:
- **PostgreSQL**: Version 15+ for primary data storage with JSON support
- **Redis**: Version 7+ for caching and session management
- **MinIO or AWS S3**: Object storage for uploaded resume files and generated reports

**Development and Deployment Tools**:
- **Docker**: Container runtime for service deployment and local development
- **Docker Compose**: Local development orchestration and service coordination
- **GitHub Actions or GitLab CI**: Automated testing and deployment pipeline

### 11.2 Internal Service Dependencies

#### 11.2.1 Service Dependency Chain

**Primary Processing Pipeline**:
```
Resume Parser Service → Profile Discovery Service → Data Enrichment Service → Narrative Generation Service
```

**Service Communication Requirements**:
- **HTTP REST APIs**: Primary communication method between services
- **JSON Data Format**: Standardized data exchange format across all services
- **Health Check Endpoints**: Required for service discovery and load balancing
- **Error Handling**: Consistent error response format and status code usage

### 11.3 Development Environment Dependencies

#### 11.3.1 Development Tool Requirements

**Local Development Environment Specifications**:
```bash
# Required software versions for development environment
Development_Requirements:
  Core_Languages:
    - python: ">=3.11"
    - node: ">=18.0.0"
    - npm: ">=9.0.0"
  
  Package_Managers:
    - poetry: ">=1.6.0"  # Python dependency management
    - pnpm: ">=8.0.0"    # Node.js package management
  
  Development_Tools:
    - docker: ">=20.10.0"
    - docker-compose: ">=2.0.0"
    - git: ">=2.30.0"
  
  AI_Assisted_Development:
    - cursor: "latest stable version"
    - windsurf: "latest stable version" 
    - github_copilot: "optional but recommended"
  
  Code_Quality_Tools:
    - black: ">=23.0.0"      # Python formatting
    - isort: ">=5.12.0"      # Import sorting
    - flake8: ">=6.0.0"      # Python linting
    - mypy: ">=1.7.0"        # Type checking
    - prettier: ">=3.0.0"    # JavaScript/TypeScript formatting
    - eslint: ">=8.0.0"      # JavaScript linting
```

#### 11.3.2 Testing Framework and Quality Assurance Dependencies

**Testing Infrastructure Requirements**:
```python
TESTING_LIBRARIES = {
    'backend_testing': {
        'pytest': '>=7.4.0',           # Primary testing framework
        'pytest_asyncio': '>=0.21.0',  # Async test support
        'pytest_cov': '>=4.1.0',       # Coverage reporting
        'httpx': '>=0.25.0',            # HTTP client for API testing
        'factory_boy': '>=3.3.0',      # Test data generation
    },
    'integration_testing': {
        'testcontainers': '>=3.7.0',   # Docker containers for testing
        'requests_mock': '>=1.11.0',   # HTTP mocking
    }
}

QUALITY_GATES = {
    'code_coverage': {
        'backend_minimum': 80,  # Percent
        'integration_minimum': 60  # Percent
    }
}
```

---

## Implementation Timeline

### Week 1: Foundation
1. **Resume Parser Service** - Self-contained, no external dependencies
2. **Basic FastAPI setup** - Learn service communication patterns
3. **Docker setup** - Get comfortable with containerization

### Week 2: External Integrations  
4. **Profile Discovery Service** - Simple GitHub API + basic search
5. **Service-to-service communication** - Learn how services talk to each other

### Week 3: Data Processing
6. **Data Enrichment Service** - Combine and normalize data from different sources
7. **Database integration** - Store and retrieve candidate profiles

### Week 4: AI Integration & UI
8. **Narrative Generation Service** - LLM integration for final reports
9. **Frontend basics** - Simple UI to test the entire pipeline

---

## Success Metrics

### Technical KPIs
- **Parsing accuracy** ≥ 95% on test set of diverse resumes
- **Profile discovery success rate** ≥ 85% for GitHub and LinkedIn profiles
- **End-to-end processing time** < 45 seconds (median)
- **System uptime** ≥ 99% during business hours

### Business KPIs
- **Time savings** ≥ 90% reduction in manual candidate screening time
- **User satisfaction** ≥ 4.5/5 rating from recruiters
- **Assessment quality** ≥ 4/5 rating from hiring managers
- **Processing throughput** 200+ candidates per day per recruiter

### Quality Metrics
- **Data extraction confidence** ≥ 80% average across all fields
- **Narrative generation quality** ≥ 4/5 rating for relevance and accuracy
- **Error rate** < 1% for successful file uploads and processing
- **User adoption** 100% of target recruiters actively using system within 2 weeks