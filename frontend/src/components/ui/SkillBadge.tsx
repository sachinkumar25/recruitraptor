"use client";

import { cn } from "@/lib/utils";
import { CheckCircle2, Code2, FileText, Linkedin, HelpCircle } from "lucide-react";

type VerificationSource = "github" | "linkedin" | "resume" | "unverified";

interface SkillBadgeProps {
    skill: string;
    source?: VerificationSource;
    proficiency?: "beginner" | "intermediate" | "advanced" | "expert";
    showIcon?: boolean;
    size?: "sm" | "md" | "lg";
    className?: string;
}

const sourceConfig = {
    github: {
        icon: Code2,
        color: "bg-emerald-100 text-emerald-700 border-emerald-200 dark:bg-emerald-900/30 dark:text-emerald-400 dark:border-emerald-800",
        tooltip: "Verified via GitHub code analysis",
    },
    linkedin: {
        icon: Linkedin,
        color: "bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-800",
        tooltip: "Listed on LinkedIn profile",
    },
    resume: {
        icon: FileText,
        color: "bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700",
        tooltip: "Claimed on resume",
    },
    unverified: {
        icon: HelpCircle,
        color: "bg-slate-50 text-slate-500 border-slate-200 dark:bg-slate-900 dark:text-slate-500 dark:border-slate-800",
        tooltip: "Not yet verified",
    },
};

const sizeConfig = {
    sm: "text-xs px-2 py-0.5 gap-1",
    md: "text-sm px-2.5 py-1 gap-1.5",
    lg: "text-base px-3 py-1.5 gap-2",
};

const iconSizeConfig = {
    sm: "h-3 w-3",
    md: "h-3.5 w-3.5",
    lg: "h-4 w-4",
};

export function SkillBadge({
    skill,
    source = "resume",
    proficiency,
    showIcon = true,
    size = "md",
    className,
}: SkillBadgeProps) {
    const config = sourceConfig[source];
    const Icon = config.icon;

    return (
        <span
            className={cn(
                "inline-flex items-center rounded-full border font-medium transition-all duration-200",
                "hover:scale-105 hover:shadow-sm cursor-default",
                sizeConfig[size],
                config.color,
                className
            )}
            title={config.tooltip}
        >
            {showIcon && source === "github" && (
                <CheckCircle2 className={cn(iconSizeConfig[size], "text-emerald-600 dark:text-emerald-400")} />
            )}
            {showIcon && source !== "github" && (
                <Icon className={cn(iconSizeConfig[size], "opacity-60")} />
            )}
            {skill}
            {proficiency && (
                <span className="ml-1 opacity-60 text-xs">
                    ({proficiency})
                </span>
            )}
        </span>
    );
}

// Compound component for skill groups
interface SkillBadgeGroupProps {
    skills: Array<{
        name: string;
        source?: VerificationSource;
        proficiency?: "beginner" | "intermediate" | "advanced" | "expert";
    }>;
    size?: "sm" | "md" | "lg";
    maxDisplay?: number;
    className?: string;
}

export function SkillBadgeGroup({
    skills,
    size = "md",
    maxDisplay = 5,
    className,
}: SkillBadgeGroupProps) {
    const displaySkills = skills.slice(0, maxDisplay);
    const remainingCount = skills.length - maxDisplay;

    return (
        <div className={cn("flex flex-wrap gap-2", className)}>
            {displaySkills.map((skill) => (
                <SkillBadge
                    key={skill.name}
                    skill={skill.name}
                    source={skill.source}
                    proficiency={skill.proficiency}
                    size={size}
                />
            ))}
            {remainingCount > 0 && (
                <span
                    className={cn(
                        "inline-flex items-center rounded-full border font-medium",
                        "bg-slate-100 text-slate-600 border-slate-200",
                        "dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700",
                        sizeConfig[size]
                    )}
                >
                    +{remainingCount} more
                </span>
            )}
        </div>
    );
}
