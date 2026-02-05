"use client";

import { useState, useCallback } from "react";
import { UploadCloud, File, X, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface DropzoneProps {
    onFileSelect: (file: File) => void;
}

export function Dropzone({ onFileSelect }: DropzoneProps) {
    const [isDragActive, setIsDragActive] = useState(false);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragActive(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragActive(false);
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            const file = e.dataTransfer.files[0];
            handleFile(file);
        }
    }, []);

    const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    }, []);

    const handleFile = (file: File) => {
        // Validate file type (PDF or DOCX)
        const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'];
        // For demo purposes, accepting all, but ideally we check type.

        setSelectedFile(file);
        onFileSelect(file);
    };

    const removeFile = (e: React.MouseEvent) => {
        e.stopPropagation();
        setSelectedFile(null);
    };

    return (
        <div
            className={cn(
                "relative border-2 border-dashed rounded-xl p-10 text-center transition-all cursor-pointer",
                isDragActive
                    ? "border-blue-500 bg-blue-50/50 scale-[1.02]"
                    : "border-slate-200 hover:border-slate-300 hover:bg-slate-50/50",
                selectedFile ? "bg-blue-50/30 border-blue-200" : ""
            )}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => document.getElementById("file-upload")?.click()}
        >
            <input
                id="file-upload"
                type="file"
                className="hidden"
                onChange={handleChange}
                accept=".pdf,.docx,.doc"
            />

            {selectedFile ? (
                <div className="flex flex-col items-center animate-in fade-in zoom-in duration-300">
                    <div className="h-16 w-16 bg-blue-100 rounded-full flex items-center justify-center mb-4 text-blue-600">
                        <CheckCircle2 className="h-8 w-8" />
                    </div>
                    <h3 className="text-lg font-medium text-slate-900 mb-1">File Selected</h3>
                    <p className="text-sm text-slate-500 mb-6">{selectedFile.name}</p>

                    <div className="flex items-center gap-2 text-xs text-slate-400">
                        <File className="h-3 w-3" />
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </div>

                    <button
                        onClick={removeFile}
                        className="absolute top-4 right-4 p-1 hover:bg-slate-200 rounded-full transition-colors"
                    >
                        <X className="h-4 w-4 text-slate-400" />
                    </button>
                </div>
            ) : (
                <div className="flex flex-col items-center">
                    <div className="h-16 w-16 bg-slate-100 rounded-full flex items-center justify-center mb-4 text-slate-400">
                        <UploadCloud className="h-8 w-8" />
                    </div>
                    <h3 className="text-lg font-medium text-slate-900 mb-1">
                        Click to upload or drag and drop
                    </h3>
                    <p className="text-sm text-slate-500 mb-6 max-w-sm mx-auto">
                        Support for PDF, DOCX, and TXT files. Maximum file size 10MB.
                    </p>
                    <div className="flex gap-4">
                        <div className="px-3 py-1 rounded bg-slate-100 text-xs font-medium text-slate-500">PDF</div>
                        <div className="px-3 py-1 rounded bg-slate-100 text-xs font-medium text-slate-500">DOCX</div>
                        <div className="px-3 py-1 rounded bg-slate-100 text-xs font-medium text-slate-500">TXT</div>
                    </div>
                </div>
            )}
        </div>
    );
}
