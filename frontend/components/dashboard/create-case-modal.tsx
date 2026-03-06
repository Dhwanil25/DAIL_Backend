"use client";

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Plus, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CreateCaseModalProps {
    isOpen: boolean;
    onClose: () => void;
}

interface FormErrors {
    title?: string;
    court?: string;
    description?: string;
}

const COURTS = ['Supreme Court', 'High Court', 'District Court', 'Tribunal', 'Federal Court'];
const STATUSES = ['Open', 'In Progress', 'Appeal'];

export function CreateCaseModal({ isOpen, onClose }: CreateCaseModalProps) {
    const [form, setForm] = useState({
        title: '',
        court: '',
        status: 'Open',
        description: '',
    });
    const [errors, setErrors] = useState<FormErrors>({});
    const [submitted, setSubmitted] = useState(false);

    function validate(): FormErrors {
        const e: FormErrors = {};
        if (!form.title.trim()) e.title = 'Case title is required';
        else if (form.title.length < 3) e.title = 'Title must be at least 3 characters';
        if (!form.court) e.court = 'Please select a court';
        if (!form.description.trim()) e.description = 'Description is required';
        else if (form.description.length < 10) e.description = 'Description must be at least 10 characters';
        return e;
    }

    function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        const validationErrors = validate();
        setErrors(validationErrors);

        if (Object.keys(validationErrors).length === 0) {
            setSubmitted(true);
            setTimeout(() => {
                setSubmitted(false);
                setForm({ title: '', court: '', status: 'Open', description: '' });
                onClose();
            }, 1500);
        }
    }

    function handleChange(field: string, value: string) {
        setForm((prev) => ({ ...prev, [field]: value }));
        if (errors[field as keyof FormErrors]) {
            setErrors((prev) => ({ ...prev, [field]: undefined }));
        }
    }

    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={onClose}
                    className="fixed inset-0 bg-navy-deep/70 backdrop-blur-sm"
                />

                <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: 20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: 20 }}
                    className="relative w-full max-w-lg rounded-xl bg-navy-surface border border-white/10 shadow-2xl overflow-hidden"
                >
                    {/* Header */}
                    <div className="flex items-center justify-between px-5 py-4 border-b border-white/5">
                        <div className="flex items-center gap-2">
                            <Plus className="h-4 w-4 text-teal-accent" />
                            <h2 className="text-sm font-bold text-white">Create New Case</h2>
                        </div>
                        <button
                            onClick={onClose}
                            className="p-1 text-zinc-500 hover:text-white transition-colors"
                        >
                            <X className="h-4 w-4" />
                        </button>
                    </div>

                    {/* Success State */}
                    {submitted ? (
                        <div className="p-8 text-center">
                            <motion.div
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500/10 border border-emerald-500/20"
                            >
                                <svg className="h-6 w-6 text-emerald-400" fill="none" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                                </svg>
                            </motion.div>
                            <p className="text-sm font-semibold text-white">Case Created Successfully</p>
                            <p className="text-xs text-zinc-500 mt-1">Redirecting...</p>
                        </div>
                    ) : (
                        <form onSubmit={handleSubmit} className="p-5 space-y-4">
                            {/* Title */}
                            <div>
                                <label className="block text-xs font-semibold text-zinc-400 mb-1.5">Case Title *</label>
                                <input
                                    type="text"
                                    value={form.title}
                                    onChange={(e) => handleChange('title', e.target.value)}
                                    placeholder="e.g. State vs. Johnson"
                                    className={cn(
                                        "w-full rounded-lg bg-navy-deep border px-3 py-2 text-sm text-white placeholder-zinc-600 outline-none transition-all",
                                        errors.title ? "border-rose-500/50 focus:border-rose-500" : "border-white/10 focus:border-teal-accent/40"
                                    )}
                                />
                                {errors.title && (
                                    <p className="flex items-center gap-1 mt-1 text-[0.65rem] text-rose-400">
                                        <AlertCircle className="h-3 w-3" />{errors.title}
                                    </p>
                                )}
                            </div>

                            {/* Court + Status Row */}
                            <div className="grid grid-cols-2 gap-3">
                                <div>
                                    <label className="block text-xs font-semibold text-zinc-400 mb-1.5">Court *</label>
                                    <select
                                        value={form.court}
                                        onChange={(e) => handleChange('court', e.target.value)}
                                        className={cn(
                                            "w-full rounded-lg bg-navy-deep border px-3 py-2 text-sm text-white outline-none transition-all appearance-none",
                                            errors.court ? "border-rose-500/50" : "border-white/10 focus:border-teal-accent/40",
                                            !form.court && "text-zinc-600"
                                        )}
                                    >
                                        <option value="">Select court</option>
                                        {COURTS.map((c) => (
                                            <option key={c} value={c}>{c}</option>
                                        ))}
                                    </select>
                                    {errors.court && (
                                        <p className="flex items-center gap-1 mt-1 text-[0.65rem] text-rose-400">
                                            <AlertCircle className="h-3 w-3" />{errors.court}
                                        </p>
                                    )}
                                </div>
                                <div>
                                    <label className="block text-xs font-semibold text-zinc-400 mb-1.5">Status</label>
                                    <select
                                        value={form.status}
                                        onChange={(e) => handleChange('status', e.target.value)}
                                        className="w-full rounded-lg bg-navy-deep border border-white/10 px-3 py-2 text-sm text-white outline-none focus:border-teal-accent/40 transition-all appearance-none"
                                    >
                                        {STATUSES.map((s) => (
                                            <option key={s} value={s}>{s}</option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            {/* Description */}
                            <div>
                                <label className="block text-xs font-semibold text-zinc-400 mb-1.5">Description *</label>
                                <textarea
                                    value={form.description}
                                    onChange={(e) => handleChange('description', e.target.value)}
                                    placeholder="Describe the case details..."
                                    rows={3}
                                    className={cn(
                                        "w-full rounded-lg bg-navy-deep border px-3 py-2 text-sm text-white placeholder-zinc-600 outline-none transition-all resize-none",
                                        errors.description ? "border-rose-500/50 focus:border-rose-500" : "border-white/10 focus:border-teal-accent/40"
                                    )}
                                />
                                {errors.description && (
                                    <p className="flex items-center gap-1 mt-1 text-[0.65rem] text-rose-400">
                                        <AlertCircle className="h-3 w-3" />{errors.description}
                                    </p>
                                )}
                            </div>

                            {/* Actions */}
                            <div className="flex items-center justify-end gap-2 pt-2">
                                <button
                                    type="button"
                                    onClick={onClose}
                                    className="px-4 py-2 rounded-lg text-xs font-semibold text-zinc-400 hover:text-white bg-white/5 border border-white/5 hover:bg-white/10 transition-all"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 rounded-lg text-xs font-semibold text-navy-deep bg-teal-accent hover:bg-teal-300 transition-colors"
                                >
                                    Create Case
                                </button>
                            </div>
                        </form>
                    )}
                </motion.div>
            </div>
        </AnimatePresence>
    );
}
