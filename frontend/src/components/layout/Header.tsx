"use client";

import { usePathname } from "next/navigation";
import { Search, Bell, ChevronRight, Home } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";

export function Header() {
    const pathname = usePathname();

    // Simple breadcrumb logic
    const segments = pathname.split('/').filter(Boolean);
    const breadcrumbs = [
        { title: "Home", href: "/" },
        ...segments.map((segment, index) => ({
            title: segment.charAt(0).toUpperCase() + segment.slice(1),
            href: `/${segments.slice(0, index + 1).join('/')}`
        }))
    ];

    return (
        <header className="h-16 border-b bg-white flex items-center justify-between px-6 sticky top-0 z-10">
            {/* Breadcrumbs */}
            <div className="flex items-center text-sm text-muted-foreground gap-2">
                {breadcrumbs.map((item, index) => (
                    <div key={item.href} className="flex items-center gap-2">
                        {index > 0 && <ChevronRight className="h-4 w-4" />}
                        {index === 0 ? <Home className="h-4 w-4" /> : null}
                        <span className={index === breadcrumbs.length - 1 ? "font-medium text-foreground" : ""}>
                            {item.title}
                        </span>
                    </div>
                ))}
            </div>

            {/* Right Actions */}
            <div className="flex items-center gap-4">
                <div className="relative w-64 hidden md:block">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                        type="search"
                        placeholder="Search candidates..."
                        className="pl-9 h-9 bg-slate-50 border-slate-200"
                    />
                </div>
                <Separator orientation="vertical" className="h-6" />
                <Button variant="ghost" size="icon" className="relative text-muted-foreground hover:text-foreground">
                    <Bell className="h-5 w-5" />
                    <span className="absolute top-2 right-2 h-2 w-2 rounded-full bg-red-500 ring-2 ring-white"></span>
                </Button>
            </div>
        </header>
    );
}
