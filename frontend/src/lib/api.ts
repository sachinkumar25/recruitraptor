
// API Service Configuration
const SERVICE_URLS = {
    PARSER: '/api/parser',         // Proxies to http://localhost:8000
    DISCOVERY: '/api/discovery',   // Proxies to http://localhost:8001
    ENRICHMENT: '/api/enrichment', // Proxies to http://localhost:8002
    NARRATIVE: '/api/narrative',   // Proxies to http://localhost:8003
};

// Types based on backend models
export interface PersonalInfo {
    name: { value?: string; confidence: number };
    email: { value?: string; confidence: number };
    phone: { value?: string; confidence: number };
    location: { value?: string; confidence: number };
    linkedin_url: { value?: string; confidence: number };
    github_url: { value?: string; confidence: number };
}

export interface ExtractedResumeData {
    personal_info: PersonalInfo;
    education: any;
    experience: any;
    skills: any;
    metadata: any;
}

export interface GitHubProfile {
    profile: any;
    confidence: number;
    match_reasoning: string;
}

export interface LinkedInProfile {
    profile: any;
    confidence: number;
    match_reasoning: string;
}

export interface EnrichedCandidateProfile {
    candidate_id: string;
    personal_info: any;
    skills: any;
    experience: any;
    education: any;
    github_analysis: any;
    overall_confidence: number;
    enrichment_timestamp: string;
    job_relevance_score?: number;
}

// Narrative Engine Types
export interface BioNarrativeRequest {
    candidate_id: string;
    enriched_profile: {
        candidate_id: string;
        name: string;
        email?: string;
        location?: string;
        github_url?: string;
        technical_skills: any[];
        programming_languages: string[];
        frameworks: string[];
        experience_years?: number;
        github_analysis?: any;
        job_relevance_score?: number;
        skill_match_percentage?: number;
        skill_gaps: string[];
        skill_strengths: string[];
    };
    bio_style: 'professional' | 'casual' | 'technical';
    max_length?: number;
    llm_provider?: 'openai' | 'anthropic';
}

export interface BioNarrativeResponse {
    success: boolean;
    bio?: string;
    error_message?: string;
    processing_time_ms?: number;
}

