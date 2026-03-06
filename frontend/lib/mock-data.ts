export const MOCK_STATS = [
    { label: 'Total Cases', value: '1,248', change: '+12', trend: 'up' },
    { label: 'Total Dockets', value: '3,876', change: '+28', trend: 'up' },
    { label: 'Documents', value: '7,542', change: '+96', trend: 'up' },
    { label: 'Secondary Sources', value: '634', change: '+6', trend: 'up' },
];

export const MOCK_CASES = [
    {
        id: 'LIA-2024-001',
        title: 'State vs. Johnson',
        court: 'Supreme Court',
        filedOn: '2024-04-18',
        status: 'Open',
        summary: 'The latest docket includes 3 filings: Motion to Dismiss (Apr 20), Court Order (Apr 22), Hearing Scheduled (May 5).',
    },
    {
        id: 'LIA-2024-002',
        title: 'Bank of Trust vs. Smith',
        court: 'High Court',
        filedOn: '2024-04-15',
        status: 'In Progress',
        summary: 'Discovery phase active. Multiple document extractions pending review.',
    },
    {
        id: 'LIA-2024-003',
        title: 'People vs. Anderson',
        court: 'District Court',
        filedOn: '2024-04-12',
        status: 'Closed',
        summary: 'Case concluded with settlement. AI trend analysis noted significant copyright implications.',
    },
    {
        id: 'LIA-2024-004',
        title: 'Estate of Brown',
        court: 'Supreme Court',
        filedOn: '2024-04-10',
        status: 'Appeal',
        summary: 'Appellate brief filed. AI summary highlights jurisdiction challenges.',
    },
    {
        id: 'LIA-2024-005',
        title: 'Reg. Commission vs. Green',
        court: 'Tribunal',
        filedOn: '2024-04-08',
        status: 'Open',
        summary: 'Initial complaint filed. Automated docket tracking enabled.',
    },
];

export const MOCK_TIMELINE = [
    { date: 'Apr 20', title: 'Motion to Dismiss — Filed', type: 'filing', color: 'bg-emerald-500' },
    { date: 'Apr 22', title: 'Court Order — Issued', type: 'order', color: 'bg-blue-500' },
    { date: 'Apr 25', title: 'Reply Due', type: 'deadline', color: 'bg-amber-500' },
    { date: 'May 5', title: 'Hearing Scheduled', type: 'hearing', color: 'bg-violet-500' },
];

export const MOCK_DOCUMENTS = [
    { name: 'Petition.pdf', size: '2.4 MB', date: 'Apr 18', color: 'text-blue-400' },
    { name: 'Evidence_01.pdf', size: '5.1 MB', date: 'Apr 19', color: 'text-rose-400' },
    { name: 'Order_0422.pdf', size: '1.2 MB', date: 'Apr 22', color: 'text-violet-400' },
];
