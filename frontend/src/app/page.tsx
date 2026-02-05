import Link from "next/link";
import {
  Users,
  FileText,
  TrendingUp,
  Clock,
  ArrowUpRight
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

// Mock Data for Dashboard
const stats = [
  {
    title: "Total Candidates",
    value: "1,248",
    change: "+12%",
    icon: Users,
  },
  {
    title: "Analyzed Resumes",
    value: "845",
    change: "+18%",
    icon: FileText,
  },
  {
    title: "Avg Match Score",
    value: "78%",
    change: "+2.4%",
    icon: TrendingUp,
  },
  {
    title: "Pending Review",
    value: "24",
    change: "-5%",
    icon: Clock,
  },
];

const recentCandidates = [
  {
    id: "1",
    name: "Sarah Chen",
    role: "Senior Full Stack Engineer",
    appliedDate: "2 hrs ago",
    matchScore: 92,
    status: "Analyzed",
    skills: ["React", "Node.js", "AWS"],
    image: null
  },
  {
    id: "2",
    name: "Michael Ross",
    role: "DevOps Specialist",
    appliedDate: "4 hrs ago",
    matchScore: 88,
    status: "Enriched",
    skills: ["Kubernetes", "Docker", "Python"],
    image: null
  },
  {
    id: "3",
    name: "Jessica Wu",
    role: "Product Manager",
    appliedDate: "1 day ago",
    matchScore: 75,
    status: "Processing",
    skills: ["Agile", "Roadmapping", "SQL"],
    image: null
  },
  {
    id: "4",
    name: "David Kim",
    role: "Frontend Developer",
    appliedDate: "1 day ago",
    matchScore: 81,
    status: "Analyzed",
    skills: ["Vue.js", "TypeScript", "Tailwind"],
    image: null
  },
];

export default function Dashboard() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Dashboard</h1>
          <p className="text-slate-500 mt-1">Overview of candidate pipeline and recent activity.</p>
        </div>
        <div className="flex gap-2">
          <Link href="/upload">
            <Button>
              <FileText className="mr-2 h-4 w-4" />
              Upload Resume
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium text-slate-500">
                {stat.title}
              </CardTitle>
              <stat.icon className="h-4 w-4 text-slate-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-slate-900">{stat.value}</div>
              <p className="text-xs text-slate-500 mt-1">
                <span className={stat.change.startsWith('+') ? "text-green-600 font-medium" : "text-red-600 font-medium"}>
                  {stat.change}
                </span>{" "}
                from last month
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent Activity / Pipeline */}
      <div className="grid gap-6 md:grid-cols-7">
        <Card className="col-span-4 lg:col-span-5">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Recent Candidates</CardTitle>
                <CardDescription>
                  Latest resumes processed by the system.
                </CardDescription>
              </div>
              <Button variant="outline" size="sm" asChild>
                <Link href="/candidates">
                  View All <ArrowUpRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentCandidates.map((candidate) => (
                <div key={candidate.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-slate-50 transition-colors">
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 font-semibold">
                      {candidate.name.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div>
                      <h3 className="font-medium text-slate-900">{candidate.name}</h3>
                      <p className="text-sm text-slate-500">{candidate.role}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-6">
                    <div className="hidden md:flex gap-2">
                      {candidate.skills.slice(0, 2).map(skill => (
                        <Badge key={skill} variant="secondary" className="px-2 py-0.5 text-xs text-slate-600 bg-slate-100">
                          {skill}
                        </Badge>
                      ))}
                      {candidate.skills.length > 2 && (
                        <Badge variant="secondary" className="px-2 py-0.5 text-xs bg-slate-100">+{candidate.skills.length - 2}</Badge>
                      )}
                    </div>
                    <div className="text-right min-w-[80px]">
                      <div className="font-bold text-slate-900">{candidate.matchScore}%</div>
                      <div className="text-xs text-slate-500">Match</div>
                    </div>
                    <Button size="sm" variant="ghost">View</Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions / Insights */}
        <Card className="col-span-3 lg:col-span-2">
          <CardHeader>
            <CardTitle>Quick Insights</CardTitle>
            <CardDescription>System performance & top skills</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div>
                <h4 className="text-sm font-medium text-slate-500 mb-3">Top Detected Skills</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>React/Next.js</span>
                    <span className="font-medium">42%</span>
                  </div>
                  <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 rounded-full" style={{ width: "42%" }}></div>
                  </div>

                  <div className="flex items-center justify-between text-sm mt-3">
                    <span>Python/Django</span>
                    <span className="font-medium">28%</span>
                  </div>
                  <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                    <div className="h-full bg-indigo-500 rounded-full" style={{ width: "28%" }}></div>
                  </div>

                  <div className="flex items-center justify-between text-sm mt-3">
                    <span>Kubernetes</span>
                    <span className="font-medium">15%</span>
                  </div>
                  <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                    <div className="h-full bg-cyan-500 rounded-full" style={{ width: "15%" }}></div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
