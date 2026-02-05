"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, Filter, MoreHorizontal, Loader2, RefreshCw } from "lucide-react";
import { RecruitRaptorApi, EnrichedCandidateProfile } from "@/lib/api";

export default function CandidatesPage() {
    const [candidates, setCandidates] = useState<EnrichedCandidateProfile[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

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

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-slate-900">Candidates</h1>
                    <p className="text-slate-500 mt-1">Manage and screen scanned resumes.</p>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" size="icon" onClick={fetchCandidates} title="Refresh List">
                        <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                    </Button>
                    <Link href="/upload">
                        <Button>Fast Upload</Button>
                    </Link>
                </div>
            </div>

            <div className="bg-white rounded-lg border shadow-sm p-4">
                {/* Toolbar */}
                <div className="flex items-center gap-4 mb-4">
                    <div className="relative flex-1">
                        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
                        <Input
                            placeholder="Filter candidates..."
                            className="pl-9 w-full md:w-[300px]"
                        />
                    </div>
                    <Button variant="outline" size="sm" className="gap-2">
                        <Filter className="h-4 w-4" />
                        Filter
                    </Button>
                </div>

                {/* Table */}
                <div className="rounded-md border">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Candidate</TableHead>
                                <TableHead>Overall Confidence</TableHead>
                                <TableHead>Skills</TableHead>
                                <TableHead>Match Score</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead className="text-right">Actions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {loading && candidates.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={6} className="h-24 text-center">
                                        <div className="flex justify-center items-center gap-2 text-slate-500">
                                            <Loader2 className="h-4 w-4 animate-spin" /> Loading candidates...
                                        </div>
                                    </TableCell>
                                </TableRow>
                            ) : candidates.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={6} className="h-24 text-center text-slate-500">
                                        No candidates found. Upload a resume to get started.
                                    </TableCell>
                                </TableRow>
                            ) : (
                                candidates.map((candidate) => {
                                    // Helper: extract top skills
                                    const topSkills = candidate.skills?.technical_skills
                                        ?.slice(0, 3)
                                        .map((s: any) => s.skill_name) || [];
                                    const extraSkillsCount = (candidate.skills?.technical_skills?.length || 0) - 3;

                                    const matchScore = Math.round((candidate.job_relevance_score || 0) * 100);

                                    return (
                                        <TableRow key={candidate.candidate_id} className="cursor-pointer hover:bg-slate-50">
                                            <TableCell className="font-medium">
                                                <Link href={`/candidates/${candidate.candidate_id}`} className="block">
                                                    {candidate.personal_info.name}
                                                    <div className="text-xs text-slate-500 font-normal">
                                                        {new Date(candidate.enrichment_timestamp).toLocaleDateString()}
                                                    </div>
                                                </Link>
                                            </TableCell>
                                            <TableCell>
                                                <Badge variant="outline" className={candidate.overall_confidence > 0.8 ? "text-green-600 border-green-200" : "text-slate-600"}>
                                                    {(candidate.overall_confidence * 100).toFixed(0)}%
                                                </Badge>
                                            </TableCell>
                                            <TableCell>
                                                <div className="flex flex-wrap gap-1">
                                                    {topSkills.map((skill: string) => (
                                                        <Badge key={skill} variant="outline" className="text-xs font-normal">
                                                            {skill}
                                                        </Badge>
                                                    ))}
                                                    {extraSkillsCount > 0 && (
                                                        <span className="text-xs text-slate-400 ml-1">+{extraSkillsCount}</span>
                                                    )}
                                                </div>
                                            </TableCell>
                                            <TableCell>
                                                <div className="flex items-center gap-2">
                                                    <span className={`font-bold ${matchScore >= 90 ? 'text-green-600' : matchScore >= 80 ? 'text-blue-600' : 'text-slate-600'}`}>
                                                        {matchScore}%
                                                    </span>
                                                    <div className="h-2 w-16 bg-slate-100 rounded-full overflow-hidden">
                                                        <div
                                                            className={`h-full rounded-full ${matchScore >= 90 ? 'bg-green-500' : matchScore >= 80 ? 'bg-blue-500' : 'bg-slate-400'}`}
                                                            style={{ width: `${matchScore}%` }}
                                                        ></div>
                                                    </div>
                                                </div>
                                            </TableCell>
                                            <TableCell>
                                                <Badge variant="default" className="bg-blue-600 hover:bg-blue-700">
                                                    Enriched
                                                </Badge>
                                            </TableCell>
                                            <TableCell className="text-right">
                                                <Button variant="ghost" size="icon">
                                                    <MoreHorizontal className="h-4 w-4" />
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    );
                                })
                            )}
                        </TableBody>
                    </Table>
                </div>
            </div>
        </div>
    );
}
