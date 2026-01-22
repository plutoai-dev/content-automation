'use client';

import React, { useEffect, useState } from 'react';
import {
    Activity, CheckCircle, Clock, Video, ExternalLink,
    RefreshCw, TrendingUp, ChevronRight, Layout, Zap, Eye,
    FileText, Hash, Send, X
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Dashboard() {
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedVideo, setSelectedVideo] = useState<any>(null);

    const fetchData = async () => {
        setLoading(true);
        try {
            const res = await fetch('/api/data');
            const result = await res.json();
            if (result.error) throw new Error(result.error);
            setData(result);
            setError(null);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 60000);
        return () => clearInterval(interval);
    }, []);

    // Animation Variants
    const container = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1
            }
        }
    };

    const item = {
        hidden: { y: 20, opacity: 0 },
        show: { y: 0, opacity: 1 }
    };

    if (loading && !data && !error) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-[#0a0f1e]">
                <motion.div
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="flex flex-col items-center gap-6"
                >
                    <RefreshCw className="w-12 h-12 text-violet-500 animate-spin" />
                    <p className="text-white/60 font-bold tracking-[0.2em] text-sm uppercase">Initializing Engine...</p>
                </motion.div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-[#0a0f1e]">
                <motion.div
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="flex flex-col items-center gap-6 text-center"
                >
                    <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center">
                        <X className="w-8 h-8 text-red-500" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-white mb-2">Connection Error</h2>
                        <p className="text-white/60 text-sm mb-4">Failed to load dashboard data</p>
                        <p className="text-red-400 text-xs font-mono bg-red-500/10 p-3 rounded max-w-md">{error}</p>
                    </div>
                    <button
                        onClick={fetchData}
                        className="button-primary"
                    >
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Retry
                    </button>
                </motion.div>
            </div>
        );
    }

    const { stats, activity, platformDistribution } = data || {
        stats: { total: 0, success: 0, processing: 0, lastActivity: 'N/A' },
        activity: [],
        platformDistribution: []
    };

    return (
        <div className="min-h-screen text-white pb-20 overflow-x-hidden">
            <div className="max-w-[1400px] mx-auto px-6 pt-10">
                {/* Header */}
                <header className="mb-12 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                    <motion.div
                        initial={{ x: -20, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                    >
                        <h1 className="text-5xl font-black mb-3 tracking-tighter">
                            <span className="text-gradient">CONTENT</span> ENGINE
                        </h1>
                        <div className="flex items-center gap-4">
                            <div className="flex items-center gap-2 px-3 py-1 bg-green-500/10 border border-green-500/30 rounded-full">
                                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.6)]" />
                                <span className="text-green-500 text-xs font-black uppercase tracking-widest">Active</span>
                            </div>
                            <p className="text-white/40 text-sm font-medium tracking-wide">Monitoring G-Drive Folder...</p>
                        </div>
                    </motion.div>

                    <motion.div
                        initial={{ x: 20, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        className="flex flex-col items-end gap-3"
                    >
                        <div className="glass-card px-6 py-3 rounded-2xl border-violet-500/20 bg-violet-500/5 flex items-center gap-4">
                            <div className="flex flex-col">
                                <span className="text-[10px] font-black text-violet-400 uppercase tracking-widest">Engine Status</span>
                                <span className="text-sm font-bold text-white max-w-[200px] truncate">{data?.engineStatus || 'Idle'}</span>
                            </div>
                            <div className="w-8 h-8 rounded-full bg-violet-500/20 flex items-center justify-center">
                                <Activity className="w-4 h-4 text-violet-400 animate-pulse" />
                            </div>
                        </div>
                        <button
                            onClick={fetchData}
                            className="button-outline group flex items-center gap-2"
                            disabled={loading}
                        >
                            <RefreshCw className={`w-4 h-4 text-violet-400 group-hover:rotate-180 transition-transform duration-700 ${loading ? 'animate-spin' : ''}`} />
                            <span>SYNC DATA</span>
                        </button>
                    </motion.div>
                </header>

                {/* Stats Grid */}
                <motion.div
                    variants={container}
                    initial="hidden"
                    animate="show"
                    className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12"
                >
                    <StatCard
                        title="Total Produced"
                        value={stats.total}
                        icon={<Video />}
                        trend="+12%"
                        color="violet"
                    />
                    <StatCard
                        title="Success Rate"
                        value={`${stats.total > 0 ? 100 : 0}%`}
                        icon={<CheckCircle />}
                        trend="Stable"
                        color="emerald"
                    />
                    <StatCard
                        title="Active Tasks"
                        value={stats.processing}
                        icon={<Zap />}
                        trend="None"
                        color="amber"
                    />
                    <StatCard
                        title="Pulse Rate"
                        value="60s"
                        icon={<Activity />}
                        trend="Optimized"
                        color="rose"
                    />
                </motion.div>

                {/* Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                    {/* Table Area */}
                    <motion.div
                        initial={{ y: 30, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        transition={{ delay: 0.4 }}
                        className="lg:col-span-8 space-y-6"
                    >
                        <div className="glass-card rounded-[2rem] overflow-hidden">
                            <div className="p-8 border-b border-white/5 flex items-center justify-between">
                                <h2 className="text-2xl font-black tracking-tight">Recent Executions</h2>
                                <Activity className="w-5 h-5 text-fuchsia-500 animate-pulse" />
                            </div>
                            <div className="overflow-x-auto">
                                <table className="w-full text-left">
                                    <thead>
                                        <tr className="bg-white/[0.02]">
                                            <th className="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-white/40">Resource</th>
                                            <th className="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-white/40">Progress</th>
                                            <th className="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-white/40">Channels</th>
                                            <th className="px-8 py-5 text-right text-[10px] font-black uppercase tracking-widest text-white/40">Action</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-white/5">
                                        {activity.length === 0 ? (
                                            <tr>
                                                <td colSpan={4} className="px-8 py-20 text-center">
                                                    <Video className="w-12 h-12 text-white/10 mx-auto mb-4" />
                                                    <p className="text-white/30 text-lg font-medium">Ready for input. Waiting on Drive polling...</p>
                                                </td>
                                            </tr>
                                        ) : (
                                            activity.map((row: any, i: number) => (
                                                <tr key={i} className="glass-hover group">
                                                    <td className="px-8 py-6">
                                                        <div className="flex items-center gap-4">
                                                            <div className="w-12 h-12 bg-white/5 rounded-2xl flex items-center justify-center text-white/40 group-hover:bg-violet-500/20 group-hover:text-violet-400 transition-all duration-500">
                                                                <Video className="w-6 h-6" />
                                                            </div>
                                                            <div className="flex flex-col">
                                                                <span className="text-sm font-black tracking-tight text-white/80 group-hover:text-white transition-colors">Video #{stats.total - i}</span>
                                                                <a href={row['original video link']} target="_blank" rel="noopener" className="text-[10px] font-bold text-white/30 hover:text-violet-400 flex items-center gap-1 transition-colors">
                                                                    SOURCE FILE <ExternalLink className="w-2 h-2" />
                                                                </a>
                                                            </div>
                                                        </div>
                                                    </td>
                                                    <td className="px-8 py-6">
                                                        <div className="flex items-center gap-2">
                                                            <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                                                            <span className="text-[10px] font-black uppercase tracking-wider text-emerald-400">Deployed</span>
                                                        </div>
                                                    </td>
                                                    <td className="px-8 py-6">
                                                        <div className="flex flex-wrap gap-2">
                                                            {(row.platform || '').split(',').map((p: string, j: number) => (
                                                                <span key={j} className="text-[9px] font-black px-2 py-1 bg-white/5 text-white/50 border border-white/10 rounded-md tracking-tighter uppercase whitespace-nowrap">
                                                                    {p.trim()}
                                                                </span>
                                                            ))}
                                                        </div>
                                                    </td>
                                                    <td className="px-8 py-6">
                                                        <div className="flex items-center justify-end gap-3">
                                                            <button
                                                                onClick={() => setSelectedVideo(row)}
                                                                className="p-2.5 rounded-xl bg-white/5 text-white/40 hover:bg-white/10 hover:text-white transition-all group/btn"
                                                                title="View Strategy"
                                                            >
                                                                <Layout className="w-4 h-4 group-hover/btn:scale-110 transition-transform" />
                                                            </button>
                                                            <a
                                                                href={row['final video link']}
                                                                target="_blank"
                                                                rel="noopener"
                                                                className="button-primary px-4 py-2 text-xs flex items-center gap-2"
                                                            >
                                                                <Eye className="w-4 h-4" />
                                                                <span>PREVIEW</span>
                                                            </a>
                                                        </div>
                                                    </td>
                                                </tr>
                                            ))
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </motion.div>

                    {/* Sidebar Area */}
                    <motion.div
                        initial={{ x: 30, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        transition={{ delay: 0.6 }}
                        className="lg:col-span-4 space-y-8"
                    >
                        {/* Distribution Card */}
                        <div className="glass-card p-8 rounded-[2rem]">
                            <div className="flex items-center justify-between mb-8">
                                <h2 className="text-xl font-black">Optimization</h2>
                                <TrendingUp className="w-5 h-5 text-emerald-500" />
                            </div>
                            <div className="space-y-6">
                                {platformDistribution.length === 0 ? (
                                    <div className="py-10 text-center border-2 border-dashed border-white/5 rounded-2xl">
                                        <p className="text-white/20 text-sm font-bold uppercase tracking-widest italic">Awaiting Metrics...</p>
                                    </div>
                                ) : (
                                    platformDistribution.map((p: any, i: number) => (
                                        <div key={i} className="group">
                                            <div className="flex justify-between items-end mb-3">
                                                <span className="text-xs font-black text-white/40 uppercase tracking-widest">{p.name}</span>
                                                <span className="text-sm font-bold text-violet-400">{p.value}</span>
                                            </div>
                                            <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden border border-white/5">
                                                <motion.div
                                                    initial={{ width: 0 }}
                                                    animate={{ width: `${(p.value / stats.total) * 100}%` }}
                                                    transition={{ duration: 1.5, ease: "easeOut" }}
                                                    className="bg-gradient-to-r from-violet-600 to-fuchsia-500 h-full rounded-full"
                                                />
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>

                        {/* Log Card */}
                        <div className="bg-gradient-to-br from-indigo-600 to-violet-800 p-8 rounded-[2rem] shadow-[0_20px_50px_rgba(99,102,241,0.3)] relative overflow-hidden group">
                            <div className="relative z-10">
                                <h3 className="text-2xl font-black mb-3 tracking-tight">Full Visibility</h3>
                                <p className="text-white/60 text-sm font-medium mb-8 leading-relaxed italic">Access granular execution logs and transcription metadata in the cloud.</p>
                                <a
                                    href={data?.spreadsheetId ? `https://docs.google.com/spreadsheets/d/${data.spreadsheetId}` : "https://docs.google.com/spreadsheets/d/1JTJzRwHIFe25MFFmOxofVNbymWUEr9M7VCM3F1zWlfA"}
                                    target="_blank"
                                    rel="noopener"
                                    className="flex items-center justify-center gap-3 w-full py-4 bg-white text-indigo-700 rounded-2xl font-black shadow-xl hover:scale-[1.03] transition-all"
                                >
                                    <span>LOGS SPREADSHEET</span>
                                    <ChevronRight className="w-5 h-5" />
                                </a>
                            </div>
                            <Activity className="absolute -bottom-6 -right-6 w-36 h-36 text-white/10 rotate-12 group-hover:rotate-45 group-hover:scale-110 transition-all duration-700" />
                        </div>
                    </motion.div>
                </div>
            </div>

            {/* Strategic Details Modal */}
            <AnimatePresence>
                {selectedVideo && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-6">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setSelectedVideo(null)}
                            className="absolute inset-0 bg-black/80 backdrop-blur-md"
                        />
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0, y: 20 }}
                            animate={{ scale: 1, opacity: 1, y: 0 }}
                            exit={{ scale: 0.9, opacity: 0, y: 20 }}
                            className="relative w-full max-w-3xl glass-card rounded-[2.5rem] shadow-[0_40px_100px_rgba(0,0,0,0.8)] overflow-hidden"
                        >
                            <div className="p-8 border-b border-white/10 flex items-center justify-between">
                                <div className="flex items-center gap-4">
                                    <div className="p-3 bg-violet-500/20 text-violet-400 rounded-2xl">
                                        <Zap className="w-6 h-6" />
                                    </div>
                                    <h2 className="text-3xl font-black tracking-tighter uppercase">Content Strategy</h2>
                                </div>
                                <button
                                    onClick={() => setSelectedVideo(null)}
                                    className="p-3 bg-white/5 hover:bg-white/10 text-white/40 hover:text-white rounded-2xl transition-all"
                                >
                                    <X className="w-6 h-6" />
                                </button>
                            </div>

                            <div className="p-8 space-y-10">
                                {/* Title Section */}
                                <section className="space-y-4">
                                    <div className="flex items-center gap-2 text-violet-400">
                                        <FileText className="w-4 h-4" />
                                        <span className="text-[10px] font-black uppercase tracking-widest">Headline</span>
                                    </div>
                                    <p className="text-2xl font-black text-white leading-tight">
                                        {selectedVideo['content strategy']?.split('\n\n')[0].replace('TITLE:', '').trim() || 'No Title Available'}
                                    </p>
                                </section>

                                {/* Caption Section */}
                                <section className="space-y-4">
                                    <div className="flex items-center gap-2 text-fuchsia-400">
                                        <Send className="w-4 h-4" />
                                        <span className="text-[10px] font-black uppercase tracking-widest">Caption</span>
                                    </div>
                                    <div className="p-6 bg-white/5 rounded-3xl border border-white/5">
                                        <p className="text-white/70 leading-relaxed font-medium">
                                            {selectedVideo['content strategy']?.split('\n\n')[1].replace('CAPTION:', '').trim() || 'No Caption Available'}
                                        </p>
                                    </div>
                                </section>

                                {/* Hashtags Section */}
                                <section className="space-y-4">
                                    <div className="flex items-center gap-2 text-amber-400">
                                        <Hash className="w-4 h-4" />
                                        <span className="text-[10px] font-black uppercase tracking-widest">Optimization</span>
                                    </div>
                                    <div className="flex flex-wrap gap-2 text-amber-400 font-bold">
                                        {selectedVideo['content strategy']?.split('\n\n')[2].replace('HASHTAGS:', '').trim() || '#automation'}
                                    </div>
                                </section>
                            </div>

                            <div className="p-8 bg-white/[0.02] flex items-center justify-end border-t border-white/10">
                                <a
                                    href={selectedVideo['final video link']}
                                    target="_blank"
                                    rel="noopener"
                                    className="button-primary flex items-center gap-3 px-8"
                                >
                                    <Eye className="w-5 h-5" />
                                    <span>REPLAY EXECUTION</span>
                                </a>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
}

function StatCard({ title, value, icon, trend, color }: any) {
    const colors: any = {
        violet: 'border-violet-500/20 text-violet-500 bg-violet-500/10',
        emerald: 'border-emerald-500/20 text-emerald-500 bg-emerald-500/10',
        amber: 'border-amber-500/20 text-amber-500 bg-amber-500/10',
        rose: 'border-rose-500/20 text-rose-500 bg-rose-500/10',
    };

    return (
        <motion.div
            whileHover={{ y: -5, scale: 1.02 }}
            className="glass-card p-8 rounded-[2rem] group"
        >
            <div className="flex items-center justify-between mb-8">
                <div className={`p-4 rounded-2xl ${colors[color]} border transition-colors group-hover:scale-110 duration-500`}>
                    {React.cloneElement(icon, { className: 'w-7 h-7' })}
                </div>
                <div className="flex flex-col items-end">
                    <span className="text-[10px] font-black text-white/20 uppercase tracking-[0.2em] mb-1">Pulse</span>
                    <span className={`text-[10px] font-black uppercase ${color === 'rose' ? 'text-rose-400' : 'text-emerald-400'}`}>{trend}</span>
                </div>
            </div>
            <p className="text-xs font-black text-white/30 mb-2 uppercase tracking-widest">{title}</p>
            <h3 className="text-4xl font-black text-white tracking-tighter">{value}</h3>
        </motion.div>
    );
}
