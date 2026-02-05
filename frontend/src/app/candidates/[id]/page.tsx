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
    RefreshCw
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Separator } from "@/components/ui/separator";
import { RecruitRaptorApi, EnrichedCandidateProfile } from "@/lib/api";

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

    if (loading) {
        return (
            <div className="flex h-[50vh] items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                <span className="ml-2 text-slate-500">Loading profile...</span>
            </div>
        );
    }

    if (error || !candidate) {
        return (
            <div className="flex h-[50vh] flex-col items-center justify-center space-y-4">
                <AlertTriangle className="h-12 w-12 text-destructive" />
                <h2 className="text-xl font-semibold">Error Loading Profile</h2>
                <p className="text-slate-500">{error || "Candidate not found"}</p>
                <Button variant="outline" onClick={() => window.location.reload()}>
                    Try Again
                </Button>
            </div>
        );
    }

    // Helper to process skills
    const verifiedSkills = candidate.skills.technical_skills
        .filter((s: any) => s.evidence_sources && s.evidence_sources.includes("github"))
        .map((s: any) => s.skill_name);

    const claimedSkills = candidate.skills.technical_skills
        .filter((s: any) => !s.evidence_sources || !s.evidence_sources.includes("github"))
        .map((s: any) => s.skill_name);

    // Helper to process experience (assuming arrays are aligned by index)
    const experienceList = candidate.experience.companies.map((company: string, index: number) => ({
        company,
        role: candidate.experience.positions[index] || "Role",
        dates: candidate.experience.dates[index] || "Dates unknown",
        description: candidate.experience.descriptions[index] || "",
        technologies: candidate.experience.technologies_used[company] || []
    }));

    return (
        <div className="space-y-6 max-w-5xl mx-auto">
            {/* Back Button */}
            <div className="flex items-center gap-2 text-slate-500 hover:text-slate-900 transition-colors">
                <Link href="/candidates" className="flex items-center gap-1">
                    <ChevronLeft className="h-4 w-4" />
                    Back to Candidates
                </Link>
            </div>

            {/* Header Profile Card */}
            <div className="bg-white rounded-xl border shadow-sm p-6">
                <div className="flex flex-col md:flex-row gap-6 items-start">
                    <div className="h-20 w-20 rounded-full bg-slate-100 flex items-center justify-center text-2xl font-bold text-slate-500 uppercase">
                        {candidate.personal_info.name.split(' ').map((n: string) => n[0]).join('').slice(0, 2)}
                    </div>

                    <div className="flex-1 space-y-2">
                        <div className="flex items-center justify-between">
                            <div>
                                <h1 className="text-2xl font-bold text-slate-900">{candidate.personal_info.name}</h1>
                                <p className="text-slate-500">{candidate.personal_info.linkedin_username || candidate.personal_info.github_username}</p>
                            </div>
                            <div className="text-right">
                                <div className="text-3xl font-bold text-blue-600">{Math.round((candidate.job_relevance_score || 0) * 100)}%</div>
                                <div className="text-xs text-slate-500 uppercase tracking-wide font-medium">Match Score</div>
                            </div>
                        </div>

                        <div className="flex flex-wrap gap-4 text-sm text-slate-600 mt-2">
                            {candidate.personal_info.email && (
                                <div className="flex items-center gap-1.5">
                                    <Mail className="h-4 w-4" />
                                    {candidate.personal_info.email}
                                </div>
                            )}
                            {candidate.personal_info.location && (
                                <div className="flex items-center gap-1.5">
                                    <MapPin className="h-4 w-4" />
                                    {candidate.personal_info.location}
                                </div>
                            )}
                            <div className="flex items-center gap-3">
                                {candidate.personal_info.linkedin_url && (
                                    <a href={candidate.personal_info.linkedin_url.startsWith('http') ? candidate.personal_info.linkedin_url : `https://${candidate.personal_info.linkedin_url}`} target="_blank" className="flex items-center gap-1 text-blue-700 hover:underline">
                                        <Linkedin className="h-4 w-4" />
                                        LinkedIn
                                    </a>
                                )}
                                {candidate.personal_info.github_url && (
                                    <a href={candidate.personal_info.github_url.startsWith('http') ? candidate.personal_info.github_url : `https://${candidate.personal_info.github_url}`} target="_blank" className="flex items-center gap-1 text-slate-900 hover:underline">
                                        <Github className="h-4 w-4" />
                                        GitHub
                                    </a>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content Tabs */}
            <Tabs defaultValue="overview" className="w-full">
                <TabsList className="grid w-full grid-cols-4 lg:w-[400px]">
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="experience">Experience</TabsTrigger>
                    <TabsTrigger value="skills">Skills</TabsTrigger>
                    <TabsTrigger value="raw">Raw Data</TabsTrigger>
                </TabsList>

                {/* OVERVIEW TAB */}
                <TabsContent value="overview" className="mt-6 space-y-6">
                    <Card>
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

                {/* EXPERIENCE TAB */}
                <TabsContent value="experience" className="mt-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Work Experience</CardTitle>
                            <CardDescription>Extracted from Resume.</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-8 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px before:h-full before:w-0.5 before:bg-slate-200">
                                {experienceList.map((exp: any, index: number) => (
                                    <div key={index} className="relative flex items-start group">
                                        <div className="absolute left-0 h-10 w-10 flex items-center justify-center rounded-full bg-white border border-slate-200 text-slate-500 z-10">
                                            <Calendar className="h-5 w-5" />
                                        </div>
                                        <div className="ml-16 w-full">
                                            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-1">
                                                <h3 className="font-semibold text-slate-900">{exp.role}</h3>
                                                <span className="text-sm text-slate-500">{exp.dates}</span>
                                            </div>
                                            <p className="text-blue-600 font-medium text-sm mb-2">{exp.company}</p>
                                            <p className="text-slate-600 text-sm mb-3">
                                                {exp.description}
                                            </p>
                                            <div className="flex flex-wrap gap-2">
                                                {exp.technologies && exp.technologies.map((tech: string) => (
                                                    <Badge key={tech} variant="secondary" className="text-xs bg-slate-100 text-slate-600">
                                                        {tech}
                                                    </Badge>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
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
                                    <h3 className="text-sm font-medium text-slate-900 mb-3 flex items-center gap-2">
                                        <Code2 className="h-4 w-4 text-green-600" />
                                        Verified by Code Analysis (GitHub)
                                    </h3>
                                    <div className="flex flex-wrap gap-2">
                                        {verifiedSkills.length > 0 ? verifiedSkills.map((skill: string) => (
                                            <Badge key={skill} className="bg-green-100 text-green-700 hover:bg-green-200 border-green-200 pl-1 pr-3 py-1 text-sm gap-1">
                                                <CheckCircle2 className="h-3 w-3" />
                                                {skill}
                                            </Badge>
                                        )) : <span className="text-sm text-slate-400 italic">No skills verified via GitHub yet.</span>}
                                    </div>
                                </div>

                                <Separator />

                                <div>
                                    <h3 className="text-sm font-medium text-slate-900 mb-3">
                                        Claimed on Resume
                                    </h3>
                                    <div className="flex flex-wrap gap-2">
                                        {claimedSkills.map((skill: string) => (
                                            <Badge key={skill} variant="secondary" className="pl-3 pr-3 py-1 text-sm">
                                                {skill}
                                            </Badge>
                                        ))}
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
        </div>
    );
}
