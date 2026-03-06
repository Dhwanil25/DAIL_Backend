"use client";

import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAnalytics } from '@/lib/hooks';
import { MOCK_STATS } from '@/lib/mock-data';

export function KPIStats() {
    const { data: analytics } = useAnalytics();

    const stats = analytics
        ? [
            { label: 'Total Cases', value: analytics.totals.cases.toLocaleString(), change: '+12', trend: 'up' as const },
            { label: 'Total Dockets', value: analytics.totals.dockets.toLocaleString(), change: '+28', trend: 'up' as const },
            { label: 'Documents', value: analytics.totals.documents.toLocaleString(), change: '+96', trend: 'up' as const },
            { label: 'Secondary Sources', value: analytics.totals.secondary_sources.toLocaleString(), change: '+6', trend: 'up' as const },
        ]
        : MOCK_STATS;

    return (
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4 lg:gap-4">
            {stats.map((stat, idx) => (
                <motion.div
                    key={stat.label}
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.07 }}
                    className="group relative overflow-hidden rounded-xl bg-navy-surface p-4 border border-white/5 hover:border-teal-accent/20 transition-all duration-300"
                >
                    <div className="flex flex-col gap-1">
                        <p className="text-[0.65rem] font-semibold text-zinc-500 uppercase tracking-widest">{stat.label}</p>
                        <h3 className="text-2xl font-bold tracking-tight text-white">{stat.value}</h3>
                        <div className="flex items-center gap-1">
                            {stat.trend === 'up' ? (
                                <TrendingUp className="h-3 w-3 text-emerald-500" />
                            ) : (
                                <TrendingDown className="h-3 w-3 text-rose-500" />
                            )}
                            <span className={cn(
                                "text-[0.65rem] font-bold",
                                stat.trend === 'up' ? "text-emerald-500" : "text-rose-500"
                            )}>
                                {stat.change}
                            </span>
                            <span className="text-[0.6rem] text-zinc-600">this month</span>
                        </div>
                    </div>
                </motion.div>
            ))}
        </div>
    );
}
