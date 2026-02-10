"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import {
    ChevronLeft,
    Mail,
    Linkedin,
    Github,
    MapPin,
    CheckCircle2,
    AlertTriangle,
    BrainCircuit,
    Code2,
    Calendar,
    Loader2,
    Sparkles,
    RefreshCw,
    ExternalLink,
    Star,
    GraduationCap,
    Tag,
    Briefcase,
    Target,
    Zap,
    ThumbsUp,
    ThumbsDown
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Separator } from "@/components/ui/separator";
import { JobProfile, JobService } from "@/lib/jobs";
import { RecruitRaptorApi, EnrichedCandidateProfile } from "@/lib/api";
import { MatchScoreRing } from "@/components/ui/MatchScoreRing";
import { SkillBadge } from "@/components/ui/SkillBadge";
import { cn } from "@/lib/utils";

export default function CandidateDetailPage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = use(params);
    const [candidate, setCandidate] = useState<EnrichedCandidateProfile | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Narrative generation state
    const [generatedNarrative, setGeneratedNarrative] = useState<string | null>(null);
    const [narrativeLoading, setNarrativeLoading] = useState(false);
    const [narrativeError, setNarrativeError] = useState<string | null>(null);
    const [selectedBioStyle, setSelectedBioStyle] = useState<'professional' | 'casual' | 'technical'>('professional');

    // JD Analysis state
    // JD Analysis state
    const [jdText, setJdText] = useState("");
    const [jdUrl, setJdUrl] = useState("");
    const [fetchingUrl, setFetchingUrl] = useState(false);
    const [analyzing, setAnalyzing] = useState(false);
    const [analysisError, setAnalysisError] = useState<string | null>(null);
    const [analysisResult, setAnalysisResult] = useState<any | null>(null);

    // Job Selector State
    const [activeJobs, setActiveJobs] = useState<JobProfile[]>([]);
    const [selectedJobId, setSelectedJobId] = useState<string>("");

    useEffect(() => {
        // Load active jobs
        setActiveJobs(JobService.getAll());
    }, []);

    const handleJobSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const jobId = e.target.value;
        setSelectedJobId(jobId);

        if (jobId) {
            const job = activeJobs.find(j => j.id === jobId);
            if (job) {
                setJdText(job.description);
            }
        }
    }; // Should be typed properly based on API response

    useEffect(() => {
        const fetchCandidate = async () => {
            try {
                const data = await RecruitRaptorApi.getCandidate(id);
                setCandidate(data);
                // If candidate already has a bio, use it
                if (data.personal_info?.bio) {
                    setGeneratedNarrative(data.personal_info.bio);
                }
            } catch (err) {
                console.error("Failed to fetch candidate:", err);
                setError(err instanceof Error ? err.message : "Failed to load candidate profile");
            } finally {
                setLoading(false);
            }
        };

        if (id) {
            fetchCandidate();
        }
    }, [id]);

    // Generate narrative handler
    const handleGenerateNarrative = async () => {
        if (!candidate) return;

        setNarrativeLoading(true);
        setNarrativeError(null);

        try {
            const response = await RecruitRaptorApi.generateBioNarrative(
                candidate,
                selectedBioStyle,
                300
            );

            if (response.success && response.bio) {
                setGeneratedNarrative(response.bio);
            } else {
                setNarrativeError(response.error_message || 'Failed to generate narrative');
            }
        } catch (err) {
            console.error("Failed to generate narrative:", err);
            setNarrativeError(err instanceof Error ? err.message : 'Failed to generate narrative');
        } finally {
            setNarrativeLoading(false);
        }
    };

    // Analyze Match Handler
    const handleAnalyzeMatch = async () => {
        if (!candidate || !jdText.trim()) return;

        setAnalyzing(true);
        setAnalysisError(null);
        setAnalysisResult(null);

        try {
            const response = await RecruitRaptorApi.analyzeJobMatch(candidate, jdText);

            if (response.success && response.narrative) {
                setAnalysisResult(response.narrative);
            } else {
                setAnalysisError(response.error_message || 'Failed to analyze match');
            }
        } catch (err) {
            console.error("Match analysis failed:", err);
            setAnalysisError(err instanceof Error ? err.message : 'Failed to analyze match');
        } finally {
            setAnalyzing(false);
        }
    };

    // Fetch JD from URL
    const handleFetchUrl = async () => {
        if (!jdUrl.trim()) return;
        setFetchingUrl(true);
        setAnalysisError(null);
        try {
            const result = await RecruitRaptorApi.fetchJobDescription(jdUrl);
            if (result.success && result.text) {
                setJdText(result.text);
                // Clear URL input after successful fetch
                setJdUrl("");
            } else {
                setAnalysisError(result.error || "Failed to fetch content");
            }
        } catch (error) {
            setAnalysisError("Failed to fetch content from URL");
        } finally {
            setFetchingUrl(false);
        }
    };

    if (loading) {
        return (
            <div className="flex h-[50vh] flex-col items-center justify-center gap-4 animate-fade-in">
                <div className="relative">
                    <div className="h-16 w-16 rounded-full bg-gradient-to-br from-indigo-500/20 to-purple-500/20 animate-pulse" />
                    <Loader2 className="h-8 w-8 animate-spin text-indigo-600 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
                </div>
                <span className="text-muted-foreground">Loading candidate profile...</span>
            </div>
        );
    }

    if (error || !candidate) {
        return (
            <div className="flex h-[50vh] flex-col items-center justify-center space-y-4 animate-fade-in">
                <div className="h-16 w-16 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                    <AlertTriangle className="h-8 w-8 text-red-600 dark:text-red-400" />
                </div>
                <h2 className="text-xl font-semibold">Error Loading Profile</h2>
                <p className="text-muted-foreground">{error || "Candidate not found"}</p>
                <Button variant="outline" onClick={() => window.location.reload()}>
                    Try Again
                </Button>
            </div>
        );
    }

    // Helper to process skills
    const verifiedSkills = candidate.skills.technical_skills
        .filter((s: any) => s.evidence_sources && s.evidence_sources.includes("github"))
        .map((s: any) => ({
            name: s.skill_name,
            source: 'github' as const,
            confidence: (s.confidence_score || 0) * 100,
            years: s.years_of_experience
        }));

    const claimedSkills = candidate.skills.technical_skills
        .filter((s: any) => !s.evidence_sources || !s.evidence_sources.includes("github"))
        .map((s: any) => ({
            name: s.skill_name,
            source: 'resume' as const,
            confidence: (s.confidence_score || 0) * 100
        }));

    // Helper to process experience (assuming arrays are aligned by index)
    const experienceList = candidate.experience.companies.map((company: string, index: number) => ({
        company,
        role: candidate.experience.positions[index] || "Role",
        dates: candidate.experience.dates[index] || "Dates unknown",
        description: candidate.experience.descriptions[index] || "",
        technologies: candidate.experience.technologies_used[company] || []
    }));

    // Helper to process education
    const educationList = candidate.education?.institutions?.map((inst: string, index: number) => ({
        institution: inst,
        degree: candidate.education.degrees?.[index] || "Degree",
        field: candidate.education.fields_of_study?.[index] || "",
        dates: candidate.education.dates?.[index] || "Dates unknown",
    })) || [];

    const matchScore = Math.round((candidate.job_relevance_score || 0) * 100);

    return (
        <div className="space-y-6 max-w-5xl mx-auto animate-fade-in">
            {/* Back Button */}
            <Link
                href="/candidates"
                className="inline-flex items-center gap-1.5 text-muted-foreground hover:text-foreground transition-colors group"
            >
                <ChevronLeft className="h-4 w-4 group-hover:-translate-x-0.5 transition-transform" />
                <span>Back to Candidates</span>
            </Link>

            {/* Premium Header Profile Card */}
            <div className="relative overflow-hidden rounded-2xl border border-slate-800 bg-slate-950 shadow-2xl">
                {/* Gradient Background - Reduced height */}
                <div className="absolute inset-0 h-32 bg-gradient-to-r from-indigo-900 via-purple-900 to-slate-900 opacity-90" />
                <div className="absolute inset-0 h-24 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIj48cGF0aCBkPSJNMzYgMzRjMC0yIDItNCAyLTRzMiAyIDIgNC0yIDQtMiA0LTItMi0yLTQiLz48L2c+PC9nPjwvc3ZnPg==')] opacity-30" />

                <div className="relative px-6 pb-6 pt-12">
                    <div className="flex flex-col items-center text-center gap-6">
                        {/* Profile Avatar - Centered */}
                        <div className="relative shrink-0">
                            <div className="h-32 w-32 rounded-full bg-gradient-to-br from-indigo-600 to-purple-700 flex items-center justify-center text-5xl font-bold text-white shadow-xl ring-4 ring-slate-900 mt-2">
                                {candidate.personal_info.name.split(' ').map((n: string) => n[0]).join('').slice(0, 2)}
                            </div>
                        </div>

                        {/* Profile Info - Centered */}
                        <div className="flex-1 pt-2 space-y-4 w-full">
                            <div className="flex flex-col items-center gap-4">
                                <div>
                                    <h1 className="text-4xl font-bold text-white tracking-tight mb-2">{candidate.personal_info.name}</h1>
                                    {(candidate.personal_info.linkedin_username || candidate.personal_info.github_username) && (
                                        <div className="flex items-center justify-center gap-4 text-slate-300 text-sm font-medium">
                                            {candidate.personal_info.github_username && (
                                                <span className="flex items-center gap-1.5">
                                                    <Github className="h-4 w-4" />
                                                    @{candidate.personal_info.github_username}
                                                </span>
                                            )}
                                        </div>
                                    )}
                                </div>

                                {/* Match Score Ring - Centered */}
                                <div>
                                    <MatchScoreRing score={matchScore} size="lg" className="text-white" />
                                </div>
                            </div>

                            <div className="flex flex-wrap justify-center gap-3">
                                {candidate.personal_info.email && (
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        className="gap-2 bg-white/10 text-white border-white/10 hover:bg-white/20 hover:text-white backdrop-blur-md transition-all"
                                        asChild
                                    >
                                        <a href={`mailto:${candidate.personal_info.email}`}>
                                            <Mail className="h-4 w-4" />
                                            Email
                                        </a>
                                    </Button>
                                )}
                                {candidate.personal_info.linkedin_url && (
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        className="gap-2 bg-white/10 text-white border-white/10 hover:bg-white/20 hover:text-white backdrop-blur-md transition-all"
                                        asChild
                                    >
                                        <Link
                                            href={
                                                candidate.personal_info.linkedin_url.startsWith('http')
                                                    ? candidate.personal_info.linkedin_url
                                                    : candidate.personal_info.linkedin_url.includes('linkedin.com')
                                                        ? `https://${candidate.personal_info.linkedin_url}`
                                                        : `https://linkedin.com/in/${candidate.personal_info.linkedin_url.replace('@', '')}`
                                            }
                                            target="_blank"
                                            rel="noopener noreferrer"
                                        >
                                            <Linkedin className="h-4 w-4" />
                                            LinkedIn
                                        </Link>
                                    </Button>
                                )}
                                {candidate.personal_info.github_url && (
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        className="gap-2 bg-white/10 text-white border-white/10 hover:bg-white/20 hover:text-white backdrop-blur-md transition-all"
                                        asChild
                                    >
                                        <Link
                                            href={
                                                candidate.personal_info.github_url.startsWith('http')
                                                    ? candidate.personal_info.github_url
                                                    : candidate.personal_info.github_url.includes('github.com')
                                                        ? `https://${candidate.personal_info.github_url}`
                                                        : `https://github.com/${candidate.personal_info.github_url.replace('@', '')}`
                                            }
                                            target="_blank"
                                            rel="noopener noreferrer"
                                        >
                                            <Github className="h-4 w-4" />
                                            GitHub
                                        </Link>
                                    </Button>
                                )}
                            </div>

                            {/* Verification Badges & Contact */}
                            <div className="flex flex-wrap justify-center gap-3 text-sm pt-2">
                                {candidate.personal_info.location && (
                                    <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-800/50 border border-slate-700 text-slate-300">
                                        <MapPin className="h-3.5 w-3.5" />
                                        {candidate.personal_info.location}
                                    </div>
                                )}
                                {candidate.personal_info.github_url && (
                                    <Badge className="gap-1.5 bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
                                        <CheckCircle2 className="h-3.5 w-3.5" />
                                        GitHub Verified
                                    </Badge>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content Tabs - Pill Style */}
            <Tabs defaultValue="overview" className="w-full">
                <TabsList className="inline-flex h-12 items-center justify-center rounded-full bg-slate-200 dark:bg-slate-800 p-1 text-slate-500">
                    <TabsTrigger value="overview" className="rounded-full px-6 py-2.5 text-sm font-medium transition-all data-[state=active]:bg-slate-900 data-[state=active]:text-white data-[state=active]:shadow-md">Overview</TabsTrigger>
                    <TabsTrigger value="jd-match" className="rounded-full px-6 py-2.5 text-sm font-medium transition-all data-[state=active]:bg-slate-900 data-[state=active]:text-white data-[state=active]:shadow-md">JD Match</TabsTrigger>
                    <TabsTrigger value="experience" className="rounded-full px-6 py-2.5 text-sm font-medium transition-all data-[state=active]:bg-slate-900 data-[state=active]:text-white data-[state=active]:shadow-md">Experience</TabsTrigger>
                    <TabsTrigger value="skills" className="rounded-full px-6 py-2.5 text-sm font-medium transition-all data-[state=active]:bg-slate-900 data-[state=active]:text-white data-[state=active]:shadow-md">Skills</TabsTrigger>
                    <TabsTrigger value="raw" className="rounded-full px-6 py-2.5 text-sm font-medium transition-all data-[state=active]:bg-slate-900 data-[state=active]:text-white data-[state=active]:shadow-md">Raw Data</TabsTrigger>
                </TabsList>

                {/* OVERVIEW TAB */}
                <TabsContent value="overview" className="mt-6 space-y-6 animate-fade-in">
                    {/* AI Narrative Card with Gradient Border */}
                    <Card className="relative overflow-hidden border-0 shadow-card">
                        <CardHeader>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <BrainCircuit className="h-5 w-5 text-purple-600" />
                                    <CardTitle>AI Narrative Summary</CardTitle>
                                </div>
                                <div className="flex items-center gap-2">
                                    <select
                                        value={selectedBioStyle}
                                        onChange={(e) => setSelectedBioStyle(e.target.value as any)}
                                        className="text-sm border rounded-md px-2 py-1 bg-white"
                                        disabled={narrativeLoading}
                                    >
                                        <option value="professional">Professional</option>
                                        <option value="casual">Casual</option>
                                        <option value="technical">Technical</option>
                                    </select>
                                    <Button
                                        onClick={handleGenerateNarrative}
                                        disabled={narrativeLoading}
                                        size="sm"
                                        className="gap-2"
                                    >
                                        {narrativeLoading ? (
                                            <>
                                                <Loader2 className="h-4 w-4 animate-spin" />
                                                Generating...
                                            </>
                                        ) : generatedNarrative ? (
                                            <>
                                                <RefreshCw className="h-4 w-4" />
                                                Regenerate
                                            </>
                                        ) : (
                                            <>
                                                <Sparkles className="h-4 w-4" />
                                                Generate Narrative
                                            </>
                                        )}
                                    </Button>
                                </div>
                            </div>
                        </CardHeader>
                        <CardContent>
                            {narrativeError && (
                                <Alert variant="destructive" className="mb-4">
                                    <AlertTriangle className="h-4 w-4" />
                                    <AlertTitle>Error</AlertTitle>
                                    <AlertDescription>{narrativeError}</AlertDescription>
                                </Alert>
                            )}
                            {narrativeLoading ? (
                                <div className="flex items-center justify-center py-8">
                                    <Loader2 className="h-6 w-6 animate-spin text-purple-600 mr-2" />
                                    <span className="text-slate-500">Generating AI narrative...</span>
                                </div>
                            ) : generatedNarrative ? (
                                <p className="text-slate-700 leading-relaxed whitespace-pre-wrap">
                                    {generatedNarrative}
                                </p>
                            ) : (
                                <div className="text-center py-8 text-slate-500">
                                    <Sparkles className="h-8 w-8 mx-auto mb-2 text-purple-300" />
                                    <p>Click "Generate Narrative" to create an AI-powered bio summary.</p>
                                    <p className="text-sm mt-1">Powered by GPT-4 / Claude</p>
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    <div className="grid md:grid-cols-2 gap-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-base">GitHub Insights</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="flex justify-between items-center text-sm">
                                    <span className="text-slate-500">Public Repositories</span>
                                    <span className="font-medium">{candidate.github_analysis?.total_repositories || 0}</span>
                                </div>
                                <div className="flex justify-between items-center text-sm">
                                    <span className="text-slate-500">Total Stars</span>
                                    <span className="font-medium">{candidate.github_analysis?.total_stars || 0}</span>
                                </div>
                                <Separator />
                                <div>
                                    <span className="text-xs text-slate-500 mb-2 block">Top Languages</span>
                                    <div className="flex gap-2 flex-wrap">
                                        {candidate.github_analysis?.languages_distribution && Object.keys(candidate.github_analysis.languages_distribution).slice(0, 3).map(lang => (
                                            <Badge key={lang} variant="outline">{lang}</Badge>
                                        ))}
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        <Card className="border-red-100 bg-red-50/10">
                            <CardHeader>
                                <CardTitle className="text-base text-red-900 flex items-center gap-2">
                                    <AlertTriangle className="h-4 w-4" />
                                    Flagged Items
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                {candidate.skills.skill_gaps && candidate.skills.skill_gaps.length > 0 ? (
                                    candidate.skills.skill_gaps.map((gap: string, i: number) => (
                                        <Alert key={i} variant="destructive" className="bg-white border-red-200 text-red-800 mb-2">
                                            <AlertTriangle className="h-4 w-4" />
                                            <AlertTitle>Missing Skill</AlertTitle>
                                            <AlertDescription>
                                                Missing required skill: <strong>{gap}</strong>
                                            </AlertDescription>
                                        </Alert>
                                    ))
                                ) : (
                                    <p className="text-sm text-slate-500">No major flags detected.</p>
                                )}
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* JD MATCH TAB */}
                <TabsContent value="jd-match" className="mt-6 space-y-6 animate-fade-in">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Briefcase className="h-5 w-5 text-indigo-600" />
                                Job Description Analysis
                            </CardTitle>
                            <CardDescription>
                                Paste a job description to see how well {candidate.personal_info.name} matches the requirements.
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex gap-2">
                                <input
                                    type="url"
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                    placeholder="Paste JD URL (e.g. LinkedIn, Greenhouse)..."
                                    value={jdUrl}
                                    onChange={(e) => setJdUrl(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleFetchUrl()}
                                />
                                <Button
                                    variant="outline"
                                    onClick={handleFetchUrl}
                                    disabled={fetchingUrl || !jdUrl.trim()}
                                >
                                    {fetchingUrl ? <Loader2 className="h-4 w-4 animate-spin" /> : <ExternalLink className="h-4 w-4" />}
                                    <span className="sr-only sm:not-sr-only sm:ml-2">Fetch</span>
                                </Button>
                            </div>
                            <div className="relative">
                                <div className="absolute inset-0 flex items-center">
                                    <span className="w-full border-t" />
                                </div>
                                <div className="relative flex justify-center text-xs uppercase">
                                    <span className="bg-background px-2 text-muted-foreground mr-2">Or paste text</span>
                                </div>
                            </div>

                            {/* Active Job Selector */}
                            {activeJobs.length > 0 && (
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
                                        Select from Active Jobs
                                    </label>
                                    <div className="relative">
                                        <Briefcase className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                                        <select
                                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 pl-9 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 appearance-none"
                                            value={selectedJobId}
                                            onChange={handleJobSelect}
                                        >
                                            <option value="">-- Choose a saved job profile --</option>
                                            {activeJobs.map((job) => (
                                                <option key={job.id} value={job.id}>
                                                    {job.title} - {job.department}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                    <div className="text-xs text-slate-500 text-center">- OR -</div>
                                </div>
                            )}
                            <textarea
                                className="flex min-h-[150px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-y"
                                placeholder="Paste Job Description here..."
                                value={jdText}
                                onChange={(e) => setJdText(e.target.value)}
                            />
                            <div className="flex justify-end">
                                <Button
                                    onClick={handleAnalyzeMatch}
                                    disabled={analyzing || !jdText.trim()}
                                    className="gap-2"
                                >
                                    {analyzing ? (
                                        <>
                                            <Loader2 className="h-4 w-4 animate-spin" />
                                            Analyzing Match...
                                        </>
                                    ) : (
                                        <>
                                            <Target className="h-4 w-4" />
                                            Analyze Match
                                        </>
                                    )}
                                </Button>
                            </div>

                            {analysisError && (
                                <Alert variant="destructive">
                                    <AlertTriangle className="h-4 w-4" />
                                    <AlertTitle>Analysis Failed</AlertTitle>
                                    <AlertDescription>{analysisError}</AlertDescription>
                                </Alert>
                            )}
                        </CardContent>
                    </Card>

                    {analysisResult && (
                        <div className="grid md:grid-cols-3 gap-6 animate-in slide-in-from-bottom-4 duration-500">
                            {/* Match Score Card */}
                            <Card className="md:col-span-1 border-indigo-100 bg-indigo-50/10 dark:bg-indigo-950/10">
                                <CardHeader>
                                    <CardTitle className="text-center text-lg">Holistic Match Score</CardTitle>
                                </CardHeader>
                                <CardContent className="flex flex-col items-center justify-center pt-2 pb-6">
                                    <MatchScoreRing
                                        score={Math.round((analysisResult.confidence_score || 0) * 100)}
                                        size="xl"
                                    />
                                    <div className="mt-4 text-center px-4">
                                        <Badge variant={analysisResult.recommendation?.toLowerCase().includes('hire') ? 'default' : 'secondary'}>
                                            {analysisResult.recommendation || "Analysis Complete"}
                                        </Badge>
                                    </div>
                                </CardContent>
                            </Card>

                            {/* Analysis Details */}
                            <Card className="md:col-span-2">
                                <CardHeader>
                                    <CardTitle>Analysis Results</CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-6">
                                    <div>
                                        <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                                            <Sparkles className="h-4 w-4 text-purple-500" />
                                            Overall Assessment
                                        </h3>
                                        <p className="text-slate-900 text-sm leading-relaxed font-medium">
                                            {analysisResult.overall_assessment}
                                        </p>
                                    </div>

                                    <Separator />

                                    <div className="grid sm:grid-cols-2 gap-4">
                                        <div className="space-y-2">
                                            <h4 className="font-bold text-sm flex items-center gap-2 text-emerald-800">
                                                <ThumbsUp className="h-4 w-4" />
                                                Key Strengths
                                            </h4>
                                            <div className="text-sm text-slate-900 font-medium">
                                                {analysisResult.technical_skills_assessment?.content}
                                            </div>
                                        </div>

                                        <div className="space-y-2">
                                            <h4 className="font-bold text-sm flex items-center gap-2 text-amber-800">
                                                <Zap className="h-4 w-4" />
                                                Potential Gaps
                                            </h4>
                                            <div className="text-sm text-slate-900 font-medium">
                                                {analysisResult.growth_potential?.content}
                                            </div>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    )}
                </TabsContent>

                {/* EXPERIENCE TAB */}
                <TabsContent value="experience" className="mt-6 space-y-8 animate-fade-in">
                    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                        {/* Navigation Sidebar (Sticky) */}
                        <div className="hidden lg:block col-span-1">
                            <div className="sticky top-24 space-y-1">
                                <h3 className="font-semibold text-sm text-foreground mb-4 px-3">On this page</h3>
                                <a href="#work-experience" className="block px-3 py-2 text-sm text-slate-600 hover:text-indigo-600 hover:bg-slate-50 rounded-md transition-colors">
                                    Work Experience
                                </a>
                                <a href="#education" className="block px-3 py-2 text-sm text-slate-600 hover:text-indigo-600 hover:bg-slate-50 rounded-md transition-colors">
                                    Education
                                </a>
                            </div>
                        </div>

                        {/* Main Timeline Content */}
                        <div className="col-span-1 lg:col-span-3 space-y-10">
                            {/* Work Experience Section */}
                            <section id="work-experience" className="scroll-mt-24">
                                <div className="flex items-center gap-2 mb-6">
                                    <div className="h-8 w-8 rounded-lg bg-blue-100 flex items-center justify-center text-blue-600">
                                        <Briefcase className="h-4 w-4" />
                                    </div>
                                    <h2 className="text-xl font-bold text-foreground">Work Experience</h2>
                                </div>

                                <Card>
                                    <CardContent className="pt-6">
                                        <div className="space-y-8 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px before:h-full before:w-0.5 before:bg-slate-200 dark:before:bg-slate-800">
                                            {experienceList.map((exp: any, index: number) => (
                                                <div key={index} className="relative flex items-start group">
                                                    <div className="absolute left-0 h-10 w-10 flex items-center justify-center rounded-full bg-white dark:bg-slate-900 border-2 border-slate-100 dark:border-slate-800 shadow-sm z-10">
                                                        {exp.company ? (
                                                            <span className="text-xs font-bold text-slate-600 dark:text-slate-400">
                                                                {exp.company.substring(0, 2).toUpperCase()}
                                                            </span>
                                                        ) : (
                                                            <Briefcase className="h-4 w-4 text-slate-400" />
                                                        )}
                                                    </div>
                                                    <div className="ml-16 w-full">
                                                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-2">
                                                            <div>
                                                                <h3 className="text-lg font-bold text-foreground">{exp.role}</h3>
                                                                <p className="text-indigo-950 font-bold">{exp.company}</p>
                                                            </div>
                                                            <Badge variant="outline" className="w-fit mt-1 sm:mt-0 bg-slate-100 text-black border-slate-300 font-bold shadow-sm">
                                                                {exp.dates}
                                                            </Badge>
                                                        </div>
                                                        <p className="text-black text-sm leading-relaxed mb-4 font-medium">
                                                            {exp.description}
                                                        </p>
                                                        {exp.technologies && exp.technologies.length > 0 && (
                                                            <div className="flex flex-wrap gap-2">
                                                                {exp.technologies.map((tech: string) => (
                                                                    <Badge key={tech} variant="secondary" className="text-xs bg-white text-black border border-slate-300 shadow-sm font-semibold">
                                                                        {tech}
                                                                    </Badge>
                                                                ))}
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </CardContent>
                                </Card>
                            </section>

                            {/* Education Section */}
                            <section id="education" className="scroll-mt-24">
                                <div className="flex items-center gap-2 mb-6">
                                    <div className="h-8 w-8 rounded-lg bg-emerald-100 flex items-center justify-center text-emerald-600">
                                        <GraduationCap className="h-4 w-4" />
                                    </div>
                                    <h2 className="text-xl font-bold text-foreground">Education</h2>
                                </div>

                                <Card>
                                    <CardContent className="pt-6">
                                        <div className="space-y-8 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px before:h-full before:w-0.5 before:bg-slate-200 dark:before:bg-slate-800">
                                            {educationList && educationList.length > 0 ? educationList.map((edu: any, index: number) => (
                                                <div key={index} className="relative flex items-start group">
                                                    <div className="absolute left-0 h-10 w-10 flex items-center justify-center rounded-full bg-white dark:bg-slate-900 border-2 border-slate-100 dark:border-slate-800 shadow-sm z-10">
                                                        <GraduationCap className="h-4 w-4 text-emerald-600" />
                                                    </div>
                                                    <div className="ml-16 w-full">
                                                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-2">
                                                            <div>
                                                                <h3 className="text-lg font-bold text-foreground">{edu.institution}</h3>
                                                                <p className="text-emerald-950 font-bold">{edu.degree} {edu.field && `• ${edu.field}`}</p>
                                                            </div>
                                                            <Badge variant="outline" className="w-fit mt-1 sm:mt-0 bg-slate-100 text-black border-slate-300 font-bold shadow-sm">
                                                                {edu.dates}
                                                            </Badge>
                                                        </div>
                                                    </div>
                                                </div>
                                            )) : (
                                                <div className="ml-16 text-slate-500 italic">No education history found.</div>
                                            )}
                                        </div>
                                    </CardContent>
                                </Card>
                            </section>
                        </div>
                    </div>
                </TabsContent>

                {/* SKILLS TAB */}
                <TabsContent value="skills" className="mt-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Skill Verification</CardTitle>
                            <CardDescription>
                                Analysis from Resume and GitHub.
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-6">
                                <div>
                                    <h3 className="text-sm font-medium text-foreground mb-3 flex items-center gap-2">
                                        <Code2 className="h-4 w-4 text-emerald-600" />
                                        Verified by Code Analysis (GitHub)
                                    </h3>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4">
                                        {verifiedSkills.length > 0 ? verifiedSkills.map((skill: any) => (
                                            <div key={skill.name} className="flex flex-col gap-1.5">
                                                <div className="flex justify-between items-center text-sm">
                                                    <span className="font-bold flex items-center gap-1.5 text-black">
                                                        <Code2 className="h-3 w-3 text-emerald-600" />
                                                        {skill.name}
                                                    </span>
                                                    <span className="text-slate-900 text-xs font-bold">
                                                        {skill.confidence > 80 ? 'Expert' : skill.confidence > 60 ? 'Advanced' : 'Intermediate'} ({Math.round(skill.confidence)}%)
                                                    </span>
                                                </div>
                                                <Progress value={skill.confidence} className="h-2" />
                                                {skill.years && (
                                                    <p className="text-[10px] text-muted-foreground text-right">
                                                        ~{skill.years} years exp.
                                                    </p>
                                                )}
                                            </div>
                                        )) : <span className="text-sm text-muted-foreground italic">No skills verified via GitHub yet.</span>}
                                    </div>
                                </div>

                                <Separator />

                                <div>
                                    <h3 className="text-sm font-medium text-foreground mb-3">
                                        Claimed on Resume
                                    </h3>
                                    <div className="flex flex-wrap gap-2">
                                        {claimedSkills.map((skill: any) => {
                                            const proficiency = skill.confidence > 80 ? 'expert' :
                                                skill.confidence > 60 ? 'advanced' :
                                                    skill.confidence > 40 ? 'intermediate' : 'beginner';
                                            return (
                                                <SkillBadge
                                                    key={skill.name}
                                                    skill={skill.name}
                                                    source="resume"
                                                    proficiency={proficiency}
                                                    size="md"
                                                    showIcon={false}
                                                />
                                            );
                                        })}
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* RAW DATA TAB */}
                <TabsContent value="raw" className="mt-6">
                    <Card className="bg-slate-950 text-slate-300 border-slate-800">
                        <CardHeader>
                            <CardTitle className="text-slate-100">Raw JSON Output</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <pre className="overflow-x-auto p-4 rounded bg-slate-900 text-xs font-mono">
                                {JSON.stringify(candidate, null, 2)}
                            </pre>
                        </CardContent>
                    </Card>
                </TabsContent>

            </Tabs>
        </div >
    );
}
