"use client";

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Library, Search, ChevronLeft, ChevronRight, ExternalLink } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useSecondarySources } from '@/lib/hooks';
import type { SecondarySourceResponse } from '@/types';

const PER_PAGE = 10;

const FALLBACK_SOURCES = [
    { id: 1, case_number: 1, secondary_source_link: null, secondary_source_title: 'AI Litigation Trends Report 2024' },
    { id: 2, case_number: 2, secondary_source_link: null, secondary_source_title: 'Federal Register Notice on AI Governance' },
    { id: 3, case_number: 3, secondary_source_link: null, secondary_source_title: 'Harvard Law Review: AI and Liability' },
];

export default function SourcesPage() {
    const [page, setPage] = useState(1);
    const [searchText, setSearchText] = useState('');

    const skip = (page - 1) * PER_PAGE;
    const { data: sourcesData, isLoading } = useSecondarySources({
        skip,
        limit: PER_PAGE,
    });

    const total = sourcesData?.total || 0;
    const totalPages = Math.ceil(total / PER_PAGE);
    const sources: SecondarySourceResponse[] = sourcesData?.items || FALLBACK_SOURCES;

    const filtered = searchText
        ? sources.filter(s => (s.secondary_source_title || '').toLowerCase().includes(searchText.toLowerCase()))
        : sources;

    return (
        <div className="space-y-5 max-w-[1600px] mx-auto">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-xl font-bold text-white">Secondary Sources</h1>
                    <p className="text-[0.8rem] text-zinc-500 mt-0.5">{total} total source{total !== 1 ? 's' : ''}</p>
                </div>
            </div>

            {/* Search */}
            <div className="flex flex-wrap gap-2 items-center">
                <div className="relative flex-1 min-w-[200px] max-w-md">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-zinc-500" />
                    <input type="text" value={searchText} onChange={(e) => setSearchText(e.target.value)}
                        placeholder="Search by source title..."
                        className="w-full rounded-lg bg-white/5 py-1.5 pl-9 pr-3 text-[0.8rem] text-white placeholder-zinc-500 outline-none ring-1 ring-white/5 focus:ring-teal-accent/30 transition-all" />
                </div>
            </div>

            {isLoading ? (
                <div className="space-y-2">
                    {[...Array(PER_PAGE)].map((_, i) => <div key={i} className="rounded-xl bg-navy-surface border border-white/5 p-4 h-16 animate-pulse" />)}
                </div>
            ) : (
                <div className="space-y-2" key={`page-${page}`}>
                    {filtered.map((source, idx) => (
                        <motion.div key={source.id} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.04 }}
                            className="flex items-center gap-3 rounded-xl bg-navy-surface border border-white/5 p-4 hover:border-teal-accent/20 transition-all cursor-pointer group">
                            <div className="p-1.5 rounded-md bg-violet-500/10 border border-violet-500/20">
                                <Library className="h-4 w-4 text-violet-400" />
                            </div>
                            <div className="flex-1 min-w-0">
                                <h3 className="text-[0.8rem] font-semibold text-white group-hover:text-teal-accent transition-colors truncate">
                                    {source.secondary_source_title || `Source #${source.id}`}
                                </h3>
                                <div className="flex items-center gap-2 mt-0.5">
                                    <span className="text-[0.55rem] font-mono px-1.5 py-0.5 rounded bg-teal-accent/10 text-teal-accent/80 border border-teal-accent/20">Case #{source.case_number}</span>
                                </div>
                            </div>
                            {source.secondary_source_link && (
                                <a href={source.secondary_source_link} target="_blank" rel="noopener noreferrer" className="p-1.5 text-zinc-500 hover:text-teal-accent transition-colors opacity-0 group-hover:opacity-100">
                                    <ExternalLink className="h-3.5 w-3.5" />
                                </a>
                            )}
                        </motion.div>
                    ))}
                    {filtered.length === 0 && (
                        <div className="text-center py-6">
                            <p className="text-[0.8rem] text-zinc-500">No sources found.</p>
                        </div>
                    )}
                </div>
            )}

            {totalPages > 1 && (
                <div className="flex items-center justify-between pt-2">
                    <p className="text-[0.7rem] text-zinc-500">Showing {skip + 1}–{Math.min(skip + PER_PAGE, total)} of {total}</p>
                    <div className="flex items-center gap-1.5">
                        <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="p-1.5 rounded-lg bg-white/5 text-zinc-400 hover:text-white disabled:opacity-30 transition-colors border border-white/5"><ChevronLeft className="h-3.5 w-3.5" /></button>
                        {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
                            let pn: number; if (totalPages <= 7) pn = i + 1; else if (page <= 4) pn = i + 1; else if (page >= totalPages - 3) pn = totalPages - 6 + i; else pn = page - 3 + i;
                            return <button key={pn} onClick={() => setPage(pn)} className={cn("px-2.5 py-1 rounded-lg text-[0.7rem] font-semibold transition-all border", page === pn ? "bg-teal-accent/10 text-teal-accent border-teal-accent/20" : "bg-white/5 text-zinc-400 border-white/5 hover:text-white")}>{pn}</button>;
                        })}
                        <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages} className="p-1.5 rounded-lg bg-white/5 text-zinc-400 hover:text-white disabled:opacity-30 transition-colors border border-white/5"><ChevronRight className="h-3.5 w-3.5" /></button>
                    </div>
                </div>
            )}
        </div>
    );
}
