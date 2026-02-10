
"use client";

import { useEffect, useState } from "react";
import { Plus, Briefcase, MapPin, Calendar, Trash2, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { JobProfile, JobService } from "@/lib/jobs";
import { formatDistanceToNow } from "date-fns";

export default function JobsPage() {
    const [jobs, setJobs] = useState<JobProfile[]>([]);
    const [searchTerm, setSearchTerm] = useState("");
    const [isCreateOpen, setIsCreateOpen] = useState(false);

    // Form state
    const [newJobTitle, setNewJobTitle] = useState("");
    const [newJobDepartment, setNewJobDepartment] = useState("");
    const [newJobLocation, setNewJobLocation] = useState("");
    const [newJobDescription, setNewJobDescription] = useState("");

    useEffect(() => {
        // Load jobs on mount
        setJobs(JobService.getAll());
    }, []);

    const handleCreateJob = () => {
        if (!newJobTitle || !newJobDescription) return;

        const newJob = JobService.create({
            title: newJobTitle,
            department: newJobDepartment || "General",
            location: newJobLocation || "Remote",
            description: newJobDescription,
        });

        setJobs([newJob, ...jobs]);
        setIsCreateOpen(false);
        resetForm();
    };

    const handleDeleteJob = (id: string, e: React.MouseEvent) => {
        e.stopPropagation();
        if (confirm("Are you sure you want to delete this job profile?")) {
            JobService.delete(id);
            setJobs(jobs.filter(j => j.id !== id));
        }
    };

    const resetForm = () => {
        setNewJobTitle("");
        setNewJobDepartment("");
        setNewJobLocation("");
        setNewJobDescription("");
    };

    const filteredJobs = jobs.filter(job =>
        job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.department.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="h-screen flex flex-col bg-slate-50 dark:bg-slate-950 overflow-hidden">
            {/* Header */}
            <header className="flex-none h-16 border-b bg-white/50 dark:bg-slate-900/50 backdrop-blur-md z-10">
                <div className="h-full px-8 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Briefcase className="h-5 w-5 text-indigo-500" />
                        <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-500 to-purple-600 bg-clip-text text-transparent">
                            Job Hub
                        </h1>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 overflow-y-auto p-8">
                <div className="max-w-6xl mx-auto space-y-8">

                    {/* Toolbar */}
                    <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
                        <div className="relative w-full sm:w-96">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                            <Input
                                placeholder="Search active jobs..."
                                className="pl-10 bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 focus:ring-indigo-500"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>

                        <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
                            <DialogTrigger asChild>
                                <Button className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white shadow-lg shadow-indigo-500/25">
                                    <Plus className="mr-2 h-4 w-4" />
                                    Create Job Profile
                                </Button>
                            </DialogTrigger>
                            <DialogContent className="sm:max-w-[600px]">
                                <DialogHeader>
                                    <DialogTitle>Create New Job Profile</DialogTitle>
                                    <DialogDescription>
                                        Define a new role to match candidates against.
                                    </DialogDescription>
                                </DialogHeader>
                                <div className="grid gap-4 py-4">
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="space-y-2">
                                            <Label htmlFor="title">Job Title</Label>
                                            <Input id="title" placeholder="e.g. Senior Product Designer" value={newJobTitle} onChange={e => setNewJobTitle(e.target.value)} />
                                        </div>
                                        <div className="space-y-2">
                                            <Label htmlFor="dept">Department</Label>
                                            <Input id="dept" placeholder="e.g. Engineering" value={newJobDepartment} onChange={e => setNewJobDepartment(e.target.value)} />
                                        </div>
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="location">Location</Label>
                                        <Input id="location" placeholder="e.g. Remote, NY" value={newJobLocation} onChange={e => setNewJobLocation(e.target.value)} />
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="desc">Job Description</Label>
                                        <Textarea
                                            id="desc"
                                            placeholder="Paste the full job description here..."
                                            className="h-[200px] font-mono text-sm"
                                            value={newJobDescription}
                                            onChange={e => setNewJobDescription(e.target.value)}
                                        />
                                    </div>
                                </div>
                                <DialogFooter>
                                    <Button variant="outline" onClick={() => setIsCreateOpen(false)}>Cancel</Button>
                                    <Button onClick={handleCreateJob} disabled={!newJobTitle || !newJobDescription}>Create Profile</Button>
                                </DialogFooter>
                            </DialogContent>
                        </Dialog>
                    </div>

                    {/* Job Grid */}
                    {filteredJobs.length === 0 ? (
                        <div className="text-center py-20">
                            <div className="inline-flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-900 mb-4">
                                <Briefcase className="h-8 w-8 text-slate-400" />
                            </div>
                            <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100">No active jobs found</h3>
                            <p className="text-slate-500 dark:text-slate-400">Create a job profile to start matching candidates.</p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {filteredJobs.map((job) => (
                                <Card key={job.id} className="group hover:shadow-lg transition-all duration-200 border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
                                    <CardHeader>
                                        <div className="flex justify-between items-start">
                                            <div className="space-y-1">
                                                <CardTitle className="text-lg font-bold text-slate-900 dark:text-slate-50 group-hover:text-indigo-600 transition-colors">
                                                    {job.title}
                                                </CardTitle>
                                                <CardDescription className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
                                                    <span className="flex items-center gap-1">
                                                        <Briefcase className="h-3 w-3" /> {job.department}
                                                    </span>
                                                    <span>•</span>
                                                    <span className="flex items-center gap-1">
                                                        <MapPin className="h-3 w-3" /> {job.location}
                                                    </span>
                                                </CardDescription>
                                            </div>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-red-500 transition-opacity"
                                                onClick={(e) => handleDeleteJob(job.id, e)}
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    </CardHeader>
                                    <CardContent>
                                        <p className="text-sm text-slate-600 dark:text-slate-300 line-clamp-3 mb-4">
                                            {job.description}
                                        </p>
                                        <div className="flex items-center gap-2 text-xs text-slate-400">
                                            <Calendar className="h-3 w-3" />
                                            <span>Created {formatDistanceToNow(new Date(job.createdAt))} ago</span>
                                        </div>
                                    </CardContent>
                                    <CardFooter className="pt-0">
                                        <Button variant="outline" className="w-full text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 border-indigo-100">
                                            View Details
                                        </Button>
                                    </CardFooter>
                                </Card>
                            ))}
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}
