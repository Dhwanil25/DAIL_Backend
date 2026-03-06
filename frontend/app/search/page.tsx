"use client";

import { useState, Suspense, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
    Search as SearchIcon,
    Briefcase,
    BookOpen,
    FileText,
    Library,
    X,
    ExternalLink,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useCases, useDockets, useDocuments, useSecondarySources, useAnalytics } from '@/lib/hooks';
import { useSearchParams } from 'next/navigation';
import type { CaseResponse, DocketResponse, DocumentResponse, SecondarySourceResponse } from '@/types';

type Category = 'all' | 'cases' | 'dockets' | 'documents' | 'sources';

const CATEGORIES: { key: Category; label: string; icon: any }[] = [
    { key: 'all', label: 'All', icon: SearchIcon },
    { key: 'cases', label: 'Cases', icon: Briefcase },
    { key: 'dockets', label: 'Dockets', icon: BookOpen },
    { key: 'documents', label: 'Documents', icon: FileText },
    { key: 'sources', label: 'Sources', icon: Library },
];

interface SearchResult {
    id: string;
    type: 'case' | 'docket' | 'document' | 'source';
    title: string;
    subtitle: string;
    detail?: string;
    link?: string | null;
    badge?: string;
    badgeColor: string;
}

function StatCard({ label, value, icon: Icon, color }: { label: string; value: number | string; icon: any; color: string }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-xl bg-navy-surface border border-white/5 p-4 flex items-center gap-3"
        >
            <div className={cn('p-2 rounded-lg', color)}>
                <Icon className="h-4 w-4" />
            </div>
            <div>
                <p className="text-[0.6rem] font-semibold text-zinc-500 uppercase tracking-widest">{label}</p>
                <p className="text-xl font-bold text-white">{typeof value === 'number' ? value.toLocaleString() : value}</p>
            </div>
        </motion.div>
    );
}

