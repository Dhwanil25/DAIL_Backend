"use client";

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
    Send,
    Zap,
    Copy,
    Check,
    Sparkles
} from 'lucide-react';
import { ActivityChart } from './activity-chart';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export function IntelligencePanel() {
    const router = useRouter();
    const [copied, setCopied] = useState(false);

    function handleCopy() {
        const text = "Latest docket includes 3 filings:\n• Motion to Dismiss (Apr 20)\n• Court Order (Apr 22)\n• Hearing Scheduled (May 5)";
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    }

    return (
        <div className="flex flex-col gap-4">
            {/* System Health */}
            <div className="rounded-xl bg-navy-surface border border-white/5 p-4">
                <div className="flex items-center justify-between mb-3">
                    <h3 className="text-[0.65rem] font-semibold text-zinc-500 uppercase tracking-widest">System Health</h3>
                    <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                        <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                        <span className="text-[0.6rem] font-bold text-emerald-400 uppercase tracking-wider">All Systems Operational</span>
                    </div>
                </div>

                <div className="flex items-end gap-0.5 h-8">
                    {[...Array(24)].map((_, i) => (
                        <motion.div
                            key={i}
                            initial={{ height: 8 }}
                            animate={{ height: Math.random() * 20 + 8 }}
                            transition={{ repeat: Infinity, repeatType: "reverse", duration: 1, delay: i * 0.04 }}
                            className="flex-1 rounded-sm bg-teal-accent/30"
                        />
                    ))}
                </div>
            </div>

            {/* AI Assistant */}
            <div className="rounded-xl bg-navy-surface border border-white/5 p-4 flex flex-col">
                <div className="flex items-center gap-2 mb-4">
                    <div className="p-1 rounded-md bg-violet-500/10 border border-violet-500/20">
                        <Zap className="h-3.5 w-3.5 text-violet-400" />
                    </div>
                    <h3 className="text-[0.8rem] font-bold text-white">AI Assistant</h3>
                </div>

                <div className="space-y-3 mb-4">
                    <div className="rounded-lg bg-white/[0.03] p-3 border border-white/5">
                        <p className="text-[0.75rem] text-zinc-400 italic">
                            Summarize latest docket for LIA-2024-001
                        </p>
                    </div>

                    <motion.div
                        initial={{ opacity: 0, y: 6 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-3"
                    >
                        <div className="flex items-center gap-1.5">
                            <Sparkles className="h-3 w-3 text-teal-accent" />
                            <span className="text-[0.6rem] font-bold text-zinc-500 uppercase tracking-widest">AI Response</span>
                        </div>
                        <div className="text-[0.8rem] text-zinc-300 leading-relaxed space-y-2">
                            <p>Latest docket includes 3 filings:</p>
                            <ul className="space-y-1.5 ml-1">
                                <li className="flex items-center gap-2 text-[0.75rem]">
                                    <div className="h-1 w-1 rounded-full bg-teal-accent shrink-0" />
                                    <span>Motion to Dismiss (Apr 20)</span>
                                </li>
                                <li className="flex items-center gap-2 text-[0.75rem]">
                                    <div className="h-1 w-1 rounded-full bg-teal-accent shrink-0" />
                                    <span>Court Order (Apr 22)</span>
                                </li>
                                <li className="flex items-center gap-2 text-[0.75rem]">
                                    <div className="h-1 w-1 rounded-full bg-teal-accent shrink-0" />
                                    <span>Hearing Scheduled (May 5)</span>
                                </li>
                            </ul>
                        </div>

                        <div className="flex items-center gap-2 pt-1">
                            <button
                                onClick={handleCopy}
                                className="flex items-center gap-1 px-2 py-1 rounded-md bg-white/5 text-[0.6rem] font-semibold text-zinc-400 hover:text-white transition-colors border border-white/5"
                            >
                                {copied ? (
                                    <>
                                        <Check className="h-3 w-3 text-emerald-400" />
                                        <span className="text-emerald-400">Copied!</span>
                                    </>
                                ) : (
                                    <>
                                        <Copy className="h-3 w-3" />
                                        <span>Copy</span>
                                    </>
                                )}
                            </button>
                            <Link
                                href="/ai"
                                className="flex items-center gap-1 px-2 py-1 rounded-md bg-white/5 text-[0.6rem] font-semibold text-zinc-400 hover:text-white transition-colors border border-white/5"
                            >
                                <Sparkles className="h-3 w-3" />
                                <span>Open Chat</span>
                            </Link>
                        </div>
                    </motion.div>
                </div>

                <Link
                    href="/ai"
                    className="mt-auto relative block"
                >
                    <div className="w-full rounded-lg bg-navy-deep border border-white/10 px-3 py-2 text-[0.8rem] text-zinc-600 cursor-pointer hover:border-teal-accent/40 transition-all pr-10">
                        Ask anything...
                    </div>
                    <div className="absolute right-1.5 top-1 p-1.5 rounded-md bg-teal-accent text-navy-deep">
                        <Send className="h-3.5 w-3.5" />
                    </div>
                </Link>
            </div>

            {/* Analytics */}
            <div className="rounded-xl bg-navy-surface border border-white/5 p-4">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-[0.8rem] font-bold text-white">Analytics</h3>
                    <Link
                        href="/analytics"
                        className="flex items-center px-2 py-1 rounded-md bg-white/5 text-[0.6rem] text-zinc-400 hover:text-white transition-colors border border-white/5 font-semibold uppercase tracking-wider"
                    >
                        Last 6 Months
                    </Link>
                </div>

                <div className="flex items-center gap-4 mb-3">
                    <div className="flex items-center gap-1.5">
                        <div className="h-2 w-2 rounded-full bg-teal-accent" />
                        <span className="text-[0.6rem] font-semibold text-zinc-500 uppercase">Cases</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                        <div className="h-2 w-2 rounded-full bg-violet-accent" />
                        <span className="text-[0.6rem] font-semibold text-zinc-500 uppercase">Docs</span>
                    </div>
                </div>

                <ActivityChart />
            </div>
        </div>
    );
}
