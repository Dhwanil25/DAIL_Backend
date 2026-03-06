"use client";

import { motion } from 'framer-motion';
import { BarChart3, TrendingUp } from 'lucide-react';
import { useAnalytics } from '@/lib/hooks';
import {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    PieChart,
    Pie,
    Cell,
    Legend,
} from 'recharts';

const CHART_COLORS = ['#14F1D9', '#7C3AED', '#10B981', '#F59E0B', '#EF4444', '#3B82F6', '#EC4899', '#8B5CF6'];

const FALLBACK_METRICS = [
    { label: 'Total Cases', value: '1,248' },
    { label: 'Open Cases', value: '312' },
    { label: 'Total Documents', value: '7,542' },
    { label: 'Secondary Sources', value: '634' },
];

export default function AnalyticsPage() {
    const { data: analytics, isLoading } = useAnalytics();

    const metrics = analytics
        ? [
            { label: 'Total Cases', value: analytics.totals.cases.toLocaleString() },
            { label: 'Total Dockets', value: analytics.totals.dockets.toLocaleString() },
            { label: 'Total Documents', value: analytics.totals.documents.toLocaleString() },
            { label: 'Secondary Sources', value: analytics.totals.secondary_sources.toLocaleString() },
        ]
        : FALLBACK_METRICS;

    return (
        <div className="space-y-5 max-w-[1600px] mx-auto">
            <div>
                <h1 className="text-xl font-bold text-white">Analytics</h1>
                <p className="text-[0.8rem] text-zinc-500 mt-0.5">
                    {analytics ? 'Live database statistics' : 'Dashboard insights and reporting'}
                </p>
            </div>

            {/* Metric Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                {metrics.map((m, idx) => (
                    <motion.div
                        key={m.label}
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.05 }}
                        className="rounded-xl bg-navy-surface border border-white/5 p-4 hover:border-teal-accent/20 transition-all"
                    >
                        <p className="text-[0.6rem] font-semibold text-zinc-500 uppercase tracking-widest">{m.label}</p>
                        <h3 className="text-2xl font-bold text-white mt-1">{m.value}</h3>
                    </motion.div>
                ))}
            </div>

            {isLoading ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div className="rounded-xl bg-navy-surface border border-white/5 p-5 h-80 animate-pulse" />
                    <div className="rounded-xl bg-navy-surface border border-white/5 p-5 h-80 animate-pulse" />
                </div>
            ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {/* Yearly Filings Bar Chart */}
                    <div className="rounded-xl bg-navy-surface border border-white/5 p-5">
                        <h3 className="text-[0.8rem] font-bold text-white mb-4 flex items-center gap-2">
                            <TrendingUp className="h-4 w-4 text-teal-accent" />
                            Cases Filed by Year
                        </h3>
                        {analytics?.yearly_filings && analytics.yearly_filings.length > 0 ? (
                            <ResponsiveContainer width="100%" height={250}>
                                <BarChart data={analytics.yearly_filings}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                                    <XAxis dataKey="year" tick={{ fill: '#71717a', fontSize: 11 }} />
                                    <YAxis tick={{ fill: '#71717a', fontSize: 11 }} />
                                    <Tooltip
                                        contentStyle={{ background: '#111827', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }}
                                        labelStyle={{ color: '#fff' }}
                                        itemStyle={{ color: '#14F1D9' }}
                                    />
                                    <Bar dataKey="count" fill="#14F1D9" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="h-[250px] flex items-center justify-center text-zinc-600 text-[0.8rem]">
                                No yearly data available — start the backend to see real analytics
                            </div>
                        )}
                    </div>

                    {/* Status Breakdown Pie Chart */}
                    <div className="rounded-xl bg-navy-surface border border-white/5 p-5">
                        <h3 className="text-[0.8rem] font-bold text-white mb-4 flex items-center gap-2">
                            <BarChart3 className="h-4 w-4 text-violet-400" />
                            Case Status Distribution
                        </h3>
                        {analytics?.status_breakdown && analytics.status_breakdown.length > 0 ? (
                            <ResponsiveContainer width="100%" height={250}>
                                <PieChart>
                                    <Pie
                                        data={analytics.status_breakdown.filter(s => !(s.status?.toLowerCase() === 'active' && s.count === 1))}
                                        dataKey="count"
                                        nameKey="status"
                                        cx="50%"
                                        cy="50%"
                                        outerRadius={80}
                                        label={({ name, percent }) => {
                                            const pct = ((percent ?? 0) * 100).toFixed(1);
                                            return pct === '0.0' ? '' : `${name} ${pct}%`;
                                        }}
                                        labelLine={{ stroke: '#71717a' }}
                                    >
                                        {analytics.status_breakdown
                                            .filter(s => !(s.status?.toLowerCase() === 'active' && s.count === 1))
                                            .map((_, idx) => (
                                                <Cell key={idx} fill={CHART_COLORS[idx % CHART_COLORS.length]} />
                                            ))}
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{ background: '#111827', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }}
                                        labelStyle={{ color: '#fff' }}
                                        itemStyle={{ color: '#fff' }}
                                    />
                                    <Legend
                                        wrapperStyle={{ fontSize: '0.65rem', color: '#a1a1aa' }}
                                    />
                                </PieChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="h-[250px] flex items-center justify-center text-zinc-600 text-[0.8rem]">
                                No status data available — start the backend to see real analytics
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Area of Application Breakdown */}
            {analytics?.area_breakdown && analytics.area_breakdown.length > 0 && (
                <div className="rounded-xl bg-navy-surface border border-white/5 p-5">
                    <h3 className="text-[0.8rem] font-bold text-white mb-4">
                        Top Areas of Application
                    </h3>
                    <div className="space-y-2">
                        {analytics.area_breakdown.slice(0, 10).map((area, idx) => (
                            <div key={area.area} className="flex items-center gap-3">
                                <span className="text-[0.7rem] text-zinc-400 w-48 truncate">{area.area}</span>
                                <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                                    <motion.div
                                        initial={{ width: 0 }}
                                        animate={{ width: `${(area.count / analytics.area_breakdown[0].count) * 100}%` }}
                                        transition={{ delay: idx * 0.05 }}
                                        className="h-full rounded-full"
                                        style={{ background: CHART_COLORS[idx % CHART_COLORS.length] }}
                                    />
                                </div>
                                <span className="text-[0.65rem] text-zinc-500 font-mono w-8 text-right">{area.count}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
