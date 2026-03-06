"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    LayoutDashboard,
    Briefcase,
    BookOpen,
    FileText,
    Search,
    MessageSquare,
    BarChart3,
    Shield,
    HelpCircle,
    X,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';
import { useMobileNav } from './mobile-nav-context';



const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Cases', href: '/cases', icon: Briefcase },
    { name: 'Dockets', href: '/dockets', icon: BookOpen },
    { name: 'Documents', href: '/documents', icon: FileText },
    { name: 'Secondary Sources', href: '/sources', icon: FileText },
    { name: 'Search', href: '/search', icon: Search },
    { name: 'AI Assistant', href: '/ai', icon: MessageSquare },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
];

export function Sidebar() {
    const pathname = usePathname();
    const { isOpen, setIsOpen } = useMobileNav();

    const SidebarContent = () => (
        <div className="flex h-full w-[220px] flex-col bg-navy-deep border-r border-white/5">
            <div className="flex h-14 items-center justify-between px-4">
                <div className="flex items-center gap-2.5">
                    <div className="flex h-7 w-7 items-center justify-center rounded-md bg-teal-accent/10 border border-teal-accent/20">
                        <Shield className="h-4 w-4 text-teal-accent" />
                    </div>
                    <div>
                        <span className="text-base font-bold tracking-tight text-white">LIA</span>
                        <p className="text-[0.5rem] text-zinc-500 font-medium uppercase tracking-widest -mt-0.5">Legal Intelligence</p>
                    </div>
                </div>
                <button onClick={() => setIsOpen(false)} className="lg:hidden p-1.5 text-zinc-500 hover:text-white transition-colors">
                    <X className="h-4 w-4" />
                </button>
            </div>

            <nav className="flex-1 space-y-0.5 px-3 py-3 overflow-y-auto">
                {navigation.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.name}
                            href={item.href}
                            onClick={() => setIsOpen(false)}
                            className={cn(
                                "group relative flex items-center gap-2.5 rounded-lg px-3 py-2 text-[0.8rem] font-medium transition-all duration-200",
                                isActive
                                    ? "bg-teal-accent/5 text-teal-accent"
                                    : "text-zinc-400 hover:bg-white/5 hover:text-white"
                            )}
                        >
                            {isActive && (
                                <motion.div
                                    layoutId="sidebar-glow"
                                    className="absolute inset-0 rounded-lg bg-teal-accent/5 ring-1 ring-teal-accent/20"
                                    transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                                />
                            )}
                            <item.icon className={cn(
                                "h-4 w-4 shrink-0 transition-colors duration-200",
                                isActive ? "text-teal-accent" : "text-zinc-500 group-hover:text-zinc-300"
                            )} />
                            <span className="relative">{item.name}</span>
                        </Link>
                    );
                })}
            </nav>

            <div className="p-3 mt-auto border-t border-white/5">
                <Link
                    href="/help"
                    className="flex items-center gap-2.5 px-3 py-2 text-[0.8rem] font-medium text-zinc-400 hover:text-white transition-colors rounded-lg hover:bg-white/5"
                >
                    <HelpCircle className="h-4 w-4" />
                    <span>Help &amp; Docs</span>
                </Link>
                <p className="px-3 mt-1 text-[0.5rem] text-zinc-600 font-medium uppercase tracking-widest">
                    Open Source • API v1
                </p>
            </div>
        </div>
    );

    return (
        <>
            {/* Desktop Sidebar */}
            <div className="hidden lg:block h-full">
                <SidebarContent />
            </div>

            {/* Mobile Sidebar */}
            <AnimatePresence>
                {isOpen && (
                    <>
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setIsOpen(false)}
                            className="fixed inset-0 z-40 bg-navy-deep/80 backdrop-blur-sm lg:hidden"
                        />
                        <motion.div
                            initial={{ x: "-100%" }}
                            animate={{ x: 0 }}
                            exit={{ x: "-100%" }}
                            transition={{ type: "spring", bounce: 0, duration: 0.4 }}
                            className="fixed inset-y-0 left-0 z-50 lg:hidden"
                        >
                            <SidebarContent />
                        </motion.div>
                    </>
                )}
            </AnimatePresence>
        </>
    );
}

