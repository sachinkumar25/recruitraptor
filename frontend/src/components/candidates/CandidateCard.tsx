import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Mail, Github, Linkedin } from "lucide-react";
import { MatchScoreRing } from "@/components/ui/MatchScoreRing";
import { SkillBadge } from "@/components/ui/SkillBadge";
import { EnrichedCandidateProfile } from "@/lib/api";

interface CandidateCardProps {
    candidate: EnrichedCandidateProfile;
}

export function CandidateCard({ candidate }: CandidateCardProps) {
    const matchScore = Math.round((candidate.job_relevance_score || 0) * 100);
    const topSkills = candidate.skills?.technical_skills?.slice(0, 4) || [];

    return (
        <Link href={`/candidates/${candidate.candidate_id}`}>
            <Card className="group h-full border-0 shadow-card hover:shadow-card-hover transition-all duration-300 hover:-translate-y-1 cursor-pointer overflow-hidden">
                {/* Gradient Header */}
                <div className="h-20 bg-gradient-to-br from-indigo-500/10 via-purple-500/10 to-pink-500/10 relative">
                    <div className="absolute -bottom-8 left-6">
                        <div className="h-16 w-16 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg shadow-lg ring-4 ring-white dark:ring-slate-900">
                            {candidate.personal_info.name.split(' ').map((n: string) => n[0]).join('').slice(0, 2)}
                        </div>
                    </div>
                    <div className="absolute top-3 right-3">
                        <MatchScoreRing score={matchScore} size="sm" />
                    </div>
                </div>

                <CardContent className="pt-12 pb-6">
                    <div className="mb-4">
                        <h3 className="font-semibold text-lg text-foreground group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                            {candidate.personal_info.name}
                        </h3>
                        {candidate.personal_info.email && (
                            <p className="text-sm text-muted-foreground flex items-center gap-1.5 mt-1">
                                <Mail className="h-3.5 w-3.5" />
                                {candidate.personal_info.email}
                            </p>
                        )}
                    </div>

                    {/* Social Links */}
                    <div className="flex gap-2 mb-4">
                        {candidate.personal_info.github_url && (
                            <Badge variant="outline" className="gap-1 text-xs">
                                <Github className="h-3 w-3" />
                                GitHub
                            </Badge>
                        )}
                        {candidate.personal_info.linkedin_url && (
                            <Badge variant="outline" className="gap-1 text-xs">
                                <Linkedin className="h-3 w-3" />
                                LinkedIn
                            </Badge>
                        )}
                    </div>

                    {/* Skills */}
                    <div className="flex flex-wrap gap-1.5">
                        {topSkills.map((skill: any, i: number) => (
                            <SkillBadge
                                key={skill.skill_name}
                                skill={skill.skill_name}
                                source={skill.evidence_sources?.includes("github") ? "github" : "resume"}
                                size="sm"
                                showIcon={i === 0}
                            />
                        ))}
                        {(candidate.skills?.technical_skills?.length || 0) > 4 && (
                            <Badge variant="secondary" className="text-xs">
                                +{candidate.skills.technical_skills.length - 4}
                            </Badge>
                        )}
                    </div>
                </CardContent>
            </Card>
        </Link>
    );
}
