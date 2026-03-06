"use client";

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Edit2, ExternalLink } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useCases } from '@/lib/hooks';
import { MOCK_CASES } from '@/lib/mock-data';
import Link from 'next/link';
import type { CaseResponse } from '@/types';

export function CaseTable() {
    const [expandedRow, setExpandedRow] = useState<string | null>(null);
    const { data: casesData } = useCases({ limit: 5 });

    // Map API data to display format, fallback to mock
    const displayCases = casesData?.items
        ? casesData.items.map((c: CaseResponse) => ({
            id: `LIA-${c.id}`,
            title: c.caption,
            court: c.current_jurisdiction || c.jurisdiction_filed || 'N/A',
            filedOn: c.date_action_filed || 'N/A',
            status: c.status_disposition || 'Unknown',
            summary: c.brief_description || c.summary_facts_activity || 'No summary available.',
        }))
        : MOCK_CASES;

    return (
        <div className="rounded-xl bg-navy-surface border border-white/5 overflow-hidden">
            <div className="flex flex-wrap items-center justify-between gap-2 px-4 py-3 border-b border-white/5">
                <h2 className="text-sm font-bold text-white">
                    Recent Cases
                    <span className="ml-2 text-[0.6rem] font-semibold text-zinc-500">
                        showing {displayCases.length}
                    </span>
                </h2>
                <Link href="/cases" className="text-teal-accent hover:text-teal-300 text-[0.7rem] font-semibold transition-colors">
                    View All →
                </Link>
            </div>

            <div className="overflow-x-auto">
                <table className="min-w-full">
                    <thead>
                        <tr className="border-b border-white/5 bg-white/[0.02]">
                            <th className="px-4 py-2 text-left text-[0.6rem] font-bold text-zinc-500 uppercase tracking-widest">ID</th>
                            <th className="px-4 py-2 text-left text-[0.6rem] font-bold text-zinc-500 uppercase tracking-widest">Case Title</th>
                            <th className="px-4 py-2 text-left text-[0.6rem] font-bold text-zinc-500 uppercase tracking-widest hidden sm:table-cell">Court</th>
                            <th className="px-4 py-2 text-left text-[0.6rem] font-bold text-zinc-500 uppercase tracking-widest hidden md:table-cell">Filed On</th>
                            <th className="px-4 py-2 text-left text-[0.6rem] font-bold text-zinc-500 uppercase tracking-widest">Status</th>
                            <th className="px-4 py-2 text-right text-[0.6rem] font-bold text-zinc-500 uppercase tracking-widest">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {displayCases.map((caseItem) => (
                            <React.Fragment key={caseItem.id}>
                                <tr
                                    onClick={() => setExpandedRow(expandedRow === caseItem.id ? null : caseItem.id)}
                                    className="group hover:bg-white/[0.03] cursor-pointer transition-colors"
                                >
                                    <td className="px-4 py-2.5 text-[0.65rem] font-mono text-teal-accent/80">{caseItem.id}</td>
                                    <td className="px-4 py-2.5 text-[0.8rem] font-semibold text-white group-hover:text-teal-accent transition-colors max-w-[200px] truncate">{caseItem.title}</td>
                                    <td className="px-4 py-2.5 text-[0.7rem] text-zinc-400 hidden sm:table-cell">{caseItem.court}</td>
                                    <td className="px-4 py-2.5 text-[0.7rem] text-zinc-500 hidden md:table-cell">{caseItem.filedOn}</td>
                                    <td className="px-4 py-2.5">
                                        <span className={cn(
                                            "text-[0.55rem] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border",
                                            caseItem.status.toLowerCase().includes('open') || caseItem.status.toLowerCase().includes('pending')
                                                ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                                                : caseItem.status.toLowerCase().includes('progress') || caseItem.status.toLowerCase().includes('active')
                                                    ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                                                    : caseItem.status.toLowerCase().includes('closed') || caseItem.status.toLowerCase().includes('settled')
                                                        ? "bg-zinc-500/10 text-zinc-400 border-zinc-500/20"
                                                        : "bg-violet-500/10 text-violet-400 border-violet-500/20"
                                        )}>
                                            {caseItem.status}
                                        </span>
                                    </td>
                                    <td className="px-4 py-2.5">
                                        <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <button className="p-1 text-zinc-500 hover:text-teal-accent transition-colors">
                                                <ExternalLink className="h-3 w-3" />
                                            </button>
                                            <button className="p-1 text-zinc-500 hover:text-teal-accent transition-colors">
                                                <Edit2 className="h-3 w-3" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                                <AnimatePresence>
                                    {expandedRow === caseItem.id && (
                                        <tr key={`expanded-${caseItem.id}`}>
                                            <td colSpan={6} className="px-0 py-0">
                                                <motion.div
                                                    initial={{ height: 0, opacity: 0 }}
                                                    animate={{ height: 'auto', opacity: 1 }}
                                                    exit={{ height: 0, opacity: 0 }}
                                                    transition={{ duration: 0.2 }}
                                                    className="overflow-hidden"
                                                >
                                                    <div className="px-6 py-4 bg-white/[0.02] text-[0.75rem] text-zinc-400 leading-relaxed border-l-2 border-teal-accent/30 ml-4">
                                                        <p className="text-[0.6rem] font-bold text-zinc-500 uppercase tracking-widest mb-1">AI Summary</p>
                                                        {caseItem.summary}
                                                    </div>
                                                </motion.div>
                                            </td>
                                        </tr>
                                    )}
                                </AnimatePresence>
                            </React.Fragment>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
