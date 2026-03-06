import { HelpCircle, ExternalLink } from 'lucide-react';

export default function HelpPage() {
    return (
        <div className="space-y-5 max-w-[800px] mx-auto">
            <div>
                <h1 className="text-xl font-bold text-white">Help & Docs</h1>
                <p className="text-[0.8rem] text-zinc-500 mt-0.5">Documentation and resources for LIA platform</p>
            </div>

            <div className="space-y-3">
                {[
                    { title: 'Getting Started', desc: 'Learn the basics of the LIA platform' },
                    { title: 'API Reference', desc: 'Complete REST API documentation at /api/v1' },
                    { title: 'AI Features', desc: 'How to use AI-powered search, summarization, and analysis' },
                    { title: 'Data Import', desc: 'Import cases, dockets, and documents in bulk' },
                    { title: 'Keyboard Shortcuts', desc: '⌘K for command palette, ⌘/ for help' },
                ].map((item) => (
                    <div key={item.title} className="flex items-center gap-3 rounded-xl bg-navy-surface border border-white/5 p-4 hover:border-teal-accent/20 transition-all cursor-pointer group">
                        <HelpCircle className="h-4 w-4 text-zinc-500 group-hover:text-teal-accent shrink-0" />
                        <div className="flex-1">
                            <h3 className="text-[0.8rem] font-semibold text-white group-hover:text-teal-accent transition-colors">{item.title}</h3>
                            <p className="text-[0.7rem] text-zinc-500">{item.desc}</p>
                        </div>
                        <ExternalLink className="h-3.5 w-3.5 text-zinc-600 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                ))}
            </div>
        </div>
    );
}
