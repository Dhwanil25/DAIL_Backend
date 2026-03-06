"use client";

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Eye, Edit2, Trash2, ChevronLeft, ChevronRight, X, AlertTriangle, Search } from 'lucide-react';
import { cn } from '@/lib/utils';
import { CreateCaseModal } from '@/components/dashboard/create-case-modal';
import { useCases, useDeleteCase } from '@/lib/hooks';
import { MOCK_CASES } from '@/lib/mock-data';
import type { CaseResponse } from '@/types';

const PER_PAGE = 9;

interface DisplayCase {
    id: string;
    numericId?: number;
    title: string;
    court: string;
    filedOn: string;
    status: string;
    summary: string;
    jurisdictionType?: string | null;
    area?: string | null;
}

export default function CasesPage() {
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [page, setPage] = useState(1);
    const [expandedCase, setExpandedCase] = useState<string | null>(null);
    const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
    const [searchQ, setSearchQ] = useState('');

    const skip = (page - 1) * PER_PAGE;
    const { data: casesData, isLoading } = useCases({
        skip,
        limit: PER_PAGE,
        q: searchQ.length >= 2 ? searchQ : undefined,
    });
    const deleteMutation = useDeleteCase();

    const total = casesData?.total || 0;
    const totalPages = Math.ceil(total / PER_PAGE);

    const displayCases: DisplayCase[] = casesData?.items
        ? casesData.items.map((c: CaseResponse) => ({
            id: `LIA-${c.id}`,
            numericId: c.id,
            title: c.caption,
            court: c.current_jurisdiction || c.jurisdiction_filed || 'N/A',
            filedOn: c.date_action_filed || 'N/A',
            status: c.status_disposition || 'Unknown',
            summary: c.brief_description || c.summary_facts_activity || 'No summary available.',
            jurisdictionType: c.jurisdiction_type,
            area: c.area_of_application,
        }))
        : MOCK_CASES.map(c => ({ ...c, numericId: undefined, jurisdictionType: null, area: null }));

    function handleDelete(caseItem: DisplayCase) {
        if (caseItem.numericId) deleteMutation.mutate(caseItem.numericId);
        setDeleteConfirm(null);
    }

    return (
        <div className="space-y-5 max-w-[1600px] mx-auto">
            <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                    <h1 className="text-xl font-bold text-white">Cases</h1>
                    <p className="text-[0.8rem] text-zinc-500 mt-0.5">{total} total case{total !== 1 ? 's' : ''}</p>
                </div>
                <button onClick={() => setShowCreateModal(true)} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-teal-accent text-navy-deep text-[0.75rem] font-semibold hover:bg-teal-300 transition-colors">
                    <Plus className="h-3.5 w-3.5" /><span>New Case</span>
                </button>
            </div>

            {/* Search */}
            <div className="flex flex-wrap gap-2 items-center">
                <div className="relative flex-1 min-w-[200px] max-w-md">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-zinc-500" />
                    <input
                        type="text" value={searchQ}
                        onChange={(e) => { setSearchQ(e.target.value); setPage(1); }}
                        placeholder="Search cases by name, description..."
                        className="w-full rounded-lg bg-white/5 py-1.5 pl-9 pr-3 text-[0.8rem] text-white placeholder-zinc-500 outline-none ring-1 ring-white/5 focus:ring-teal-accent/30 transition-all"
                    />
                </div>
            </div>

            {isLoading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                    {[...Array(PER_PAGE)].map((_, i) => <div key={i} className="rounded-xl bg-navy-surface border border-white/5 p-4 h-40 animate-pulse" />)}
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3" key={`page-${page}-${searchQ}`}>
                    {displayCases.map((caseItem, idx) => (
                        <motion.div key={caseItem.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.05 }}
                            className="rounded-xl bg-navy-surface border border-white/5 p-4 hover:border-teal-accent/20 transition-all group">
                            <div className="flex items-center justify-between mb-3">
                                <span className="text-[0.6rem] font-mono text-teal-accent/80">{caseItem.id}</span>
                                <span className={cn("text-[0.55rem] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded-full border",
                                    caseItem.status.toLowerCase().includes('open') || caseItem.status.toLowerCase().includes('pending') ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                                        : caseItem.status.toLowerCase().includes('progress') || caseItem.status.toLowerCase().includes('active') ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                                            : caseItem.status.toLowerCase().includes('closed') || caseItem.status.toLowerCase().includes('settled') ? "bg-zinc-500/10 text-zinc-400 border-zinc-500/20"
                                                : "bg-violet-500/10 text-violet-400 border-violet-500/20"
                                )}>{caseItem.status}</span>
                            </div>
                            <h3 className="text-[0.85rem] font-semibold text-white mb-1 group-hover:text-teal-accent transition-colors truncate">{caseItem.title}</h3>
                            <p className="text-[0.7rem] text-zinc-500">{caseItem.court} · Filed {caseItem.filedOn}</p>

                            <AnimatePresence>
                                {expandedCase === caseItem.id ? (
                                    <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
                                        <p className="text-[0.7rem] text-zinc-400 mt-2 border-t border-white/5 pt-2">{caseItem.summary}</p>
                                    </motion.div>
                                ) : (
                                    <p className="text-[0.7rem] text-zinc-400 mt-2 line-clamp-2">{caseItem.summary}</p>
                                )}
                            </AnimatePresence>

                            <AnimatePresence>
                                {deleteConfirm === caseItem.id && (
                                    <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden mt-2">
                                        <div className="flex items-center gap-2 bg-rose-500/10 border border-rose-500/20 rounded-lg p-2">
                                            <AlertTriangle className="h-3.5 w-3.5 text-rose-400 shrink-0" />
                                            <span className="text-[0.7rem] text-rose-300 flex-1">Delete this case?</span>
                                            <button onClick={() => handleDelete(caseItem)} className="px-2 py-0.5 rounded bg-rose-500 text-[0.6rem] font-bold text-white hover:bg-rose-400 transition-colors">Delete</button>
                                            <button onClick={() => setDeleteConfirm(null)} className="p-0.5 text-zinc-400 hover:text-white transition-colors"><X className="h-3 w-3" /></button>
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>

                            <div className="flex items-center gap-1 mt-3 pt-2 border-t border-white/5">
                                <button onClick={() => setExpandedCase(expandedCase === caseItem.id ? null : caseItem.id)} title={expandedCase === caseItem.id ? 'Collapse' : 'View details'} className={cn("p-1.5 transition-colors", expandedCase === caseItem.id ? "text-teal-accent" : "text-zinc-500 hover:text-teal-accent")}><Eye className="h-3.5 w-3.5" /></button>
                                <button onClick={() => setShowCreateModal(true)} title="Edit case" className="p-1.5 text-zinc-500 hover:text-teal-accent transition-colors"><Edit2 className="h-3.5 w-3.5" /></button>
                                <button onClick={() => setDeleteConfirm(deleteConfirm === caseItem.id ? null : caseItem.id)} title="Delete case" className={cn("p-1.5 transition-colors", deleteConfirm === caseItem.id ? "text-rose-400" : "text-zinc-500 hover:text-rose-400")}><Trash2 className="h-3.5 w-3.5" /></button>
                            </div>
                        </motion.div>
                    ))}
                    {displayCases.length === 0 && !isLoading && (
                        <div className="col-span-full text-center py-8">
                            <p className="text-[0.8rem] text-zinc-500">No cases found.</p>
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
                            let pn: number;
                            if (totalPages <= 7) pn = i + 1; else if (page <= 4) pn = i + 1; else if (page >= totalPages - 3) pn = totalPages - 6 + i; else pn = page - 3 + i;
                            return <button key={pn} onClick={() => setPage(pn)} className={cn("px-2.5 py-1 rounded-lg text-[0.7rem] font-semibold transition-all border", page === pn ? "bg-teal-accent/10 text-teal-accent border-teal-accent/20" : "bg-white/5 text-zinc-400 border-white/5 hover:text-white")}>{pn}</button>;
                        })}
                        <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages} className="p-1.5 rounded-lg bg-white/5 text-zinc-400 hover:text-white disabled:opacity-30 transition-colors border border-white/5"><ChevronRight className="h-3.5 w-3.5" /></button>
                    </div>
                </div>
            )}

            <AnimatePresence>
                {showCreateModal && <CreateCaseModal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} />}
            </AnimatePresence>
        </div>
    );
}
