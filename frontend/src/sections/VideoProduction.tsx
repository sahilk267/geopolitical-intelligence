// ============================================
// VIDEO PRODUCTION PIPELINE DASHBOARD
// Monitor and manage automated video generation
// ============================================

import { useState, useEffect } from 'react';
import { useAppStore } from '@/store';
import { api } from '@/lib/api';
import {
    Video,
    X,
    AlertCircle,
    CheckCircle2,
    Clock,
    Filter,
    Search,
    MoreVertical,
    Eye,
    Activity,
    Share2,
    Send,
    Youtube
} from 'lucide-react';
import type { VideoJob } from '@/types';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

export function VideoProduction() {
    const {
        videoJobs,
        videoPipelineStatus,
        fetchVideoJobs,
        fetchVideoPipelineStatus,
        cancelVideoJob,
        isFetching
    } = useAppStore();

    const [filterStatus, setFilterStatus] = useState<string>('all');
    const [searchQuery, setSearchQuery] = useState('');

    useEffect(() => {
        fetchVideoJobs();
        fetchVideoPipelineStatus();

        // Polling for updates if there are active jobs
        const activeJobs = videoJobs.some((j: VideoJob) => ['queued', 'processing', 'tts_generating', 'avatar_rendering', 'video_compositing'].includes(j.status));

        let interval: any;
        if (activeJobs) {
            interval = setInterval(() => {
                fetchVideoJobs();
                fetchVideoPipelineStatus();
            }, 5000);
        }

        return () => {
            if (interval) clearInterval(interval);
        };
    }, [fetchVideoJobs, fetchVideoPipelineStatus, videoJobs.length]);

    const filteredJobs = videoJobs.filter((job: VideoJob) => {
        const matchesStatus = filterStatus === 'all' || job.status === filterStatus;
        const matchesSearch = job.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
            (job.errorMessage && job.errorMessage.toLowerCase().includes(searchQuery.toLowerCase()));
        return matchesStatus && matchesSearch;
    });

    const handleDistribute = async (jobId: string) => {
        const AVAILABLE_PLATFORMS = ['telegram', 'youtube', 'facebook', 'instagram', 'twitter', 'linkedin', 'whatsapp'];
        const platforms = prompt(
            `Select platforms to distribute to (comma-separated):\n\nAvailable: ${AVAILABLE_PLATFORMS.join(', ')}\n\nOr use the Content Factory section for a better experience.`,
            'telegram'
        );
        if (!platforms) return;

        const platformList = platforms.split(',').map(p => p.trim().toLowerCase()).filter(p => AVAILABLE_PLATFORMS.includes(p));
        if (platformList.length === 0) {
            alert('No valid platforms selected.');
            return;
        }

        try {
            const job = videoJobs.find((j: VideoJob) => j.id === jobId);
            if (!job) {
                alert('Video job not found.');
                return;
            }

            const result = await api.post('/distribution/publish', {
                content_type: 'video',
                platforms: platformList,
                params: {
                    video_id: jobId,
                    title: `Intelligence Report: ${jobId.substring(0, 8)}`,
                    description: "Automated geopolitical intelligence update."
                }
            }) as any;

            alert('✅ Distribution triggered! Result: ' + JSON.stringify(result));
        } catch (err: any) {
            alert('❌ Distribution failed: ' + (err.message || 'Unknown error'));
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'completed': return <CheckCircle2 className="w-4 h-4 text-green-400" />;
            case 'failed': return <AlertCircle className="w-4 h-4 text-red-400" />;
            case 'cancelled': return <X className="w-4 h-4 text-slate-400" />;
            case 'queued': return <Clock className="w-4 h-4 text-amber-400" />;
            default: return <div className="w-4 h-4 rounded-full border-2 border-[#C7A84A] border-t-transparent animate-spin" />;
        }
    };

    const getStatusBadge = (status: string) => {
        const variants: Record<string, string> = {
            completed: 'bg-green-500/10 text-green-400 border-green-500/20',
            failed: 'bg-red-500/10 text-red-400 border-red-500/20',
            cancelled: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
            queued: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
            processing: 'bg-[#C7A84A]/10 text-[#C7A84A] border-[#C7A84A]/20',
        };
        return variants[status] || variants.processing;
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-white">Video Production</h2>
                    <p className="text-slate-400 text-sm">Monitor and manage automated video generation pipeline</p>
                </div>
                <Button
                    variant="outline"
                    onClick={() => { fetchVideoJobs(); fetchVideoPipelineStatus(); }}
                    disabled={isFetching}
                    className="border-slate-700 bg-slate-800/50 hover:bg-slate-700 text-slate-300"
                >
                    Refresh Status
                </Button>
            </div>

            {/* Pipeline Overview */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-slate-400">Total Jobs</p>
                                <h3 className="text-2xl font-bold text-white mt-1">{videoPipelineStatus?.totalJobs || 0}</h3>
                            </div>
                            <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400">
                                <Video className="w-5 h-5" />
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-slate-400">Processing</p>
                                <h3 className="text-2xl font-bold text-[#C7A84A] mt-1">{videoPipelineStatus?.processing || 0}</h3>
                            </div>
                            <div className="w-10 h-10 rounded-lg bg-[#C7A84A]/10 flex items-center justify-center text-[#C7A84A]">
                                <Activity className="w-5 h-5 animate-pulse" />
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-slate-400">Completed</p>
                                <h3 className="text-2xl font-bold text-green-400 mt-1">{videoPipelineStatus?.completed || 0}</h3>
                            </div>
                            <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center text-green-400">
                                <CheckCircle2 className="w-5 h-5" />
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-slate-400">Failed</p>
                                <h3 className="text-2xl font-bold text-red-400 mt-1">{videoPipelineStatus?.failed || 0}</h3>
                            </div>
                            <div className="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center text-red-400">
                                <AlertCircle className="w-5 h-5" />
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Filters & Actions */}
            <div className="flex flex-col md:flex-row gap-4 items-center justify-between bg-slate-800/30 p-4 rounded-xl border border-slate-700/50">
                <div className="flex items-center gap-4 w-full md:w-auto">
                    <div className="relative flex-1 md:w-64">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                        <input
                            type="text"
                            placeholder="Search by ID or error..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full pl-10 pr-4 py-2 bg-slate-900/50 border border-slate-700 rounded-lg text-sm text-white focus:outline-none focus:border-[#C7A84A]"
                        />
                    </div>
                    <div className="flex items-center gap-2">
                        <Filter className="w-4 h-4 text-slate-400" />
                        <select
                            value={filterStatus}
                            onChange={(e) => setFilterStatus(e.target.value)}
                            className="bg-slate-900/50 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-[#C7A84A]"
                        >
                            <option value="all">All Statuses</option>
                            <option value="queued">Queued</option>
                            <option value="processing">Processing</option>
                            <option value="completed">Completed</option>
                            <option value="failed">Failed</option>
                            <option value="cancelled">Cancelled</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* Main Jobs Table */}
            <Card className="bg-[#0B1F3A]/50 border-slate-700/50 overflow-hidden">
                <CardContent className="p-0">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-slate-900/50 border-b border-slate-700/50">
                                    <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Status</th>
                                    <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Job Details</th>
                                    <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Progress</th>
                                    <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Priority</th>
                                    <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Created</th>
                                    <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-700/50 text-white">
                                {filteredJobs.length === 0 ? (
                                    <tr>
                                        <td colSpan={6} className="px-6 py-12 text-center text-slate-400">
                                            <div className="flex flex-col items-center justify-center gap-2">
                                                <Video className="w-8 h-8 opacity-20" />
                                                <p>No video jobs found matching your criteria</p>
                                            </div>
                                        </td>
                                    </tr>
                                ) : (
                                    filteredJobs.map((job: VideoJob) => (
                                        <tr key={job.id} className="hover:bg-slate-800/30 transition-colors">
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <div className="flex items-center gap-2">
                                                    {getStatusIcon(job.status)}
                                                    <Badge variant="outline" className={cn("capitalize px-2 py-0", getStatusBadge(job.status))}>
                                                        {job.status.replace('_', ' ')}
                                                    </Badge>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex flex-col">
                                                    <span className="text-sm font-medium font-mono text-slate-300">ID: {job.id.substring(0, 8)}...</span>
                                                    <span className="text-xs text-slate-500">{job.resolution}</span>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 min-w-[200px]">
                                                <div className="space-y-1.5">
                                                    <div className="flex justify-between text-[10px] text-slate-400">
                                                        <span>{job.currentStage || 'Initializing'}</span>
                                                        <span>{Math.round(job.progress)}%</span>
                                                    </div>
                                                    <Progress value={job.progress} className="h-1.5 bg-slate-700" />
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <Badge variant="outline" className={cn(
                                                    "text-xs px-2 py-0 border",
                                                    job.priority === 2 ? "text-red-400 border-red-400/20" :
                                                        job.priority === 1 ? "text-amber-400 border-amber-400/20" :
                                                            "text-slate-400 border-slate-700"
                                                )}>
                                                    {job.priority === 2 ? 'Urgent' : job.priority === 1 ? 'High' : 'Normal'}
                                                </Badge>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                                                {new Date(job.createdAt).toLocaleString()}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-right">
                                                <div className="flex items-center justify-end gap-2">
                                                    {job.status === 'completed' && job.outputUrl && (
                                                        <>
                                                            <Button size="icon" variant="ghost" title="View Video" asChild>
                                                                <a href={job.outputUrl} target="_blank" rel="noopener noreferrer">
                                                                    <Eye className="w-4 h-4 text-blue-400" />
                                                                </a>
                                                            </Button>
                                                            <Button
                                                                size="icon"
                                                                variant="ghost"
                                                                title="Distribute Video"
                                                                onClick={() => handleDistribute(job.id)}
                                                            >
                                                                <Share2 className="w-4 h-4 text-sky-400" />
                                                            </Button>
                                                        </>
                                                    )}
                                                    {['queued', 'processing', 'tts_generating', 'avatar_rendering', 'video_compositing'].includes(job.status) && (
                                                        <Button
                                                            size="icon"
                                                            variant="ghost"
                                                            title="Cancel Job"
                                                            onClick={() => cancelVideoJob(job.id)}
                                                        >
                                                            <X className="w-4 h-4 text-red-400 hover:text-red-300" />
                                                        </Button>
                                                    )}
                                                    <Button size="icon" variant="ghost">
                                                        <MoreVertical className="w-4 h-4 text-slate-400" />
                                                    </Button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
