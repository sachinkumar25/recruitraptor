"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import {
    Search,
    Filter,
    LayoutGrid,
    List,
    Loader2,
    RefreshCw,
    Upload,
    Mail,
    Github,
    Linkedin,
    SlidersHorizontal,
    ArrowUpDown
} from "lucide-react";
import { RecruitRaptorApi, EnrichedCandidateProfile } from "@/lib/api";
import { MatchScoreRing } from "@/components/ui/MatchScoreRing";
import { SkillBadge } from "@/components/ui/SkillBadge";
import { CandidateCard } from "@/components/candidates/CandidateCard";
import { AdvancedFilterPanel, FilterState, initialFilterState } from "@/components/candidates/AdvancedFilterPanel";
import { cn } from "@/lib/utils";

type ViewMode = "grid" | "table";

export default function CandidatesPage() {
    const [candidates, setCandidates] = useState<EnrichedCandidateProfile[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchQuery, setSearchQuery] = useState("");
    const [viewMode, setViewMode] = useState<ViewMode>("grid");
    const [sortBy, setSortBy] = useState<"date" | "score" | "name">("date");
    const [isFilterOpen, setIsFilterOpen] = useState(false);
    const [filters, setFilters] = useState<FilterState>(initialFilterState);

    const fetchCandidates = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await RecruitRaptorApi.getCandidates();
            setCandidates(data);
        } catch (err) {
            console.error("Failed to fetch candidates:", err);
            setError("Failed to load candidates.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCandidates();
    }, []);

    // Filter and sort candidates
    const filteredCandidates = candidates
        .filter(c => {
            const query = searchQuery.toLowerCase();
            const matchesSearch = (
                c.personal_info.name.toLowerCase().includes(query) ||
                c.personal_info.email?.toLowerCase().includes(query) ||
                c.skills?.technical_skills?.some((s: any) =>
                    s.skill_name.toLowerCase().includes(query)
                )
            );

            const matchesScore = (c.job_relevance_score || 0) * 100 >= filters.minScore;

            const matchesSources = (
                (filters.sources.github ? c.personal_info.github_url : true) &&
                (filters.sources.linkedin ? c.personal_info.linkedin_url : true) &&
                (filters.sources.resume ? true : true) // Resume is always present usually
            );

            // Logic for source filtering: if a source is UNCHECKED, we don't filter OUT candidates that have it, 
            // but usually source filters mean "Must have X". 
            // Only if "Github" is checked, candidate must have Github? 
            // Or if "Github" is unchecked, we assume we don't care?
            // Let's assume checked means "Show candidates from this source". 
            // But candidates have multiple sources.
            // Let's implement: If Github is unchecked, hide candidates that ONLY have Github? No.
            // Let's implement: If Github is checked, candidate MUST have Github url IF we strictly require it?
            // The UI says "Data Sources". Usually this means "Include data from...". 
            // Actually, for candidates, it usually means "Has Profile On...".
            // So if Github is checked, show candidates who have Github.
            // If ALL are checked, show everyone? 
            // Let's refine the logic: Show candidate if they match ANY of the selected sources? 
            // Or show if they have ALL required sources?
            // "Data Sources" usually implies "Enriched with...". 
            // Let's go with: If Github is checked, we WANT candidates with Github. 
            // If it's unchecked, we don't require it.
            // Wait, if I uncheck Github, do I want to HIDE candidates with Github? Or just not require it?
            // Usually filters are restrictive.
            // Let's do: If Github is checked, candidate MUST have Github.

            const hasGithub = !!c.personal_info.github_url;
            const hasLinkedin = !!c.personal_info.linkedin_url;

            // If checked, it is REQUIRED.
            const matchesGithub = filters.sources.github ? hasGithub : true;
            const matchesLinkedin = filters.sources.linkedin ? hasLinkedin : true;

            // Resume is always base.

            const candidateSkills = c.skills?.technical_skills?.map((s: any) => s.skill_name.toLowerCase()) || [];
            const matchesSkills = filters.skills.every(skill =>
                candidateSkills.includes(skill.toLowerCase())
            );

            return matchesSearch && matchesScore && matchesGithub && matchesLinkedin && matchesSkills;
        })
        .sort((a, b) => {
            switch (sortBy) {
                case "score":
                    return (b.job_relevance_score || 0) - (a.job_relevance_score || 0);
                case "name":
                    return a.personal_info.name.localeCompare(b.personal_info.name);
                case "date":
                default:
                    return new Date(b.enrichment_timestamp).getTime() - new Date(a.enrichment_timestamp).getTime();
            }
        });

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-foreground">Candidates</h1>
                    <p className="text-muted-foreground mt-1">
                        {candidates.length} candidates in your pipeline
                    </p>
                </div>
                <div className="flex gap-2">
                    <Button
                        variant="outline"
                        size="icon"
                        onClick={fetchCandidates}
                        title="Refresh List"
                        className="shrink-0"
                    >
                        <RefreshCw className={cn("h-4 w-4", loading && "animate-spin")} />
                    </Button>
                    <Link href="/upload">
                        <Button className="gap-2 bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 shadow-lg shadow-indigo-500/25">
                            <Upload className="h-4 w-4" />
                            Upload Resume
                        </Button>
                    </Link>
                </div>
            </div>

            {/* Toolbar */}
            <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 shadow-sm">
                <div className="flex flex-1 gap-3 w-full sm:w-auto">
                    {/* Search */}
                    <div className="relative flex-1 max-w-md">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input
                            placeholder="Search by name, email, or skills..."
                            className="pl-9 bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                    </div>

                    {/* Sort */}
                    <div className="flex items-center gap-2">
                        <Button variant="outline" size="sm" className="gap-2">
                            <ArrowUpDown className="h-4 w-4" />
                            <select
                                className="bg-transparent border-0 outline-none text-sm cursor-pointer"
                                value={sortBy}
                                onChange={(e) => setSortBy(e.target.value as any)}
                            >
                                <option value="date">Newest</option>
                                <option value="score">Match Score</option>
                                <option value="name">Name</option>
                            </select>
                        </Button>
                    </div>

                    {/* Filter Toggle */}
                    <div className="flex items-center gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            className={cn(
                                "gap-2",
                                (filters.minScore > 0 || filters.skills.length > 0 || !filters.sources.github || !filters.sources.linkedin) && "border-indigo-500 text-indigo-600 bg-indigo-50"
                            )}
                            onClick={() => setIsFilterOpen(true)}
                        >
                            <SlidersHorizontal className="h-4 w-4" />
                            <span className="hidden sm:inline">Filters</span>
                            {(filters.minScore > 0 || filters.skills.length > 0) && (
                                <Badge variant="secondary" className="ml-1 px-1 py-0 h-5 text-[10px] bg-indigo-100 text-indigo-700 hover:bg-indigo-100">
                                    Active
                                </Badge>
                            )}
                        </Button>
                    </div>
                </div>

                {/* View Mode Toggle */}
                <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1">
                    <Button
                        variant="ghost"
                        size="sm"
                        className={cn(
                            "gap-1.5 px-3",
                            viewMode === "grid" && "bg-white dark:bg-slate-700 shadow-sm"
                        )}
                        onClick={() => setViewMode("grid")}
                    >
                        <LayoutGrid className="h-4 w-4" />
                        <span className="hidden sm:inline">Grid</span>
                    </Button>
                    <Button
                        variant="ghost"
                        size="sm"
                        className={cn(
                            "gap-1.5 px-3",
                            viewMode === "table" && "bg-white dark:bg-slate-700 shadow-sm"
                        )}
                        onClick={() => setViewMode("table")}
                    >
                        <List className="h-4 w-4" />
                        <span className="hidden sm:inline">List</span>
                    </Button>
                </div>
            </div>

            {/* Content */}
            {loading && candidates.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-20">
                    <Loader2 className="h-8 w-8 animate-spin text-indigo-500 mb-4" />
                    <p className="text-muted-foreground">Loading candidates...</p>
                </div>
            ) : filteredCandidates.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-20 text-center">
                    <div className="h-16 w-16 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-4">
                        <Search className="h-8 w-8 text-slate-400" />
                    </div>
                    <h3 className="text-lg font-semibold mb-1">No candidates found</h3>
                    <p className="text-muted-foreground max-w-sm">
                        {searchQuery
                            ? "Try adjusting your search terms"
                            : "Upload a resume to add your first candidate"}
                    </p>
                    {!searchQuery && (
                        <Link href="/upload" className="mt-4">
                            <Button className="gap-2">
                                <Upload className="h-4 w-4" />
                                Upload Resume
                            </Button>
                        </Link>
                    )}
                </div>
            ) : viewMode === "grid" ? (
                /* Grid View */
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {filteredCandidates.map((candidate) => {
                        const matchScore = Math.round((candidate.job_relevance_score || 0) * 100);
                        const topSkills = candidate.skills?.technical_skills?.slice(0, 4) || [];

                        return (
                            <CandidateCard key={candidate.candidate_id} candidate={candidate} />
                        );
                    })}
                </div>
            ) : (
                /* Table View */
                <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
                                <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Candidate</th>
                                <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground hidden md:table-cell">Skills</th>
                                <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Match</th>
                                <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground hidden sm:table-cell">Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredCandidates.map((candidate) => {
                                const matchScore = Math.round((candidate.job_relevance_score || 0) * 100);
                                const topSkills = candidate.skills?.technical_skills?.slice(0, 3) || [];

                                return (
                                    <tr
                                        key={candidate.candidate_id}
                                        className="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer"
                                        onClick={() => window.location.href = `/candidates/${candidate.candidate_id}`}
                                    >
                                        <td className="py-4 px-4">
                                            <div className="flex items-center gap-3">
                                                <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-semibold text-sm">
                                                    {candidate.personal_info.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                                                </div>
                                                <div>
                                                    <div className="font-medium text-foreground">{candidate.personal_info.name}</div>
                                                    <div className="text-sm text-muted-foreground">{candidate.personal_info.email || 'No email'}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="py-4 px-4 hidden md:table-cell">
                                            <div className="flex flex-wrap gap-1">
                                                {topSkills.map((skill: any) => (
                                                    <Badge key={skill.skill_name} variant="secondary" className="text-xs">
                                                        {skill.skill_name}
                                                    </Badge>
                                                ))}
                                            </div>
                                        </td>
                                        <td className="py-4 px-4">
                                            <MatchScoreRing score={matchScore} size="sm" />
                                        </td>
                                        <td className="py-4 px-4 text-sm text-muted-foreground hidden sm:table-cell">
                                            {new Date(candidate.enrichment_timestamp).toLocaleDateString()}
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            )}


            <AdvancedFilterPanel
                isOpen={isFilterOpen}
                onClose={() => setIsFilterOpen(false)}
                filters={filters}
                onFilterChange={setFilters}
                onClearFilters={() => setFilters(initialFilterState)}
            />
        </div>
    );
}
