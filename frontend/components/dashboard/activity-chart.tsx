"use client";

import {
    LineChart,
    Line,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from 'recharts';

const data = [
    { name: 'Nov', cases: 120, docs: 210 },
    { name: 'Dec', cases: 180, docs: 150 },
    { name: 'Jan', cases: 250, docs: 310 },
    { name: 'Feb', cases: 190, docs: 250 },
    { name: 'Mar', cases: 310, docs: 280 },
    { name: 'Apr', cases: 280, docs: 390 },
];

export function ActivityChart() {
    return (
        <div className="h-[200px] w-full">
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data}>
                    <defs>
                        <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#14F1D9" stopOpacity={0.8} />
                            <stop offset="100%" stopColor="#14F1D9" stopOpacity={0.2} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
                    <XAxis
                        dataKey="name"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: '#4B5563', fontSize: 10, fontWeight: 600 }}
                        dy={10}
                    />
                    <Tooltip
                        cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                        contentStyle={{
                            backgroundColor: '#111827',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '8px',
                            fontSize: '12px',
                            color: '#fff'
                        }}
                    />
                    <Bar dataKey="cases" fill="url(#barGradient)" radius={[4, 4, 0, 0]} barSize={20} />
                    <Bar dataKey="docs" fill="#7C3AED" radius={[4, 4, 0, 0]} barSize={20} opacity={0.6} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
