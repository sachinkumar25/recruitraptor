"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  Users,
  FileText,
  TrendingUp,
  Clock,
  ArrowUpRight,
  Sparkles,
  Upload,
  Zap
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MatchScoreRing } from "@/components/ui/MatchScoreRing";
import { RecruitRaptorApi, EnrichedCandidateProfile } from "@/lib/api";

// Stat card configuration
const statConfig = [
  {
    title: "Total Candidates",
    icon: Users,
    gradient: "from-blue-500 to-indigo-600",
    iconBg: "bg-blue-500/10",
    iconColor: "text-blue-500",
  },
  {
    title: "Analyzed Today",
    icon: FileText,
    gradient: "from-emerald-500 to-teal-600",
    iconBg: "bg-emerald-500/10",
    iconColor: "text-emerald-500",
  },
  {
    title: "Avg Match Score",
    icon: TrendingUp,
    gradient: "from-purple-500 to-pink-600",
    iconBg: "bg-purple-500/10",
    iconColor: "text-purple-500",
  },
  {
    title: "Pending Review",
    icon: Clock,
    gradient: "from-amber-500 to-orange-600",
    iconBg: "bg-amber-500/10",
    iconColor: "text-amber-500",
  },
];

export default function Dashboard() {
  const [candidates, setCandidates] = useState<EnrichedCandidateProfile[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCandidates = async () => {
      try {
        const data = await RecruitRaptorApi.getCandidates();
        setCandidates(data);
      } catch (err) {
        console.error("Failed to fetch candidates:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchCandidates();
  }, []);

  // Calculate stats from real data
  const stats = [
    { value: candidates.length.toString(), change: "+12%" },
    {
      value: candidates.filter(c => {
        const today = new Date().toDateString();
        return new Date(c.enrichment_timestamp).toDateString() === today;
      }).length.toString(), change: "+3"
    },
    {
      value: candidates.length > 0
        ? Math.round(candidates.reduce((acc, c) => acc + (c.job_relevance_score || 0), 0) / candidates.length * 100) + "%"
        : "0%",
      change: "+2.4%"
    },
    { value: candidates.filter(c => !c.personal_info?.bio).length.toString(), change: "-5" },
  ];

  const recentCandidates = candidates.slice(0, 5);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 p-8 text-white">
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-20" />
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="h-5 w-5" />
              <span className="text-sm font-medium text-white/80">AI-Powered Recruiting</span>
            </div>
            <h1 className="text-3xl md:text-4xl font-bold tracking-tight mb-2">
              Welcome back, Sachin
            </h1>
            <p className="text-white/80 max-w-md">
              You have {candidates.filter(c => !c.personal_info?.bio).length} candidates awaiting review.
              Let AI help you find the perfect match.
            </p>
          </div>
          <div className="flex gap-3">
            <Button size="lg" className="bg-white text-indigo-600 hover:bg-white/90 shadow-xl gap-2" asChild>
              <Link href="/upload">
                <Upload className="h-5 w-5" />
                Upload Resume
              </Link>
            </Button>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statConfig.map((stat, index) => (
          <Card
            key={stat.title}
            className="group relative overflow-hidden border-0 shadow-card hover:shadow-card-hover transition-all duration-300 hover:-translate-y-1"
          >
            <div className={`absolute inset-0 bg-gradient-to-br ${stat.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-300`} />
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <div className={`h-10 w-10 rounded-xl ${stat.iconBg} flex items-center justify-center`}>
                <stat.icon className={`h-5 w-5 ${stat.iconColor}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-foreground">
                {loading ? (
                  <div className="h-9 w-20 rounded shimmer" />
                ) : (
                  stats[index].value
                )}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                <span className={stats[index].change.startsWith('+') ? "text-emerald-600 font-medium" : "text-red-500 font-medium"}>
                  {stats[index].change}
                </span>{" "}
                from last week
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent Candidates & Quick Actions */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Recent Candidates */}
        <Card className="lg:col-span-2 border-0 shadow-card">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-xl">Recent Candidates</CardTitle>
                <CardDescription>
                  Latest resumes processed by the system
                </CardDescription>
              </div>
              <Button variant="outline" size="sm" asChild className="gap-1.5">
                <Link href="/candidates">
                  View All <ArrowUpRight className="h-4 w-4" />
                </Link>
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-4">
                {[1, 2, 3].map(i => (
                  <div key={i} className="flex items-center gap-4 p-4 rounded-xl border shimmer h-20" />
                ))}
              </div>
            ) : recentCandidates.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                <FileText className="h-12 w-12 mx-auto mb-4 opacity-30" />
                <p>No candidates yet. Upload a resume to get started.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {recentCandidates.map((candidate) => (
                  <Link
                    key={candidate.candidate_id}
                    href={`/candidates/${candidate.candidate_id}`}
                    className="flex items-center justify-between p-4 rounded-xl border border-slate-100 dark:border-slate-800 hover:border-indigo-200 dark:hover:border-indigo-800 hover:bg-slate-50/50 dark:hover:bg-slate-900/50 transition-all duration-200 group"
                  >
                    <div className="flex items-center gap-4">
                      <div className="h-12 w-12 rounded-full bg-gradient-to-br from-indigo-100 to-purple-100 dark:from-indigo-900/30 dark:to-purple-900/30 flex items-center justify-center text-indigo-600 dark:text-indigo-400 font-semibold text-sm">
                        {candidate.personal_info.name.split(' ').map((n: string) => n[0]).join('').slice(0, 2)}
                      </div>
                      <div>
                        <h3 className="font-semibold text-foreground group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                          {candidate.personal_info.name}
                        </h3>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <span>{candidate.personal_info.email || 'No email'}</span>
                          <span className="text-slate-300">•</span>
                          <span>{new Date(candidate.enrichment_timestamp).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      <div className="hidden md:flex gap-1.5">
                        {candidate.skills?.technical_skills?.slice(0, 2).map((skill: any) => (
                          <Badge key={skill.skill_name} variant="secondary" className="text-xs bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                            {skill.skill_name}
                          </Badge>
                        ))}
                      </div>
                      <MatchScoreRing
                        score={Math.round((candidate.job_relevance_score || 0) * 100)}
                        size="sm"
                      />
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions & Insights */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <Card className="border-0 shadow-card overflow-hidden">
            <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-6 text-white">
              <div className="flex items-center gap-2 mb-2">
                <Zap className="h-5 w-5" />
                <span className="font-semibold">Quick Actions</span>
              </div>
              <p className="text-sm text-white/80">Speed up your workflow</p>
            </div>
            <CardContent className="p-4 space-y-2">
              <Button variant="ghost" className="w-full justify-start gap-3 h-12 hover:bg-slate-50 dark:hover:bg-slate-800" asChild>
                <Link href="/upload">
                  <div className="h-8 w-8 rounded-lg bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
                    <Upload className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
                  </div>
                  <div className="text-left">
                    <div className="font-medium text-sm">Upload Resume</div>
                    <div className="text-xs text-muted-foreground">Add new candidate</div>
                  </div>
                </Link>
              </Button>
              <Button variant="ghost" className="w-full justify-start gap-3 h-12 hover:bg-slate-50 dark:hover:bg-slate-800" asChild>
                <Link href="/candidates">
                  <div className="h-8 w-8 rounded-lg bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
                    <Users className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                  </div>
                  <div className="text-left">
                    <div className="font-medium text-sm">View Candidates</div>
                    <div className="text-xs text-muted-foreground">Browse all profiles</div>
                  </div>
                </Link>
              </Button>
            </CardContent>
          </Card>

          {/* Top Skills */}
          <Card className="border-0 shadow-card">
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Top Skills in Pipeline</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { skill: "Python", percent: 62, color: "bg-blue-500" },
                  { skill: "React", percent: 48, color: "bg-indigo-500" },
                  { skill: "TypeScript", percent: 35, color: "bg-purple-500" },
                ].map(item => (
                  <div key={item.skill} className="space-y-1.5">
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">{item.skill}</span>
                      <span className="text-muted-foreground">{item.percent}%</span>
                    </div>
                    <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${item.color} rounded-full transition-all duration-1000`}
                        style={{ width: `${item.percent}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