export class RecruitRaptorApi {
    /**
     * Orchestrates the Resume Upload -> Parse -> Discover -> Enrich flow
     */
    static async uploadResume(file: File): Promise<EnrichedCandidateProfile> {
        try {
            // 1. Upload to Resume Parser
            console.log('Step 1: Parsing Resume...');
            const formData = new FormData();
            formData.append('file', file);

            const parseResponse = await fetch(`${SERVICE_URLS.PARSER}/api/v1/upload`, {
                method: 'POST',
                body: formData,
            });

            if (!parseResponse.ok) {
                throw new Error(`Parser Service failed: ${parseResponse.statusText}`);
            }

            const parseResult = await parseResponse.json();
            const parsedData = parseResult.parsed_data;

            // 2. Discover Profiles (GitHub/LinkedIn)
            console.log('Step 2: Discovering Profiles...');
            const discoveryResponse = await fetch(`${SERVICE_URLS.DISCOVERY}/api/v1/discover`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    candidate_data: parsedData,
                    discovery_options: {
                        search_github: true,
                        search_linkedin: true,
                        include_repository_analysis: true
                    }
                }),
            });

            if (!discoveryResponse.ok) {
                console.warn(`Discovery Service warning: ${discoveryResponse.statusText}. Proceeding with enrichment.`);
                // Note: We might want to continue even if discovery fails, but for now we'll throw or handle gracefully
            }

            const discoveryResult = discoveryResponse.ok ? await discoveryResponse.json() : { github_profiles: [], linkedin_profiles: [] };

            // 3. Enrich Data
            console.log('Step 3: Enriching Profile...');
            const enrichmentResponse = await fetch(`${SERVICE_URLS.ENRICHMENT}/api/v1/enrich`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    resume_data: parsedData,
                    github_profiles: discoveryResult.github_profiles || [],
                    linkedin_profiles: discoveryResult.linkedin_profiles || [],
                    job_context: {
                        required_skills: ["Python", "React", "TypeScript"], // Default context for now
                        preferred_skills: ["AWS", "Docker", "Kubernetes"]
                    }
                }),
            });

            if (!enrichmentResponse.ok) {
                throw new Error(`Enrichment Service failed: ${enrichmentResponse.statusText}`);
            }

            const enrichmentResult = await enrichmentResponse.json();

            if (!enrichmentResult.success || !enrichmentResult.enriched_profile) {
                throw new Error(`Enrichment failed: ${enrichmentResult.error_message || 'Unknown error'}`);
            }

            return enrichmentResult.enriched_profile;

        } catch (error) {
            console.error('Orchestration failed:', error);
            throw error;
        }
    }

    /**
     * Get all candidates from Data Enrichment Service
     */
    static async getCandidates(): Promise<EnrichedCandidateProfile[]> {
        const response = await fetch(`${SERVICE_URLS.ENRICHMENT}/api/v1/profiles`);
        if (!response.ok) {
            throw new Error(`Failed to fetch candidates: ${response.statusText}`);
        }
        return response.json();
    }

    /**
     * Get specific candidate by ID
     */
    static async getCandidate(id: string): Promise<EnrichedCandidateProfile> {
        const response = await fetch(`${SERVICE_URLS.ENRICHMENT}/api/v1/profiles/${id}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch candidate ${id}: ${response.statusText}`);
        }
        return response.json();
    }

    /**
     * Generate AI-powered bio narrative for a candidate
     */
    static async generateBioNarrative(
        candidate: EnrichedCandidateProfile,
        style: 'professional' | 'casual' | 'technical' = 'professional',
        maxLength: number = 300
    ): Promise<BioNarrativeResponse> {
        try {
            // Transform EnrichedCandidateProfile to the format expected by narrative engine
            const enrichedProfile = {
                candidate_id: candidate.candidate_id,
                name: candidate.personal_info?.name || 'Unknown',
                email: candidate.personal_info?.email,
                location: candidate.personal_info?.location,
                github_url: candidate.personal_info?.github_url,
                technical_skills: candidate.skills?.technical_skills || [],
                programming_languages: candidate.github_analysis?.languages_distribution
                    ? Object.keys(candidate.github_analysis.languages_distribution)
                    : [],
                frameworks: candidate.skills?.technical_skills
                    ?.filter((s: any) => s.category === 'framework')
                    ?.map((s: any) => s.name) || [],
                experience_years: candidate.experience?.total_years,
                github_analysis: candidate.github_analysis,
                job_relevance_score: candidate.job_relevance_score,
                skill_match_percentage: candidate.skills?.skill_match_percentage,
                skill_gaps: candidate.skills?.skill_gaps || [],
                skill_strengths: candidate.skills?.technical_skills
                    ?.filter((s: any) => s.confidence > 0.8)
                    ?.map((s: any) => s.name) || [],
            };

            const response = await fetch(`${SERVICE_URLS.NARRATIVE}/api/v1/bio`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    candidate_id: candidate.candidate_id,
                    enriched_profile: enrichedProfile,
                    bio_style: style,
                    max_length: maxLength,
                }),
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Narrative Service failed: ${response.statusText} - ${errorText}`);
            }

            return response.json();
        } catch (error) {
            console.error('Bio narrative generation failed:', error);
            return {
                success: false,
                error_message: error instanceof Error ? error.message : 'Unknown error',
            };
        }
    }

    /**
     * Check Narrative Engine health status
     */
    static async checkNarrativeHealth(): Promise<boolean> {
        try {
            const response = await fetch(`${SERVICE_URLS.NARRATIVE}/api/v1/health`);
            if (!response.ok) return false;
            const data = await response.json();
            return data.status === 'healthy' || data.status === 'degraded';
        } catch {
            return false;
        }
    }
}
