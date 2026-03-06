"use client";

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useDockets } from '@/lib/hooks';
import { MOCK_TIMELINE } from '@/lib/mock-data';
import type { DocketResponse } from '@/types';

const PER_PAGE = 10;
const DOCKET_COLORS = ['bg-emerald-500', 'bg-blue-500', 'bg-violet-500', 'bg-amber-500', 'bg-rose-500'];

export default function DocketsPage() {
    const [page, setPage] = useState(1);
    const [searchText, setSearchText] = useState('');

    const skip = (page - 1) * PER_PAGE;
    const { data: docketsData, isLoading } = useDockets({
        skip,
        limit: PER_PAGE,
    });

    const total = docketsData?.total || 0;
    const totalPages = Math.ceil(total / PER_PAGE);

    interface DisplayDocket {
        key: string; date: string; title: string; type: string; color: string; link: string | null; caseNumber: number;
    }

    const allDockets: DisplayDocket[] = docketsData?.items
        ? docketsData.items.map((d: DocketResponse, i: number) => ({
            key: `docket-${d.id}`,
            date: d.court || 'N/A',
            title: d.number || `Docket #${d.id}`,
            type: 'filing',
            color: DOCKET_COLORS[i % DOCKET_COLORS.length],
            link: d.link,
            caseNumber: d.case_number,
        }))
        : MOCK_TIMELINE.map((d, i) => ({ ...d, key: `mock-${i}`, link: null, caseNumber: 0 }));

    const filtered = searchText
        ? allDockets.filter(d => d.title.toLowerCase().includes(searchText.toLowerCase()) || d.date.toLowerCase().includes(searchText.toLowerCase()))
        : allDockets;

    return (
        <div className="space-y-5 max-w-[1600px] mx-auto">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-xl font-bold text-white">Dockets</h1>
                    <p className="text-[0.8rem] text-zinc-500 mt-0.5">{total} total entr{total !== 1 ? 'ies' : 'y'}</p>
                </div>
            </div>

            {/* Search */}
            <div className="flex flex-wrap gap-2 items-center">
                <div className="relative flex-1 min-w-[200px] max-w-md">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-zinc-500" />
                    <input type="text" value={searchText} onChange={(e) => setSearchText(e.target.value)}
                        placeholder="Search by docket number, court..."
                        className="w-full rounded-lg bg-white/5 py-1.5 pl-9 pr-3 text-[0.8rem] text-white placeholder-zinc-500 outline-none ring-1 ring-white/5 focus:ring-teal-accent/30 transition-all" />
                </div>
            </div>

            {isLoading ? (
                <div className="rounded-xl bg-navy-surface border border-white/5 p-5 space-y-4">
                    {[...Array(PER_PAGE)].map((_, i) => <div key={i} className="h-10 bg-white/5 rounded animate-pulse" />)}
                </div>
            ) : (
                <div className="rounded-xl bg-navy-surface border border-white/5 p-5" key={`page-${page}`}>
                    <div className="relative">
                        <div className="absolute left-[7px] top-0 bottom-0 w-px bg-white/10" />
                        <div className="space-y-6">
                            {filtered.map((event, idx) => (
                                <motion.div key={event.key} initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: idx * 0.06 }}
                                    className="relative flex items-start gap-4 group cursor-pointer">
                                    <div className={`relative z-10 mt-1 h-3.5 w-3.5 rounded-full border-2 border-navy-surface ${event.color}`} />
                                    <div className="flex-1 pb-5 border-b border-white/5 last:border-b-0">
                                        <div className="flex items-center gap-2 mb-1">
                                            <span className="text-[0.6rem] font-semibold text-zinc-500 uppercase tracking-widest">{event.date}</span>
                                            <span className="text-[0.55rem] px-1.5 py-0.5 rounded bg-white/5 text-zinc-500 border border-white/5 uppercase font-bold tracking-wider">{event.type}</span>
                                            {event.caseNumber > 0 && <span className="text-[0.55rem] px-1.5 py-0.5 rounded bg-teal-accent/10 text-teal-accent/80 border border-teal-accent/20 font-mono">Case #{event.caseNumber}</span>}
                                        </div>
                                        {event.link ? (
                                            <a href={event.link} target="_blank" rel="noopener noreferrer" className="text-[0.8rem] font-medium text-white hover:text-teal-accent transition-colors">{event.title}</a>
                                        ) : (
                                            <span className="text-[0.8rem] font-medium text-white group-hover:text-teal-accent transition-colors">{event.title}</span>
                                        )}
                                    </div>
                                </motion.div>
                            ))}
                            {filtered.length === 0 && (
                                <div className="text-center py-6">
                                    <p className="text-[0.8rem] text-zinc-500">No dockets found.</p>
                                </div>
                            )}
                        </div>
                    </div>
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
