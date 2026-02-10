import { useState } from "react";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription, SheetFooter } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { X } from "lucide-react";

export interface FilterState {
    minScore: number;
    sources: {
        github: boolean;
        linkedin: boolean;
        resume: boolean;
    };
    skills: string[];
}

export const initialFilterState: FilterState = {
    minScore: 0,
    sources: {
        github: true,
        linkedin: true,
        resume: true
    },
    skills: []
};

interface AdvancedFilterPanelProps {
    isOpen: boolean;
    onClose: () => void;
    filters: FilterState;
    onFilterChange: (filters: FilterState) => void;
    onClearFilters: () => void;
}

export function AdvancedFilterPanel({
    isOpen,
    onClose,
    filters,
    onFilterChange,
    onClearFilters
}: AdvancedFilterPanelProps) {
    const [skillInput, setSkillInput] = useState("");

    const handleSourceChange = (source: keyof FilterState["sources"]) => {
        onFilterChange({
            ...filters,
            sources: {
                ...filters.sources,
                [source]: !filters.sources[source]
            }
        });
    };

    const handleScoreChange = (value: number[]) => {
        onFilterChange({
            ...filters,
            minScore: value[0]
        });
    };

    const handleAddSkill = () => {
        if (skillInput.trim() && !filters.skills.includes(skillInput.trim())) {
            onFilterChange({
                ...filters,
                skills: [...filters.skills, skillInput.trim()]
            });
            setSkillInput("");
        }
    };

    const handleRemoveSkill = (skill: string) => {
        onFilterChange({
            ...filters,
            skills: filters.skills.filter(s => s !== skill)
        });
    };

    return (
        <Sheet open={isOpen} onOpenChange={onClose}>
            <SheetContent className="w-[400px] sm:w-[540px] overflow-y-auto">
                <SheetHeader>
                    <SheetTitle>Advanced Filters</SheetTitle>
                    <SheetDescription>
                        Refine your candidate search with precise criteria.
                    </SheetDescription>
                </SheetHeader>

                <div className="py-6 space-y-8">
                    {/* Minimum Match Score */}
                    <div className="space-y-4">
                        <div className="flex justify-between items-center">
                            <Label className="text-base font-medium">Minimum Match Score</Label>
                            <span className="text-sm font-medium text-indigo-600 bg-indigo-50 px-2 py-1 rounded">
                                {filters.minScore}%
                            </span>
                        </div>
                        <Slider
                            defaultValue={[filters.minScore]}
                            max={100}
                            step={1}
                            onValueChange={handleScoreChange}
                            className="w-full"
                        />
                        <div className="flex justify-between text-xs text-muted-foreground px-1">
                            <span>0%</span>
                            <span>50%</span>
                            <span>100%</span>
                        </div>
                    </div>

                    {/* Data Sources */}
                    <div className="space-y-4">
                        <Label className="text-base font-medium">Data Sources</Label>
                        <div className="grid gap-3">
                            <div className="flex items-center space-x-2">
                                <Checkbox
                                    id="github"
                                    checked={filters.sources.github}
                                    onCheckedChange={() => handleSourceChange("github")}
                                />
                                <Label htmlFor="github" className="font-normal cursor-pointer">
                                    GitHub Profile
                                </Label>
                            </div>
                            <div className="flex items-center space-x-2">
                                <Checkbox
                                    id="linkedin"
                                    checked={filters.sources.linkedin}
                                    onCheckedChange={() => handleSourceChange("linkedin")}
                                />
                                <Label htmlFor="linkedin" className="font-normal cursor-pointer">
                                    LinkedIn Profile
                                </Label>
                            </div>
                            <div className="flex items-center space-x-2">
                                <Checkbox
                                    id="resume"
                                    checked={filters.sources.resume}
                                    onCheckedChange={() => handleSourceChange("resume")}
                                />
                                <Label htmlFor="resume" className="font-normal cursor-pointer">
                                    Resume Data
                                </Label>
                            </div>
                        </div>
                    </div>

                    {/* Required Skills */}
                    <div className="space-y-4">
                        <Label className="text-base font-medium">Must Have Skills</Label>
                        <div className="flex gap-2">
                            <Input
                                placeholder="e.g. React, Python..."
                                value={skillInput}
                                onChange={(e) => setSkillInput(e.target.value)}
                                onKeyDown={(e) => e.key === "Enter" && handleAddSkill()}
                            />
                            <Button onClick={handleAddSkill} size="sm">Add</Button>
                        </div>

                        {filters.skills.length > 0 && (
                            <div className="flex flex-wrap gap-2 mt-3 p-3 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-100 dark:border-slate-800">
                                {filters.skills.map(skill => (
                                    <Badge key={skill} variant="secondary" className="gap-1 pl-2 pr-1 py-1">
                                        {skill}
                                        <button
                                            onClick={() => handleRemoveSkill(skill)}
                                            className="ml-1 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-full p-0.5 transition-colors"
                                        >
                                            <X className="h-3 w-3" />
                                        </button>
                                    </Badge>
                                ))}
                            </div>
                        )}
                        <p className="text-xs text-muted-foreground">
                            Candidates must match ALL selected skills.
                        </p>
                    </div>
                </div>

                <SheetFooter className="flex-col sm:flex-row gap-3 sm:gap-2">
                    <Button variant="outline" onClick={onClearFilters} className="w-full sm:w-auto">
                        Clear Filters
                    </Button>
                    <Button onClick={onClose} className="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-700">
                        View Results
                    </Button>
                </SheetFooter>
            </SheetContent>
        </Sheet>
    );
}
