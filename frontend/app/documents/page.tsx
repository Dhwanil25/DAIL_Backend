"use client";

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, Search, ChevronLeft, ChevronRight, ExternalLink } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useDocuments } from '@/lib/hooks';
import type { DocumentResponse } from '@/types';

const PER_PAGE = 10;
const DOC_COLORS = ['text-blue-400', 'text-rose-400', 'text-violet-400', 'text-emerald-400', 'text-amber-400', 'text-teal-400'];

const FALLBACK_DOCS = [
    { id: 1, case_number: 1, court: 'Supreme Court', date: '2024-04-18', link: null, cite_or_reference: 'Petition.pdf', document: null },
    { id: 2, case_number: 1, court: 'Supreme Court', date: '2024-04-19', link: null, cite_or_reference: 'Evidence_01.pdf', document: null },
    { id: 3, case_number: 1, court: 'High Court', date: '2024-04-22', link: null, cite_or_reference: 'Order_0422.pdf', document: null },
];

export default function DocumentsPage() {
    const [page, setPage] = useState(1);
    const [searchText, setSearchText] = useState('');

    const skip = (page - 1) * PER_PAGE;
    const { data: docsData, isLoading } = useDocuments({
        skip,
        limit: PER_PAGE,
    });

    const total = docsData?.total || 0;
    const totalPages = Math.ceil(total / PER_PAGE);
    const docs: DocumentResponse[] = docsData?.items || FALLBACK_DOCS;

    const filtered = docs.filter(d => {
        const name = (d.cite_or_reference || d.document || '').toLowerCase();
        const court = (d.court || '').toLowerCase();
        return !searchText || name.includes(searchText.toLowerCase()) || court.includes(searchText.toLowerCase());
    });

    return (
        <div className="space-y-5 max-w-[1600px] mx-auto">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-xl font-bold text-white">Documents</h1>
                    <p className="text-[0.8rem] text-zinc-500 mt-0.5">{total} total document{total !== 1 ? 's' : ''}</p>
                </div>
            </div>

            {/* Search */}
            <div className="flex flex-wrap gap-2 items-center">
                <div className="relative flex-1 min-w-[200px] max-w-md">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-zinc-500" />
                    <input type="text" value={searchText} onChange={(e) => setSearchText(e.target.value)}
                        placeholder="Search by document name, citation..."
                        className="w-full rounded-lg bg-white/5 py-1.5 pl-9 pr-3 text-[0.8rem] text-white placeholder-zinc-500 outline-none ring-1 ring-white/5 focus:ring-teal-accent/30 transition-all" />
                </div>
            </div>

            {isLoading ? (
                <div className="space-y-2">
                    {[...Array(PER_PAGE)].map((_, i) => <div key={i} className="rounded-xl bg-navy-surface border border-white/5 p-4 h-16 animate-pulse" />)}
                </div>
            ) : (
                <div className="space-y-2" key={`page-${page}`}>
                    {filtered.map((doc, idx) => (
                        <motion.div key={doc.id} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.04 }}
                            className="flex items-center gap-3 rounded-xl bg-navy-surface border border-white/5 p-4 hover:border-teal-accent/20 transition-all cursor-pointer group">
                            <div className={cn("p-1.5 rounded-md bg-navy-deep", DOC_COLORS[idx % DOC_COLORS.length])}>
                                <FileText className="h-4 w-4" />
                            </div>
                            <div className="flex-1 min-w-0">
                                <h3 className="text-[0.8rem] font-semibold text-white group-hover:text-teal-accent transition-colors truncate">
                                    {doc.cite_or_reference || doc.document || `Document #${doc.id}`}
                                </h3>
                                <div className="flex items-center gap-2 mt-0.5 flex-wrap">
                                    <span className="text-[0.7rem] text-zinc-500">{doc.court || 'N/A'}</span>
                                    <span className="h-0.5 w-0.5 rounded-full bg-zinc-700" />
                                    <span className="text-[0.7rem] text-zinc-500">{doc.date || 'N/A'}</span>
                                    <span className="h-0.5 w-0.5 rounded-full bg-zinc-700" />
                                    <span className="text-[0.55rem] font-mono px-1.5 py-0.5 rounded bg-teal-accent/10 text-teal-accent/80 border border-teal-accent/20">Case #{doc.case_number}</span>
                                </div>
                            </div>
                            {doc.link && (
                                <a href={doc.link} target="_blank" rel="noopener noreferrer" className="p-1.5 text-zinc-500 hover:text-teal-accent transition-colors opacity-0 group-hover:opacity-100">
                                    <ExternalLink className="h-3.5 w-3.5" />
                                </a>
                            )}
                        </motion.div>
                    ))}
                    {filtered.length === 0 && (
                        <div className="text-center py-6">
                            <p className="text-[0.8rem] text-zinc-500">No documents found.</p>
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
