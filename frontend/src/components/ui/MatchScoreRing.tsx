"use client";

import { cn } from "@/lib/utils";
import { Info } from "lucide-react";
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip";

interface MatchScoreRingProps {
    score: number; // 0-100
    size?: "sm" | "md" | "lg" | "xl";
    showLabel?: boolean;
    className?: string;
}

const sizeConfig = {
    sm: { width: 48, strokeWidth: 4, fontSize: "text-xs" },
    md: { width: 72, strokeWidth: 5, fontSize: "text-lg" },
    lg: { width: 96, strokeWidth: 6, fontSize: "text-2xl" },
    xl: { width: 128, strokeWidth: 8, fontSize: "text-3xl" },
};

export function MatchScoreRing({
    score,
    size = "md",
    showLabel = true,
    className,
}: MatchScoreRingProps) {
    const { width, strokeWidth, fontSize } = sizeConfig[size];
    const radius = (width - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (score / 100) * circumference;

    // Gradient IDs based on score
    const gradientId = score >= 90 ? "gradient-emerald" :
        score >= 75 ? "gradient-blue" :
            score >= 50 ? "gradient-amber" : "gradient-red";

    return (
        <div className={cn("relative inline-flex items-center justify-center group", className)}>
            <svg
                width={width}
                height={width}
                className="transform -rotate-90"
            >
                <defs>
                    <linearGradient id="gradient-emerald" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#34d399" /> {/* emerald-400 */}
                        <stop offset="100%" stopColor="#059669" /> {/* emerald-600 */}
                    </linearGradient>
                    <linearGradient id="gradient-blue" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#60a5fa" /> {/* blue-400 */}
                        <stop offset="100%" stopColor="#2563eb" /> {/* blue-600 */}
                    </linearGradient>
                    <linearGradient id="gradient-amber" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#fbbf24" /> {/* amber-400 */}
                        <stop offset="100%" stopColor="#d97706" /> {/* amber-600 */}
                    </linearGradient>
                    <linearGradient id="gradient-red" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#f87171" /> {/* red-400 */}
                        <stop offset="100%" stopColor="#dc2626" /> {/* red-600 */}
                    </linearGradient>
                </defs>

                {/* Background circle */}
                <circle
                    cx={width / 2}
                    cy={width / 2}
                    r={radius}
                    fill="none"
                    stroke="currentColor"
                    strokeWidth={strokeWidth}
                    className="text-slate-100 dark:text-slate-800"
                />
                {/* Score circle */}
                <circle
                    cx={width / 2}
                    cy={width / 2}
                    r={radius}
                    fill="none"
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    stroke={`url(#${gradientId})`}
                    className="transition-all duration-1000 ease-out"
                    style={{
                        "--score-offset": offset,
                    } as React.CSSProperties}
                />
            </svg>
            {showLabel && (
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                    <span className={cn("font-bold text-slate-900 dark:text-white", fontSize)}>
                        {score}%
                    </span>
                </div>
            )}

            {/* Info Tooltip Trigger (Only for larger sizes) */}
            {(size === 'lg' || size === 'xl') && (
                <div className="absolute -top-1 -right-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <TooltipProvider>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <div className="bg-white dark:bg-slate-800 rounded-full p-0.5 shadow-sm border border-slate-200 dark:border-slate-700 cursor-help">
                                    <Info className="h-3 w-3 text-muted-foreground" />
                                </div>
                            </TooltipTrigger>
                            <TooltipContent side="top" className="max-w-[200px] text-xs">
                                <p>Holistic match score based on technical skills, experience, and job requirements.</p>
                            </TooltipContent>
                        </Tooltip>
                    </TooltipProvider>
                </div>
            )}
        </div>
    );
}
