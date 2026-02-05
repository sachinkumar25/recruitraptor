"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
    LayoutDashboard,
    Users,
    Upload,
    Settings,
    ShieldCheck,
    LogOut
} from "lucide-react";
import { Button } from "@/components/ui/button";

const navItems = [
    {
        title: "Dashboard",
        href: "/",
        icon: LayoutDashboard,
    },
    {
        title: "Candidates",
        href: "/candidates",
        icon: Users,
    },
    {
        title: "Upload Resume",
        href: "/upload",
        icon: Upload,
    },
    {
        title: "Settings",
        href: "/settings",
        icon: Settings,
    },
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <div className="flex flex-col h-screen w-64 bg-slate-950 text-white border-r border-slate-800">
            {/* Logo Area */}
            <div className="p-6">
                <div className="flex items-center gap-2">
                    <div className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center">
                        <ShieldCheck className="h-5 w-5 text-white" />
                    </div>
                    <h1 className="text-xl font-bold tracking-tight text-white">
                        RecruitRaptor
                    </h1>
                </div>
            </div>

            {/* Navigation */}
            <div className="flex-1 px-3 py-4 space-y-1">
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                                isActive
                                    ? "bg-blue-600 text-white"
                                    : "text-slate-400 hover:text-white hover:bg-slate-900"
                            )}
                        >
                            <item.icon className="h-5 w-5" />
                            {item.title}
                        </Link>
                    );
                })}
            </div>

            {/* User Profile / Footer */}
            <div className="p-4 border-t border-slate-900">
                <div className="flex items-center gap-3 mb-4 px-2">
                    <div className="h-9 w-9 rounded-full bg-slate-800 flex items-center justify-center text-xs font-bold text-slate-300">
                        SC
                    </div>
                    <div className="flex-1 overflow-hidden">
                        <p className="text-sm font-medium text-white truncate">Sachin C.</p>
                        <p className="text-xs text-slate-500 truncate">Admin</p>
                    </div>
                </div>
                <Button variant="ghost" className="w-full justify-start text-slate-400 hover:text-white hover:bg-slate-900 gap-2">
                    <LogOut className="h-4 w-4" />
                    Sign Out
                </Button>
            </div>
        </div>
    );
}