function SearchContent() {
    const searchParams = useSearchParams();
    const initialQ = searchParams.get('q') || '';

    const [query, setQuery] = useState(initialQ);
    const [category, setCategory] = useState<Category>('all');

    const { data: analytics } = useAnalytics();

    // All data fetched server-side with high limits after backend was updated
    const { data: casesData, isLoading: casesLoading } = useCases({
        limit: 500,
        q: query || undefined,
    });
    const { data: docketsData, isLoading: docketsLoading } = useDockets({ limit: 500 });
    const { data: documentsData, isLoading: docsLoading } = useDocuments({ limit: 1000 });
    const { data: sourcesData, isLoading: sourcesLoading } = useSecondarySources({ limit: 500 });

    const allLoading = casesLoading && docketsLoading && docsLoading && sourcesLoading;
    const anyLoading = casesLoading || docketsLoading || docsLoading || sourcesLoading;

    const allResults = useMemo(() => {
        const results: SearchResult[] = [];
        const q = query.toLowerCase();

        if (category === 'all' || category === 'cases') {
            (casesData?.items || []).forEach((c: CaseResponse) => {
                results.push({
                    id: `case-${c.id}`,
                    type: 'case',
                    title: c.caption,
                    subtitle: [c.current_jurisdiction || c.jurisdiction_filed, c.date_action_filed].filter(Boolean).join(' · '),
                    detail: c.brief_description || c.summary_facts_activity || undefined,
                    badge: c.status_disposition || 'Case',
                    badgeColor: 'bg-teal-accent/10 text-teal-accent border-teal-accent/20',
                });
            });
        }

        if (category === 'all' || category === 'dockets') {
            (docketsData?.items || []).filter((d: DocketResponse) => {
                if (!q) return true;
                return `${d.number || ''} ${d.court || ''}`.toLowerCase().includes(q);
            }).forEach((d: DocketResponse) => {
                results.push({
                    id: `docket-${d.id}`,
                    type: 'docket',
                    title: d.number || `Docket #${d.id}`,
                    subtitle: d.court || 'Unknown court',
                    link: d.link,
                    badge: 'Docket',
                    badgeColor: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
                });
            });
        }

        if (category === 'all' || category === 'documents') {
            (documentsData?.items || []).filter((d: DocumentResponse) => {
                if (!q) return true;
                return `${d.cite_or_reference || ''} ${d.document || ''} ${d.court || ''}`.toLowerCase().includes(q);
            }).forEach((d: DocumentResponse) => {
                results.push({
                    id: `doc-${d.id}`,
                    type: 'document',
                    title: d.cite_or_reference || d.document || `Document #${d.id}`,
                    subtitle: [d.court, d.date].filter(Boolean).join(' · '),
                    link: d.link,
                    badge: 'Document',
                    badgeColor: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
                });
            });
        }

        if (category === 'all' || category === 'sources') {
            (sourcesData?.items || []).filter((s: SecondarySourceResponse) => {
                if (!q) return true;
                return `${s.secondary_source_title || ''}`.toLowerCase().includes(q);
            }).forEach((s: SecondarySourceResponse) => {
                results.push({
                    id: `source-${s.id}`,
                    type: 'source',
                    title: s.secondary_source_title || `Source #${s.id}`,
                    subtitle: `Case #${s.case_number}`,
                    link: s.secondary_source_link,
                    badge: 'Source',
                    badgeColor: 'bg-violet-500/10 text-violet-400 border-violet-500/20',
                });
            });
        }

        return results;
    }, [query, category, casesData, docketsData, documentsData, sourcesData]);

    const counts = useMemo(() => {
        const q = query.toLowerCase();
        return {
            cases: casesData?.items?.length || 0,
            dockets: (docketsData?.items || []).filter((d: DocketResponse) =>
                !q || `${d.number || ''} ${d.court || ''}`.toLowerCase().includes(q)
            ).length,
            documents: (documentsData?.items || []).filter((d: DocumentResponse) =>
                !q || `${d.cite_or_reference || ''} ${d.document || ''} ${d.court || ''}`.toLowerCase().includes(q)
            ).length,
            sources: (sourcesData?.items || []).filter((s: SecondarySourceResponse) =>
                !q || `${s.secondary_source_title || ''}`.toLowerCase().includes(q)
            ).length,
        };
    }, [query, casesData, docketsData, documentsData, sourcesData]);

    const totalCount = counts.cases + counts.dockets + counts.documents + counts.sources;

    const iconMap = { case: Briefcase, docket: BookOpen, document: FileText, source: Library };

    return (
        <div className="space-y-5 max-w-[1100px] mx-auto">
            {/* Header */}
            <div>
                <h1 className="text-xl font-bold text-white">Search</h1>
                <p className="text-[0.8rem] text-zinc-500 mt-0.5">
                    Search across all cases, dockets, documents, and secondary sources
                </p>
            </div>

            {/* Stat cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                <StatCard label="Total Cases" value={analytics?.totals.cases ?? '—'} icon={Briefcase} color="bg-teal-accent/10 text-teal-accent" />
                <StatCard label="Total Dockets" value={analytics?.totals.dockets ?? '—'} icon={BookOpen} color="bg-blue-500/10 text-blue-400" />
                <StatCard label="Documents" value={analytics?.totals.documents ?? '—'} icon={FileText} color="bg-rose-500/10 text-rose-400" />
                <StatCard label="Secondary Sources" value={analytics?.totals.secondary_sources ?? '—'} icon={Library} color="bg-violet-500/10 text-violet-400" />
            </div>

            {/* Search bar */}
            <div className="relative">
                <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search for anything — cases, docket numbers, documents, sources..."
                    className="w-full rounded-xl bg-navy-surface py-3 pl-11 pr-12 text-[0.85rem] text-white placeholder-zinc-500 outline-none ring-1 ring-white/5 focus:ring-teal-accent/30 transition-all border border-white/5"
                    autoFocus
                />
                {query && (
                    <button
                        onClick={() => setQuery('')}
                        className="absolute right-4 top-1/2 -translate-y-1/2 p-1 text-zinc-500 hover:text-white transition-colors"
                    >
                        <X className="h-3.5 w-3.5" />
                    </button>
                )}
            </div>

            {/* Category tabs */}
            <div className="flex flex-wrap gap-1.5">
                {CATEGORIES.map(cat => {
                    const count = cat.key === 'all' ? totalCount : counts[cat.key as keyof typeof counts] || 0;
                    return (
                        <button
                            key={cat.key}
                            onClick={() => setCategory(cat.key)}
                            className={cn(
                                "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[0.7rem] font-semibold transition-all border",
                                category === cat.key
                                    ? "bg-teal-accent/10 text-teal-accent border-teal-accent/20"
                                    : "bg-white/5 text-zinc-400 border-white/5 hover:text-white"
                            )}
                        >
                            <cat.icon className="h-3 w-3" />
                            {cat.label}
                            <span className={cn(
                                "text-[0.55rem] font-bold px-1.5 py-0.5 rounded-full",
                                category === cat.key ? "bg-teal-accent/20 text-teal-accent" : "bg-white/5 text-zinc-500"
                            )}>
                                {count}
                            </span>
                        </button>
                    );
                })}
            </div>

            {/* Results count */}
            <div className="flex items-center justify-between">
                <p className="text-[0.65rem] text-zinc-500 font-semibold uppercase tracking-widest">
                    {allLoading ? 'Loading...' : `${allResults.length.toLocaleString()} result${allResults.length !== 1 ? 's' : ''}`}
                    {query && ` for \u201c${query}\u201d`}
                    {anyLoading && !allLoading && <span className="ml-1 text-zinc-600">(loading more…)</span>}
                </p>
                {anyLoading && (
                    <div className="flex gap-1">
                        {[0, 1, 2].map(i => (
                            <span key={i} className="h-1.5 w-1.5 rounded-full bg-teal-accent/40 animate-pulse" style={{ animationDelay: `${i * 150}ms` }} />
                        ))}
                    </div>
                )}
            </div>

            {/* Results list */}
            {allLoading ? (
                <div className="space-y-2">
                    {[...Array(8)].map((_, i) => (
                        <div key={i} className="rounded-xl bg-navy-surface border border-white/5 p-4 h-20 animate-pulse" />
                    ))}
                </div>
            ) : allResults.length > 0 ? (
                <div className="space-y-2">
                    {allResults.map((result, idx) => {
                        const Icon = iconMap[result.type];
                        return (
                            <motion.div
                                key={result.id}
                                initial={{ opacity: 0, y: 6 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: Math.min(idx * 0.01, 0.3) }}
                                className="flex items-start gap-3 rounded-xl bg-navy-surface border border-white/5 p-4 hover:border-teal-accent/20 transition-all cursor-pointer group"
                            >
                                <div className="p-1.5 rounded-md bg-white/5 mt-0.5 shrink-0">
                                    <Icon className="h-4 w-4 text-zinc-400 group-hover:text-teal-accent transition-colors" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2">
                                        <h3 className="text-[0.8rem] font-semibold text-white group-hover:text-teal-accent transition-colors truncate">
                                            {result.title}
                                        </h3>
                                        {result.link && (
                                            <a href={result.link} target="_blank" rel="noopener noreferrer"
                                                onClick={(e) => e.stopPropagation()}
                                                className="opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                                                <ExternalLink className="h-3 w-3 text-zinc-500 hover:text-teal-accent" />
                                            </a>
                                        )}
                                    </div>
                                    <p className="text-[0.7rem] text-zinc-500 mt-0.5">{result.subtitle}</p>
                                    {result.detail && (
                                        <p className="text-[0.7rem] text-zinc-400 mt-1 italic line-clamp-1">{result.detail}</p>
                                    )}
                                </div>
                                <span className={cn(
                                    "text-[0.55rem] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded-full border whitespace-nowrap shrink-0",
                                    result.badgeColor
                                )}>
                                    {result.badge}
                                </span>
                            </motion.div>
                        );
                    })}
                </div>
            ) : !anyLoading ? (
                <div className="text-center py-12 rounded-xl bg-navy-surface border border-white/5">
                    <SearchIcon className="h-6 w-6 text-zinc-700 mx-auto mb-2" />
                    <p className="text-[0.8rem] text-zinc-500">No results found.</p>
                    <p className="text-[0.7rem] text-zinc-600 mt-1">Try a different search term.</p>
                </div>
            ) : null}
        </div>
    );
}

export default function SearchPage() {
    return (
        <Suspense fallback={
            <div className="space-y-5 max-w-[1100px] mx-auto">
                <div className="h-8 w-32 bg-navy-surface rounded-lg animate-pulse" />
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                    {[...Array(4)].map((_, i) => <div key={i} className="h-20 bg-navy-surface rounded-xl animate-pulse" />)}
                </div>
                <div className="h-12 bg-navy-surface rounded-xl animate-pulse" />
            </div>
        }>
            <SearchContent />
        </Suspense>
    );
}
