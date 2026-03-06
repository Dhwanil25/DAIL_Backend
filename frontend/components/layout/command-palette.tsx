"use client";

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Search,
    Briefcase,
    FileText,
    BookOpen,
    MessageSquare,
    BarChart3,
    LayoutDashboard,
} from 'lucide-react';
import { useRouter } from 'next/navigation';

export function CommandPalette() {
    const [isOpen, setIsOpen] = useState(false);
    const [query, setQuery] = useState('');
    const router = useRouter();

    useEffect(() => {
        const down = (e: KeyboardEvent) => {
            if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                setIsOpen((open) => !open);
            }
            if (e.key === 'Escape') {
                setIsOpen(false);
            }
        };
        document.addEventListener('keydown', down);
        return () => document.removeEventListener('keydown', down);
    }, []);

    const items = [
        { icon: LayoutDashboard, label: 'Dashboard', href: '/' },
        { icon: Briefcase, label: 'Cases', href: '/cases' },
        { icon: BookOpen, label: 'Dockets', href: '/dockets' },
        { icon: FileText, label: 'Documents', href: '/documents' },
        { icon: Search, label: 'Full-text Search', href: '/search' },
        { icon: MessageSquare, label: 'AI Assistant', href: '/ai' },
        { icon: BarChart3, label: 'Analytics', href: '/analytics' },
    ];

    const filtered = query
        ? items.filter(i => i.label.toLowerCase().includes(query.toLowerCase()))
        : items;

    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]">
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={() => setIsOpen(false)}
                    className="fixed inset-0 bg-navy-deep/60 backdrop-blur-sm"
                />

                <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: -20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: -20 }}
                    className="relative w-full max-w-lg overflow-hidden rounded-xl bg-navy-surface border border-white/10 shadow-2xl"
                >
                    <div className="flex items-center gap-3 px-4 py-3 border-b border-white/5 bg-white/[0.02]">
                        <Search className="h-4 w-4 text-zinc-500" />
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="What do you need?"
                            className="flex-1 bg-transparent text-[0.8rem] text-white placeholder-zinc-500 outline-none"
                            autoFocus
                        />
                        <kbd className="flex h-4 items-center gap-0.5 rounded border border-white/10 bg-white/5 px-1.5 font-mono text-[0.55rem] text-zinc-500">
                            ESC
                        </kbd>
                    </div>

                    <div className="p-2 max-h-[300px] overflow-y-auto">
                        <p className="px-3 py-1.5 text-[0.55rem] font-bold text-zinc-500 uppercase tracking-widest">Navigation</p>
                        <div className="space-y-0.5">
                            {filtered.map((item) => (
                                <button
                                    key={item.label}
                                    onClick={() => {
                                        router.push(item.href);
                                        setIsOpen(false);
                                        setQuery('');
                                    }}
                                    className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-[0.8rem] text-zinc-300 hover:bg-white/5 hover:text-teal-accent transition-all group"
                                >
                                    <item.icon className="h-3.5 w-3.5 text-zinc-500 group-hover:text-teal-accent" />
                                    <span>{item.label}</span>
                                </button>
                            ))}
                            {filtered.length === 0 && (
                                <p className="px-3 py-4 text-center text-[0.75rem] text-zinc-600">No results found</p>
                            )}
                        </div>
                    </div>

                    <div className="px-4 py-2 bg-white/[0.02] border-t border-white/5 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="flex items-center gap-1 text-[0.55rem] text-zinc-500">
                                <kbd className="rounded bg-white/5 px-1 border border-white/10">⏎</kbd>
                                <span>Select</span>
                            </div>
                            <div className="flex items-center gap-1 text-[0.55rem] text-zinc-500">
                                <kbd className="rounded bg-white/5 px-1 border border-white/10">↑↓</kbd>
                                <span>Navigate</span>
                            </div>
                        </div>
                        <p className="text-[0.55rem] text-zinc-600 font-medium italic">LIA Search v1.0</p>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
}
