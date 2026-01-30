'use client';

import React, { useEffect, useState } from 'react';
import {
    Activity, CheckCircle, Video, ExternalLink,
    RefreshCw, TrendingUp, Eye, FileText, ChevronRight, X
} from 'lucide-react';
import { motion } from 'framer-motion';

export default function Dashboard() {
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

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
                        <h1 className="text-3xl md:text-4xl lg:text-5xl font-black mb-2 md:mb-3 tracking-tighter">
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
                        className="flex flex-col items-end gap-3 w-full md:w-auto"
                    >
                        <div className="glass-card px-4 py-3 rounded-2xl border-violet-500/20 bg-violet-500/5 flex items-center justify-between gap-4 w-full md:min-w-[240px]">
                            <div className="flex flex-col flex-1">
                                <span className="text-[10px] font-bold text-violet-400 uppercase tracking-widest opacity-80">Status</span>
                                <span className="text-xs md:text-sm font-bold text-white tracking-wide">{data?.engineStatus || 'Idle'}</span>
                            </div>
                            <div className={`w-2.5 h-2.5 rounded-full ${data?.engineStatus === 'Processing' ? 'bg-green-500 animate-pulse ring-4 ring-green-500/20' : 'bg-violet-500/60'}`} />
                        </div>
                        <button
                            onClick={fetchData}
                            className="button-outline group flex items-center justify-center gap-2 w-full md:w-auto text-xs font-bold tracking-wider"
                            disabled={loading}
                        >
                            <RefreshCw className={`w-3.5 h-3.5 text-violet-400 group-hover:rotate-180 transition-transform duration-700 ${loading ? 'animate-spin' : ''}`} />
                            <span>REFRESH</span>
                        </button>
                    </motion.div>
                </header>

                {/* Stats Grid */}
                <motion.div
                    initial={{ y: 20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ delay: 0.1 }}
                    className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
                >
                    <StatCard
                        title="Videos Processed"
                        value={stats.total}
                        icon={<Video />}
                        color="violet"
                    />
                    <StatCard
                        title="Success Rate"
                        value={`${stats.total > 0 ? 100 : 0}%`}
                        icon={<CheckCircle />}
                        color="emerald"
                    />
                    <StatCard
                        title="Last Activity"
                        value={stats.lastActivity === 'N/A' ? 'Never' : new Date(stats.lastActivity).toLocaleDateString()}
                        icon={<Activity />}
                        color="cyan"
                    />
                </motion.div>

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Activity Feed */}
                    <motion.div
                        initial={{ y: 20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        transition={{ delay: 0.2 }}
                        className="lg:col-span-2"
                    >
                        <div className="glass-card p-6 rounded-3xl border-white/10">
                            <div className="flex items-center justify-between mb-6">
                                <h2 className="text-xl font-bold tracking-tight">Recent Activity</h2>
                                <Activity className="w-5 h-5 text-fuchsia-500" />
                            </div>

                            <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
                                {activity.length === 0 ? (
                                    <div className="text-center py-12">
                                        <Video className="w-10 h-10 text-white/10 mx-auto mb-4" />
                                        <p className="text-white/40 font-medium text-sm">No videos processed yet</p>
                                    </div>
                                ) : (
                                    activity.map((row: any, i: number) => (
                                        <div key={i} className="glass-card p-4 rounded-xl border-white/5 hover:border-white/20 transition-all group">
                                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                                                <div className="flex items-start gap-3">
                                                    <div className="w-10 h-10 min-w-[40px] bg-violet-500/10 rounded-lg flex items-center justify-center group-hover:bg-violet-500/20 transition-colors">
                                                        <Video className="w-5 h-5 text-violet-300" />
                                                    </div>
                                                    <div className="min-w-0">
                                                        <a
                                                            href={row.originalLink}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="hover:text-violet-400 transition-colors"
                                                        >
                                                            <h3 className="text-sm font-bold tracking-tight text-white/90 truncate pr-4 hover:text-violet-400 transition-colors">{row.title}</h3>
                                                        </a>
                                                        <div className="flex items-center gap-2 mt-1">
                                                            <span className="text-white/40 text-[10px]">{row.timestamp}</span>
                                                            <span className="text-white/10 text-[10px]">•</span>
                                                            <a
                                                                href={row.originalLink}
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                                className="flex items-center gap-1 text-white/30 hover:text-violet-400 transition-colors"
                                                            >
                                                                <ExternalLink className="w-3 h-3" />
                                                                <span className="text-[9px] font-medium">SOURCE</span>
                                                            </a>
                                                        </div>
                                                    </div>
                                                </div>

                                                <div className="flex items-center gap-4 pl-13 sm:pl-0">
                                                    <div className="flex flex-wrap gap-1.5 max-w-[200px]">
                                                        {(row.platform || '').split(',').map((p: string, j: number) => (
                                                            <span key={j} className="text-[9px] font-medium px-2 py-0.5 bg-white/5 text-white/40 border border-white/5 rounded-[4px] tracking-wide uppercase">
                                                                {p.trim()}
                                                            </span>
                                                        ))}
                                                    </div>

                                                    <a
                                                        href={row.finalLink}
                                                        target="_blank"
                                                        rel="noopener"
                                                        className="button-primary px-3 py-1.5 text-[10px] flex items-center gap-1.5 ml-auto sm:ml-0 whitespace-nowrap"
                                                    >
                                                        <Eye className="w-3 h-3" />
                                                        <span className="font-bold tracking-wider">VIEW</span>
                                                    </a>
                                                </div>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    </motion.div>

                    {/* Sidebar Area */}
                    <motion.div
                        initial={{ y: 20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        transition={{ delay: 0.4 }}
                        className="space-y-8"
                    >
                        {/* Platform Distribution */}
                        <div className="glass-card p-6 rounded-3xl border-white/10">
                            <div className="flex items-center gap-3 mb-6">
                                <TrendingUp className="w-5 h-5 text-emerald-500" />
                                <h3 className="text-lg font-black tracking-tight">Platform Distribution</h3>
                            </div>

                            <div className="space-y-4">
                                {platformDistribution.length === 0 ? (
                                    <p className="text-white/40 text-sm text-center py-4">No data available</p>
                                ) : (
                                    platformDistribution.map((p: any, i: number) => (
                                        <div key={i} className="space-y-2">
                                            <div className="flex justify-between text-sm">
                                                <span className="text-white/80 font-medium">{p.name}</span>
                                                <span className="text-white/40">{p.value}</span>
                                            </div>
                                            <div className="w-full bg-white/10 rounded-full h-2">
                                                <motion.div
                                                    initial={{ width: 0 }}
                                                    animate={{ width: `${(p.value / stats.total) * 100}%` }}
                                                    transition={{ delay: 0.5 + i * 0.1, duration: 0.8 }}
                                                    className="bg-gradient-to-r from-violet-500 to-fuchsia-500 h-2 rounded-full"
                                                />
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>

                        {/* Google Sheets Link */}
                        <div className="glass-card p-6 rounded-3xl border-white/10 group cursor-pointer hover:border-white/20 transition-all">
                            <a
                                href={data?.spreadsheetId ? `https://docs.google.com/spreadsheets/d/${data.spreadsheetId}` : "https://docs.google.com/spreadsheets/d/1JTJzRwHIFe25MFFmOxofVNbymWUEr9M7VCM3F1zWlfA"}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center justify-between"
                            >
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 bg-emerald-500/20 rounded-xl flex items-center justify-center">
                                        <FileText className="w-5 h-5 text-emerald-500" />
                                    </div>
                                    <div>
                                        <h4 className="font-bold text-white/90">View Full Logs</h4>
                                        <p className="text-white/40 text-xs">Google Sheets</p>
                                    </div>
                                </div>
                                <ChevronRight className="w-5 h-5 text-white/40 group-hover:text-white transition-colors" />
                            </a>
                            <Activity className="absolute -bottom-6 -right-6 w-36 h-36 text-white/10 rotate-12 group-hover:rotate-45 group-hover:scale-110 transition-all duration-700" />
                        </div>
                    </motion.div>
                </div>
            </div >

        </div>
    );
}

function StatCard({ title, value, icon, color }: { title: string; value: any; icon: React.ReactNode; color: string }) {
    return (
        <motion.div
            variants={{
                hidden: { y: 20, opacity: 0 },
                show: { y: 0, opacity: 1 }
            }}
            className="glass-card p-5 rounded-2xl border-white/10 hover:border-white/20 transition-all group"
        >
            <div className="flex items-center justify-between mb-3">
                <div className={`w-10 h-10 bg-${color}-500/10 rounded-lg flex items-center justify-center group-hover:bg-${color}-500/20 transition-colors`}>
                    {React.cloneElement(icon as React.ReactElement, { className: "w-5 h-5" })}
                </div>
                <span className="text-xl md:text-2xl font-bold text-white tracking-tight group-hover:text-white transition-colors">{value}</span>
            </div>
            <h3 className="text-xs font-medium text-white/40 uppercase tracking-widest group-hover:text-white/60 transition-colors">{title}</h3>
        </motion.div>
    );
}
