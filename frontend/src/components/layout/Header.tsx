"use client";

import { usePathname } from "next/navigation";
import { Search, Bell, ChevronRight, Home, Command, Plus } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import Link from "next/link";

export function Header() {
    const pathname = usePathname();

    // Simple breadcrumb logic
    const segments = pathname.split('/').filter(Boolean);
    const breadcrumbs = [
        { title: "Home", href: "/" },
        ...segments.map((segment, index) => ({
            title: segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' '),
            href: `/${segments.slice(0, index + 1).join('/')}`
        }))
    ];

    return (
        <header className="h-16 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-950/80 backdrop-blur-sm flex items-center justify-between px-6 sticky top-0 z-10">
            {/* Breadcrumbs */}
            <nav className="flex items-center text-sm text-muted-foreground gap-1">
                {breadcrumbs.map((item, index) => (
                    <div key={item.href} className="flex items-center gap-1">
                        {index > 0 && <ChevronRight className="h-4 w-4 text-slate-300 dark:text-slate-600" />}
                        {index === 0 ? (
                            <Link
                                href={item.href}
                                className="flex items-center gap-1 hover:text-foreground transition-colors"
                            >
                                <Home className="h-4 w-4" />
                            </Link>
                        ) : (
                            <Link
                                href={item.href}
                                className={
                                    index === breadcrumbs.length - 1
                                        ? "font-medium text-foreground"
                                        : "hover:text-foreground transition-colors"
                                }
                            >
                                {item.title}
                            </Link>
                        )}
                    </div>
                ))}
            </nav>

            {/* Right Actions */}
            <div className="flex items-center gap-3">
                {/* Search with Command Palette Hint */}
                <div className="relative w-64 hidden md:block group">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                        type="search"
                        placeholder="Search candidates..."
                        className="pl-9 pr-12 h-9 bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                    />
                    <kbd className="absolute right-3 top-1/2 -translate-y-1/2 hidden md:inline-flex items-center gap-0.5 rounded border border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 text-[10px] font-medium text-slate-500 dark:text-slate-400">
                        <Command className="h-3 w-3" />K
                    </kbd>
                </div>

                {/* Quick Upload Button */}
                <Link href="/upload">
                    <Button
                        size="sm"
                        className="hidden sm:flex gap-1.5 bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white shadow-lg shadow-indigo-500/25 rounded-lg"
                    >
                        <Plus className="h-4 w-4" />
                        Upload
                    </Button>
                </Link>

                <Separator orientation="vertical" className="h-6 bg-slate-200 dark:bg-slate-700" />

                {/* Notifications */}
                <Button
                    variant="ghost"
                    size="icon"
                    className="relative text-muted-foreground hover:text-foreground hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg"
                >
                    <Bell className="h-5 w-5" />
                    <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-red-500 ring-2 ring-white dark:ring-slate-950 animate-pulse" />
                </Button>
            </div>
        </header>
    );
}
