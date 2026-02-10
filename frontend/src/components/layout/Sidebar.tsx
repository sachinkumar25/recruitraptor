"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
    LayoutDashboard,
    Users,
    Upload,
    Settings,
    LogOut,
    ChevronLeft,
    Sparkles,
    Briefcase,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";

const navItems = [
    {
        title: "Dashboard",
        href: "/",
        icon: LayoutDashboard,
        badge: null,
    },
    {
        title: "Candidates",
        href: "/candidates",
        icon: Users,
        badge: null, // Could be dynamic: "3 new"
    },
    {
        title: "Upload Resume",
        href: "/upload",
        icon: Upload,
        badge: null,
    },
    {
        title: "Jobs",
        href: "/jobs",
        icon: Briefcase,
        badge: null,
    },
    {
        title: "Settings",
        href: "/settings",
        icon: Settings,
        badge: null,
    },
];

export function Sidebar() {
    const pathname = usePathname();
    const [collapsed, setCollapsed] = useState(false);

    return (
        <div
            className={cn(
                "flex flex-col h-screen bg-gradient-to-b from-slate-950 to-slate-900 text-white border-r border-slate-800/50 transition-all duration-300 ease-out-expo",
                collapsed ? "w-20" : "w-64"
            )}
        >
            {/* Logo Area */}
            <div className="p-6 relative">
                <div className="flex items-center gap-3">
                    {/* Animated Logo */}
                    <div className="relative">
                        <div className="absolute inset-0 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl blur-lg opacity-50 animate-pulse-glow" />
                        <div className="relative h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg">
                            <Sparkles className="h-5 w-5 text-white" />
                        </div>
                    </div>
                    {!collapsed && (
                        <div className="overflow-hidden">
                            <h1 className="text-xl font-bold tracking-tight text-white whitespace-nowrap">
                                RecruitRaptor
                            </h1>
                            <p className="text-xs text-slate-500">AI-Powered Hiring</p>
                        </div>
                    )}
                </div>

                {/* Collapse Toggle */}
                <button
                    onClick={() => setCollapsed(!collapsed)}
                    className={cn(
                        "absolute -right-3 top-8 h-6 w-6 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-700 transition-all duration-200 shadow-lg",
                        collapsed && "rotate-180"
                    )}
                >
                    <ChevronLeft className="h-3 w-3" />
                </button>
            </div>

            {/* Navigation */}
            <div className="flex-1 px-3 py-4 space-y-1">
                {navItems.map((item) => {
                    const isActive = pathname === item.href ||
                        (item.href !== "/" && pathname.startsWith(item.href));
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200",
                                "hover:translate-x-1",
                                isActive
                                    ? "bg-gradient-to-r from-indigo-600 to-indigo-500 text-white shadow-lg shadow-indigo-500/25"
                                    : "text-slate-400 hover:text-white hover:bg-slate-800/50"
                            )}
                        >
                            <item.icon className={cn(
                                "h-5 w-5 transition-transform duration-200",
                                isActive && "scale-110"
                            )} />
                            {!collapsed && (
                                <>
                                    <span className="flex-1">{item.title}</span>
                                    {item.badge && (
                                        <span className="px-2 py-0.5 text-xs rounded-full bg-indigo-500/20 text-indigo-300">
                                            {item.badge}
                                        </span>
                                    )}
                                </>
                            )}
                        </Link>
                    );
                })}
            </div>

            {/* User Profile / Footer */}
            <div className="p-4 border-t border-slate-800/50">
                <div className={cn(
                    "flex items-center gap-3 mb-4 px-2",
                    collapsed && "justify-center"
                )}>
                    <div className="relative">
                        <div className="h-9 w-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-xs font-bold text-white shadow-lg">
                            SC
                        </div>
                        <div className="absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full bg-emerald-500 border-2 border-slate-950" />
                    </div>
                    {!collapsed && (
                        <div className="flex-1 overflow-hidden">
                            <p className="text-sm font-medium text-white truncate">Sachin C.</p>
                            <p className="text-xs text-slate-500 truncate">Admin</p>
                        </div>
                    )}
                </div>
                {!collapsed && (
                    <Button
                        variant="ghost"
                        className="w-full justify-start text-slate-400 hover:text-white hover:bg-slate-800/50 gap-2 rounded-xl"
                    >
                        <LogOut className="h-4 w-4" />
                        Sign Out
                    </Button>
                )}
            </div>
        </div>
    );
}
