"use client";

import { motion } from 'framer-motion';
import { FileText, MoreVertical, Plus, Download } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useDocuments } from '@/lib/hooks';
import { MOCK_DOCUMENTS } from '@/lib/mock-data';
import Link from 'next/link';
import type { DocumentResponse } from '@/types';

const DOC_COLORS = ['text-blue-400', 'text-rose-400', 'text-violet-400', 'text-emerald-400', 'text-amber-400'];

export function DocumentsCard() {
    const { data: docsData } = useDocuments({ limit: 3 });

    const displayDocs = docsData?.items
        ? docsData.items.map((d: DocumentResponse, i: number) => ({
            name: d.cite_or_reference || d.document || `Document #${d.id}`,
            size: d.court || 'N/A',
            date: d.date || 'N/A',
            color: DOC_COLORS[i % DOC_COLORS.length],
        }))
        : MOCK_DOCUMENTS;

    return (
        <div className="flex flex-col rounded-xl bg-navy-surface border border-white/5 p-4 overflow-hidden">
            <div className="flex items-center justify-between mb-5">
                <h2 className="text-sm font-bold text-white">Documents</h2>
                <Link href="/documents" className="text-teal-accent hover:text-teal-300 text-[0.7rem] font-semibold transition-colors">
                    View All →
                </Link>
            </div>

            <div className="space-y-2.5 flex-1">
                {displayDocs.map((doc, idx) => (
                    <motion.div
                        key={doc.name}
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.07 }}
                        className="group flex items-center gap-3 bg-white/[0.03] hover:bg-white/[0.06] p-3 rounded-lg border border-white/5 transition-all duration-200 cursor-pointer"
                    >
                        <div className={cn("p-1.5 rounded-md bg-navy-deep", doc.color)}>
                            <FileText className="h-4 w-4" />
                        </div>

                        <div className="flex-1 min-w-0">
                            <h4 className="text-[0.8rem] font-medium text-white truncate">{doc.name}</h4>
                            <div className="flex items-center gap-2 mt-0.5">
                                <span className="text-[0.6rem] text-zinc-500 font-medium">{doc.size}</span>
                                <span className="h-0.5 w-0.5 rounded-full bg-zinc-700" />
                                <span className="text-[0.6rem] text-zinc-500 font-medium">{doc.date}</span>
                            </div>
                        </div>

                        <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button className="p-1 text-zinc-500 hover:text-white transition-colors">
                                <Download className="h-3.5 w-3.5" />
                            </button>
                            <button className="p-1 text-zinc-500 hover:text-white transition-colors">
                                <MoreVertical className="h-3.5 w-3.5" />
                            </button>
                        </div>
                    </motion.div>
                ))}
            </div>

            <Link
                href="/documents"
                className="mt-4 flex items-center justify-center gap-1.5 w-full py-2 rounded-lg border border-dashed border-white/10 text-[0.7rem] text-zinc-500 hover:text-white hover:border-teal-accent/30 hover:bg-teal-accent/5 transition-all duration-200"
            >
                <Plus className="h-3.5 w-3.5" />
                <span className="font-semibold uppercase tracking-wider">Upload Document</span>
            </Link>
        </div>
    );
}
