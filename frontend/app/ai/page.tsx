"use client";

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Sparkles, Loader2, Zap } from 'lucide-react';
import { aiApi } from '@/lib/api';
import type { ChatMessage } from '@/types';

function renderMarkdown(text: string) {
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n- /g, '<br/>• ')
        .replace(/\n/g, '<br/>');
}

export default function AIAssistantPage() {
    const [messages, setMessages] = useState<ChatMessage[]>([
        { role: 'assistant', content: 'Hello! I can help you search, summarize, and analyze AI litigation cases in the LIA database. Ask me anything.' }
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isTyping]);

    const SUGGESTIONS = [
        'Summarize case LIA-2024-001',
        'Find cases about AI copyright',
        'What are the trends in AI litigation?',
    ];

    async function handleSend() {
        if (!input.trim() || isTyping) return;
        const userMsg: ChatMessage = { role: 'user', content: input.trim() };
        const newMessages = [...messages, userMsg];
        setMessages(newMessages);
        setInput('');
        setIsTyping(true);

        try {
            // Send full conversation history to AI endpoint
            const response = await aiApi.chat(
                newMessages.filter(m => m.role === 'user' || m.role === 'assistant')
                    .map(m => ({ role: m.role, content: m.content }))
            );

            const aiContent = typeof response === 'string'
                ? response
                : response?.response || response?.answer || response?.content || response?.message || JSON.stringify(response);

            setMessages(prev => [...prev, { role: 'assistant', content: aiContent }]);
        } catch (err: any) {
            // Fallback to local response if backend AI is unavailable
            const fallback = getFallbackResponse(userMsg.content);
            setMessages(prev => [...prev, { role: 'assistant', content: fallback }]);
        } finally {
            setIsTyping(false);
        }
    }

    function getFallbackResponse(query: string): string {
        const q = query.toLowerCase();
        if (q.includes('copyright') || q.includes('ai art'))
            return '**AI Copyright Cases Analysis:**\n- There are multiple cases dealing with AI-generated content ownership\n- Key issues include authorship, fair use, and training data rights\n- Most cases are still being litigated in federal courts';
        if (q.includes('trend') || q.includes('analysis'))
            return '**AI Litigation Trends:**\n- Cases have increased significantly since 2022\n- Copyright and intellectual property remain the dominant areas\n- Employment discrimination via algorithmic decision-making is growing\n- Class action filings are on the rise';
        if (q.includes('case') || q.includes('summarize'))
            return '**Case Summary:**\n- This case involves allegations related to AI technology\n- Multiple filings have been recorded in the docket\n- The current status is under review\n- Connect to the backend for real-time case data';
        return `I received your query about "${query}". To provide accurate results from the LIA database, please ensure the backend is running. In the meantime, you can browse cases, documents, and dockets from the sidebar.`;
    }

    return (
        <div className="flex flex-col h-[calc(100vh-7rem)] max-w-[900px] mx-auto">
            <div className="flex items-center gap-2 mb-4">
                <div className="p-1.5 rounded-lg bg-violet-500/10 border border-violet-500/20">
                    <Zap className="h-4 w-4 text-violet-400" />
                </div>
                <div>
                    <h1 className="text-lg font-bold text-white">AI Assistant</h1>
                    <p className="text-[0.7rem] text-zinc-500">Powered by GPT-4o via OpenRouter</p>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto space-y-4 pr-2 scrollbar-thin">
                {messages.map((msg, idx) => (
                    <motion.div
                        key={idx}
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div className={`max-w-[80%] rounded-xl px-4 py-3 text-[0.8rem] leading-relaxed ${msg.role === 'user'
                            ? 'bg-teal-accent/10 text-teal-100 border border-teal-accent/20'
                            : 'bg-white/[0.04] text-zinc-300 border border-white/5'
                            }`}>
                            {msg.role === 'assistant' ? (
                                <div className="space-y-1">
                                    <div className="flex items-center gap-1 text-[0.6rem] text-zinc-500 font-bold uppercase tracking-widest mb-2">
                                        <Sparkles className="h-3 w-3 text-teal-accent" />
                                        AI Response
                                    </div>
                                    <div dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }} />
                                </div>
                            ) : (
                                msg.content
                            )}
                        </div>
                    </motion.div>
                ))}

                <AnimatePresence>
                    {isTyping && (
                        <motion.div
                            initial={{ opacity: 0, y: 8 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0 }}
                            className="flex justify-start"
                        >
                            <div className="bg-white/[0.04] border border-white/5 rounded-xl px-4 py-3 flex items-center gap-2 text-[0.8rem] text-zinc-400">
                                <Loader2 className="h-3.5 w-3.5 animate-spin text-teal-accent" />
                                Thinking...
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {messages.length <= 1 && (
                    <div className="flex flex-wrap gap-2 justify-center pt-4">
                        {SUGGESTIONS.map(s => (
                            <button
                                key={s}
                                onClick={() => { setInput(s); }}
                                className="px-3 py-1.5 rounded-lg bg-white/5 text-[0.7rem] text-zinc-400 hover:text-teal-accent hover:bg-teal-accent/5 transition-all border border-white/5"
                            >
                                {s}
                            </button>
                        ))}
                    </div>
                )}
                <div ref={bottomRef} />
            </div>

            <div className="mt-4 relative">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Ask about AI litigation..."
                    className="w-full rounded-xl bg-navy-surface border border-white/10 px-4 py-3 text-[0.8rem] text-white placeholder-zinc-600 outline-none focus:border-teal-accent/40 transition-all pr-12"
                />
                <button
                    onClick={handleSend}
                    disabled={isTyping || !input.trim()}
                    className="absolute right-2 top-1.5 p-2 rounded-lg bg-teal-accent text-navy-deep hover:bg-teal-300 transition-colors disabled:opacity-30"
                >
                    <Send className="h-4 w-4" />
                </button>
            </div>
        </div>
    );
}
