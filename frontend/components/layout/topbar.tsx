"use client";

import { useState, useRef, useEffect } from 'react';
import { Search, Bell, Plus, Github, Command, Menu, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useMobileNav } from './mobile-nav-context';
import { useRouter } from 'next/navigation';
import { AnimatePresence, motion } from 'framer-motion';

export function TopBar() {
    const { setIsOpen } = useMobileNav();
    const router = useRouter();
    const [searchValue, setSearchValue] = useState('');
    const [showNotifications, setShowNotifications] = useState(false);
    const notifRef = useRef<HTMLDivElement>(null);

    // Close dropdown on outside click
    useEffect(() => {
        function handleClickOutside(e: MouseEvent) {
            if (notifRef.current && !notifRef.current.contains(e.target as Node)) {
                setShowNotifications(false);
            }
        }
        if (showNotifications) {
            document.addEventListener('mousedown', handleClickOutside);
            return () => document.removeEventListener('mousedown', handleClickOutside);
        }
    }, [showNotifications]);

    function handleSearch(e: React.FormEvent) {
        e.preventDefault();
        if (searchValue.trim()) {
            router.push(`/search?q=${encodeURIComponent(searchValue.trim())}`);
            setSearchValue('');
        } else {
            router.push('/search');
        }
    }

    return (
        <header className="flex h-14 items-center justify-between border-b border-white/5 bg-navy-deep px-3 md:px-6 sticky top-0 z-30 gap-2">
            {/* Mobile hamburger */}
            <button
                onClick={() => setIsOpen(true)}
                className="lg:hidden p-2 text-zinc-500 hover:text-white transition-colors shrink-0"
            >
                <Menu className="h-5 w-5" />
            </button>

            {/* Search */}
            <form onSubmit={handleSearch} className="flex-1 max-w-md">
                <div className="group relative">
                    <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                        <Search className="h-3.5 w-3.5 text-zinc-500 group-focus-within:text-teal-accent transition-colors" />
                    </div>
                    <input
                        type="text"
                        value={searchValue}
                        onChange={(e) => setSearchValue(e.target.value)}
                        className="block w-full rounded-lg bg-white/5 py-1.5 pl-9 pr-14 text-[0.8rem] text-white placeholder-zinc-500 outline-none ring-1 ring-white/5 focus:ring-teal-accent/30 transition-all"
                        placeholder="Search cases, documents..."
                    />
                    <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                        <kbd className="hidden sm:flex h-4 items-center gap-0.5 rounded border border-white/10 bg-white/5 px-1 font-mono text-[0.55rem] font-medium text-zinc-500">
                            <Command className="h-2 w-2" />
                            <span>K</span>
                        </kbd>
                    </div>
                </div>
            </form>

            {/* Actions */}
            <div className="flex items-center gap-2 sm:gap-3 shrink-0">
                <button onClick={() => router.push('/cases')} className="hidden sm:flex h-8 items-center gap-1.5 rounded-lg bg-teal-accent px-3 text-[0.75rem] font-semibold text-navy-deep hover:bg-teal-300 transition-colors">
                    <Plus className="h-3.5 w-3.5" />
                    <span>New Case</span>
                </button>

                {/* Notifications */}
                <div className="relative" ref={notifRef}>
                    <button
                        onClick={() => setShowNotifications(!showNotifications)}
                        className="relative p-1.5 sm:p-2 text-zinc-500 hover:text-white transition-colors"
                    >
                        <Bell className="h-4 w-4 sm:h-5 sm:w-5" />
                        <span className="absolute top-0.5 right-0.5 sm:top-1 sm:right-1 h-2 w-2 rounded-full bg-violet-accent shadow-[0_0_8px_rgba(124,58,237,0.5)]" />
                    </button>

                    <AnimatePresence>
                        {showNotifications && (
                            <motion.div
                                initial={{ opacity: 0, y: 8, scale: 0.95 }}
                                animate={{ opacity: 1, y: 0, scale: 1 }}
                                exit={{ opacity: 0, y: 8, scale: 0.95 }}
                                transition={{ duration: 0.15 }}
                                className="absolute right-0 top-full mt-2 w-72 rounded-xl bg-navy-surface border border-white/10 shadow-2xl overflow-hidden z-50"
                            >
                                <div className="flex items-center justify-between px-4 py-3 border-b border-white/5">
                                    <h3 className="text-[0.75rem] font-bold text-white">Notifications</h3>
                                    <button
                                        onClick={() => setShowNotifications(false)}
                                        className="p-0.5 text-zinc-500 hover:text-white transition-colors"
                                    >
                                        <X className="h-3.5 w-3.5" />
                                    </button>
                                </div>
                                <div className="p-4 space-y-3">
                                    <div className="flex items-start gap-2.5">
                                        <div className="h-2 w-2 rounded-full bg-teal-accent mt-1.5 shrink-0" />
                                        <div>
                                            <p className="text-[0.75rem] text-zinc-300">System connected to backend</p>
                                            <p className="text-[0.6rem] text-zinc-600 mt-0.5">Just now</p>
                                        </div>
                                    </div>
                                    <div className="flex items-start gap-2.5">
                                        <div className="h-2 w-2 rounded-full bg-violet-accent mt-1.5 shrink-0" />
                                        <div>
                                            <p className="text-[0.75rem] text-zinc-300">Database synced successfully</p>
                                            <p className="text-[0.6rem] text-zinc-600 mt-0.5">2 min ago</p>
                                        </div>
                                    </div>
                                    <div className="flex items-start gap-2.5">
                                        <div className="h-2 w-2 rounded-full bg-zinc-600 mt-1.5 shrink-0" />
                                        <div>
                                            <p className="text-[0.75rem] text-zinc-400">AI service ready</p>
                                            <p className="text-[0.6rem] text-zinc-600 mt-0.5">5 min ago</p>
                                        </div>
                                    </div>
                                </div>
                                <div className="px-4 py-2 border-t border-white/5 bg-white/[0.02]">
                                    <p className="text-[0.6rem] text-zinc-600 text-center">All caught up</p>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                <a href="https://github.com/Dhwanil25/DAIL_Backend" target="_blank" rel="noopener noreferrer" className="hidden sm:block p-2 text-zinc-500 hover:text-white transition-colors">
                    <Github className="h-5 w-5" />
                </a>
            </div>
        </header>
    );
}
