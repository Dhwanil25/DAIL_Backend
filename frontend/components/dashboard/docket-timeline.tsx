"use client";

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { useDockets } from '@/lib/hooks';
import { MOCK_TIMELINE } from '@/lib/mock-data';
import Link from 'next/link';
import type { DocketResponse } from '@/types';

export function DocketTimeline() {
    const { data: docketsData } = useDockets({ limit: 4 });

    const displayTimeline = docketsData?.items
        ? docketsData.items.map((d: DocketResponse) => ({
            date: d.court || 'N/A',
            title: d.number || `Docket #${d.id}`,
            type: 'filing',
            color: d.id % 3 === 0 ? 'bg-emerald-500' : d.id % 3 === 1 ? 'bg-blue-500' : 'bg-violet-500',
        }))
        : MOCK_TIMELINE;

    return (
        <div className="flex flex-col rounded-xl bg-navy-surface border border-white/5 p-4 overflow-hidden">
            <div className="flex items-center justify-between mb-5">
                <h2 className="text-sm font-bold text-white">
                    Docket Timeline <span className="text-zinc-500 font-normal">— Recent Entries</span>
                </h2>
                <Link href="/dockets" className="text-teal-accent hover:text-teal-300 text-[0.7rem] font-semibold transition-colors">
                    View Details →
                </Link>
            </div>

            <div className="flex-1 space-y-5 relative">
                <div className="absolute left-[7px] top-1 bottom-1 w-px bg-white/10" />

                {displayTimeline.map((event, idx) => (
                    <motion.div
                        key={`${event.date}-${event.title}`}
                        initial={{ opacity: 0, x: -8 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className="relative flex items-center gap-4 group"
                    >
                        <div className={cn(
                            "relative z-10 h-3.5 w-3.5 rounded-full border-2 border-navy-surface",
                            event.color
                        )} />

                        <div className="flex flex-col">
                            <span className="text-[0.6rem] font-semibold text-zinc-500 uppercase tracking-widest">{event.date}</span>
                            <span className="text-[0.8rem] font-medium text-white group-hover:text-teal-accent transition-colors">
                                {event.title}
                            </span>
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    );
}
