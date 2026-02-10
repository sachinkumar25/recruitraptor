"use client";

import { useState } from "react";
import { Dropzone } from "@/components/upload/Dropzone";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
    Loader2,
    CheckCircle2,
    Search,
    FileText,
    BrainCircuit,
    PenTool,
    ChevronRight,
    Play,
    AlertCircle
} from "lucide-react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { RecruitRaptorApi } from "@/lib/api";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

// Pipeline Stages
const PIPELINE_STAGES = [
    { id: 'extract', label: 'Extracting Text', icon: FileText, desc: 'Parsing PDF structure and raw text...' },
    { id: 'enrich', label: 'Enriching Profile', icon: Search, desc: 'Searching GitHub/LinkedIn for data...' },
    { id: 'analyze', label: 'Analyzing Skills', icon: BrainCircuit, desc: 'Verifying skills and detecting gaps...' },
    { id: 'narrative', label: 'Generating Narrative', icon: PenTool, desc: 'Synthesizing final candidate summary...' },
];

export default function UploadPage() {
    const router = useRouter();
    const [file, setFile] = useState<File | null>(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [currentStage, setCurrentStage] = useState(0);
    const [completed, setCompleted] = useState(false);
    const [candidateId, setCandidateId] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const startProcessing = async () => {
        if (!file) return;
        setIsProcessing(true);
        setCurrentStage(0);
        setError(null);

        try {
            // Stage 1: Extraction (Parsing)
            setCurrentStage(0); // Extracting Text
            const parsedData = await RecruitRaptorApi.parseResume(file);

            // Stage 2: Enriching (Discovery)
            setCurrentStage(1);
            // Small delay for UI feedback
            await new Promise(resolve => setTimeout(resolve, 800));
            const discoveryResult = await RecruitRaptorApi.discoverProfiles(parsedData);

            // Stage 3: Analyzing (Enrichment)
            setCurrentStage(2);
            await new Promise(resolve => setTimeout(resolve, 800));
            const enrichedProfile = await RecruitRaptorApi.enrichProfile(parsedData, discoveryResult);

            // Stage 4: Narrative
            setCurrentStage(3);
            await new Promise(resolve => setTimeout(resolve, 800));
            // Generate bio to complete the pipeline visually
            await RecruitRaptorApi.generateBioNarrative(enrichedProfile);

            // Success!
            setCurrentStage(PIPELINE_STAGES.length); // All stages complete
            setCompleted(true);
            setCandidateId(enrichedProfile.candidate_id);

        } catch (err) {
            console.error("Upload failed", err);
            setError(err instanceof Error ? err.message : "An unexpected error occurred processing the resume.");
            setIsProcessing(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            <div>
                <h1 className="text-3xl font-bold tracking-tight text-slate-900">Upload Resume</h1>
                <p className="text-slate-500 mt-1">Upload a candidate's resume to start the AI analysis pipeline.</p>
            </div>

            <div className="grid gap-8 md:grid-cols-3">
                {/* Left Col: Upload Area */}
                <div className="md:col-span-2 space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Select Document</CardTitle>
                            <CardDescription>Drag and drop or browse to upload (PDF, DOCX, TXT).</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <Dropzone onFileSelect={setFile} />

                            {error && (
                                <Alert variant="destructive" className="mt-4">
                                    <AlertCircle className="h-4 w-4" />
                                    <AlertTitle>Error</AlertTitle>
                                    <AlertDescription>{error}</AlertDescription>
                                </Alert>
                            )}

                            <div className="mt-6 flex justify-end">
                                <Button
                                    size="lg"
                                    onClick={startProcessing}
                                    disabled={!file || isProcessing || completed}
                                    className="w-full sm:w-auto"
                                >
                                    {isProcessing ? (
                                        <>
                                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                            Processing...
                                        </>
                                    ) : completed ? (
                                        <>
                                            <CheckCircle2 className="mr-2 h-4 w-4" />
                                            Analysis Complete
                                        </>
                                    ) : (
                                        <>
                                            <Play className="mr-2 h-4 w-4" />
                                            Start Analysis
                                        </>
                                    )}
                                </Button>
                            </div>
                        </CardContent>
                    </Card>

                    {completed && candidateId && (
                        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="h-10 w-10 bg-green-100 rounded-full flex items-center justify-center text-green-600">
                                        <CheckCircle2 className="h-6 w-6" />
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-green-800">Candidate Processed Successfully</h3>
                                        <p className="text-green-600 text-sm">Profile enriched and narrative generated.</p>
                                    </div>
                                </div>
                                <Button onClick={() => router.push(`/candidates/${candidateId}`)}>
                                    View Profile <ChevronRight className="ml-2 h-4 w-4" />
                                </Button>
                            </div>
                        </div>
                    )}
                </div>

                {/* Right Col: Progress Pipeline */}
                <div>
                    <h3 className="font-semibold text-slate-900 mb-4 px-1">Pipeline Status</h3>
                    <div className="relative space-y-8 before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-200 before:to-transparent">

                        {PIPELINE_STAGES.map((stage, index) => {
                            const isCompleted = currentStage > index || completed;
                            const isActive = currentStage === index && isProcessing;
                            // const isPending = currentStage < index && !completed;

                            return (
                                <div key={stage.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                                    {/* Icon Marker */}
                                    <div className={cn(
                                        "flex items-center justify-center w-10 h-10 rounded-full border-2 shrink-0 z-10 transition-colors duration-300",
                                        isCompleted ? "bg-green-100 border-green-500 text-green-600" :
                                            isActive ? "bg-blue-100 border-blue-500 text-blue-600 animate-pulse" :
                                                "bg-white border-slate-200 text-slate-300"
                                    )}>
                                        {isCompleted ? <CheckCircle2 className="w-5 h-5" /> : <stage.icon className="w-5 h-5" />}
                                    </div>

                                    {/* Content */}
                                    <div className="ml-4 w-full">
                                        <h4 className={cn(
                                            "font-semibold text-sm transition-colors",
                                            isCompleted || isActive ? "text-slate-900" : "text-slate-400"
                                        )}>{stage.label}</h4>
                                        <p className="text-xs text-slate-500">{stage.desc}</p>
                                    </div>
                                </div>
                            );
                        })}

                    </div>

                    {!isProcessing && !completed && (
                        <div className="mt-8 p-4 bg-slate-50 rounded-lg border border-slate-200 text-xs text-slate-500 text-center">
                            Upload a resume to see the AI pipeline in action.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
