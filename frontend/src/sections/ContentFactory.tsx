// ============================================
// CONTENT FACTORY — AI Content Production Pipeline
// Unified dashboard: Script → Voice → Video → Upload
// ============================================

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import {
    FileText,
    Mic,
    Video,
    Share2,
    Play,
    CheckCircle,
    XCircle,
    Loader2,
    Sparkles,
    ArrowRight,
    Download,
    Send,
    Youtube,
    Twitter,
    Facebook,
    Instagram,
    Linkedin,
    MessageSquare,
    Zap,
    Volume2,
    RefreshCw,
    Database,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface PipelineStatus {
    ai_configured: boolean;
    tts_engine: string;
    tts_configured: boolean;
    avatar_engine: string;
    avatar_configured: boolean;
}

interface DistPlatform {
    id: string;
    name: string;
    connected: boolean;
    channel_name?: string;
}

const PLATFORM_ICONS: Record<string, React.ElementType> = {
    telegram: Send,
    youtube: Youtube,
    twitter: Twitter,
    facebook: Facebook,
    instagram: Instagram,
    linkedin: Linkedin,
    whatsapp: MessageSquare,
};

const PLATFORM_COLORS: Record<string, string> = {
    telegram: 'text-sky-400',
    youtube: 'text-red-500',
    twitter: 'text-blue-400',
    facebook: 'text-blue-600',
    instagram: 'text-pink-500',
    linkedin: 'text-blue-700',
    whatsapp: 'text-emerald-500',
};

const TTS_INFO: Record<string, { label: string; badge: string; badgeClass: string }> = {
    edge_tts: { label: 'Edge-TTS', badge: '⭐ FREE', badgeClass: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' },
    piper: { label: 'Piper TTS', badge: '🔒 FREE OFFLINE', badgeClass: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
    gtts: { label: 'Google TTS', badge: '🆓 BASIC', badgeClass: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' },
    elevenlabs: { label: 'ElevenLabs', badge: '💰 PAID', badgeClass: 'bg-purple-500/20 text-purple-400 border-purple-500/30' },
};

export function ContentFactory() {
    // Pipeline state
    const [pipelineStatus, setPipelineStatus] = useState<PipelineStatus | null>(null);
    const [categories, setCategories] = useState<{ category: string; article_count: number }[]>([]);
    const [selectedCategory, setSelectedCategory] = useState('');
    const [selectedRegion, setSelectedRegion] = useState('Global');
    const [isRunning, setIsRunning] = useState(false);
    const [isFetchingSources, setIsFetchingSources] = useState(false);
    const [pipelineResult, setPipelineResult] = useState<any>(null);
    const [currentStep, setCurrentStep] = useState<number>(-1);

    // Distribution
    const [platforms, setPlatforms] = useState<DistPlatform[]>([]);
    const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
    const [loadingPlatforms, setLoadingPlatforms] = useState(false);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [statusData, catData] = await Promise.all([
                api.getPipelineCapabilities(),
                api.getReportCategories(),
            ]);
            setPipelineStatus(statusData as PipelineStatus);
            const cats = Array.isArray(catData) ? catData : (catData as any)?.categories || [];
            setCategories(cats);
            // Auto-select first category if none is selected
            if (cats.length > 0 && !selectedCategory) {
                setSelectedCategory(cats[0].category);
            }
        } catch (e) {
            console.error('Failed to load pipeline data:', e);
        }

        try {
            setLoadingPlatforms(true);
            const platData = await api.getDistributionPlatforms() as DistPlatform[];
            setPlatforms(platData);
            // Auto-select connected platforms
            setSelectedPlatforms(platData.filter(p => p.connected).map(p => p.id));
        } catch (e) {
            console.error('Failed to load platforms:', e);
        } finally {
            setLoadingPlatforms(false);
        }
    };

    const togglePlatform = (id: string) => {
        setSelectedPlatforms(prev =>
            prev.includes(id) ? prev.filter(p => p !== id) : [...prev, id]
        );
    };

    const handleFetchSources = async () => {
        setIsFetchingSources(true);
        try {
            await api.fetchAllSources();
            // Refresh category counts after fetch
            await loadData();
            // Show temporary success
            setPipelineResult({ error: null, success_msg: 'Successfully fetched latest intelligence from all connected sources! You can now run the factory.' });
            setTimeout(() => {
                if (!isRunning) setPipelineResult(null);
            }, 5000);
        } catch (err: any) {
            setPipelineResult({ error: 'Failed to fetch sources: ' + (err.message || 'Unknown error') });
        } finally {
            setIsFetchingSources(false);
        }
    };

    const handleRunPipeline = async () => {
        if (!selectedCategory) {
            alert('Please select a content category first.');
            return;
        }

        console.log('Running pipeline with:', { category: selectedCategory, region: selectedRegion, platforms: selectedPlatforms });

        setIsRunning(true);
        setPipelineResult(null);
        setCurrentStep(0);

        try {
            // Simulate step progression via timing (actual backend runs all steps)
            const stepTimer = setInterval(() => {
                setCurrentStep(prev => {
                    if (prev < 3) return prev + 1;
                    clearInterval(stepTimer);
                    return prev;
                });
            }, 3000);

            const result = await api.runFullPipeline(
                selectedCategory,
                selectedRegion,
                'default',
                true,
                true,
                selectedPlatforms.length > 0 ? selectedPlatforms : undefined
            );

            console.log('Pipeline result:', result);
            clearInterval(stepTimer);
            setCurrentStep(4); // Completed
            setPipelineResult(result);
        } catch (err: any) {
            console.error('Pipeline error:', err);
            setPipelineResult({ error: err.message || 'Pipeline failed' });
            setCurrentStep(-1);
        } finally {
            setIsRunning(false);
        }
    };

    const pipelineSteps = [
        { icon: FileText, label: 'Script Generation', desc: 'AI writes journalist-quality report', engine: 'LLM (Gemini/Ollama)' },
        { icon: Mic, label: 'Voice Synthesis', desc: 'Text-to-speech narration', engine: pipelineStatus ? TTS_INFO[pipelineStatus.tts_engine]?.label || pipelineStatus.tts_engine : 'Loading...' },
        { icon: Video, label: 'Video Production', desc: 'FFmpeg auto-rendering + lip-sync', engine: 'FFmpeg + ' + (pipelineStatus?.avatar_engine || 'none') },
        { icon: Share2, label: 'Multi-Platform Upload', desc: 'Auto-distribute to social media', engine: `${selectedPlatforms.length} platform${selectedPlatforms.length !== 1 ? 's' : ''} selected` },
    ];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                        <Sparkles className="w-7 h-7 text-[#C7A84A]" />
                        AI Content Factory
                    </h1>
                    <p className="text-slate-400">Fully automated: Script → Voice → Video → Upload</p>
                </div>
                <Button
                    onClick={loadData}
                    variant="outline"
                    size="sm"
                    className="border-slate-700 text-slate-300"
                >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Refresh
                </Button>
            </div>

            {/* ═══════════════════════════════════════════ */}
            {/* PIPELINE FLOW VISUALIZATION               */}
            {/* ═══════════════════════════════════════════ */}
            <Card className="bg-gradient-to-r from-[#0B1F3A] to-[#162d50] border-slate-700/50 overflow-hidden">
                <CardContent className="pt-6 pb-4">
                    <div className="flex items-center justify-between gap-2">
                        {pipelineSteps.map((step, idx) => {
                            const Icon = step.icon;
                            const isActive = currentStep === idx;
                            const isDone = currentStep > idx;
                            const isPending = currentStep < idx;

                            return (
                                <div key={idx} className="flex items-center flex-1">
                                    {/* Step Card */}
                                    <div className={cn(
                                        "flex-1 p-4 rounded-xl border transition-all duration-500",
                                        isDone ? "bg-emerald-500/10 border-emerald-500/30" :
                                            isActive ? "bg-[#C7A84A]/10 border-[#C7A84A]/40 shadow-lg shadow-[#C7A84A]/5" :
                                                "bg-slate-800/30 border-slate-700/30"
                                    )}>
                                        <div className="flex items-center gap-3 mb-2">
                                            <div className={cn(
                                                "w-10 h-10 rounded-lg flex items-center justify-center transition-all",
                                                isDone ? "bg-emerald-500/20" :
                                                    isActive ? "bg-[#C7A84A]/20 animate-pulse" :
                                                        "bg-slate-800"
                                            )}>
                                                {isDone ? (
                                                    <CheckCircle className="w-5 h-5 text-emerald-400" />
                                                ) : isActive ? (
                                                    <Loader2 className="w-5 h-5 text-[#C7A84A] animate-spin" />
                                                ) : (
                                                    <Icon className={cn("w-5 h-5", isPending ? "text-slate-500" : "text-[#C7A84A]")} />
                                                )}
                                            </div>
                                            <div>
                                                <p className={cn(
                                                    "text-sm font-semibold",
                                                    isDone ? "text-emerald-400" :
                                                        isActive ? "text-[#C7A84A]" :
                                                            "text-slate-400"
                                                )}>{step.label}</p>
                                                <p className="text-[10px] text-slate-500">{step.desc}</p>
                                            </div>
                                        </div>
                                        <Badge variant="outline" className={cn(
                                            "text-[10px]",
                                            isDone ? "border-emerald-500/30 text-emerald-400" :
                                                isActive ? "border-[#C7A84A]/30 text-[#C7A84A]" :
                                                    "border-slate-700 text-slate-500"
                                        )}>
                                            {step.engine}
                                        </Badge>
                                    </div>
                                    {/* Arrow between steps */}
                                    {idx < pipelineSteps.length - 1 && (
                                        <ArrowRight className={cn(
                                            "w-5 h-5 mx-1 flex-shrink-0 transition-colors",
                                            isDone ? "text-emerald-400" : "text-slate-700"
                                        )} />
                                    )}
                                </div>
                            );
                        })}
                    </div>
                    {isRunning && (
                        <div className="mt-4">
                            <Progress value={(currentStep + 1) * 25} className="h-1.5 bg-slate-700" />
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* ═══════════════════════════════════════════ */}
            {/* PIPELINE CONTROLS + DISTRIBUTION           */}
            {/* ═══════════════════════════════════════════ */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left: Pipeline Runner */}
                <div className="lg:col-span-2 space-y-4">
                    <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
                        <CardHeader className="pb-3">
                            <CardTitle className="text-lg text-white flex items-center gap-2">
                                <Zap className="w-5 h-5 text-[#C7A84A]" />
                                Run Content Factory
                            </CardTitle>
                            <p className="text-xs text-slate-500">Select a topic category and hit Run — the entire pipeline executes automatically</p>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                <div>
                                    <Label className="text-slate-300">Content Category *</Label>
                                    {categories.length > 0 ? (
                                        <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                                            <SelectTrigger className="bg-slate-800 border-slate-600 text-white mt-1">
                                                <SelectValue placeholder="Select category..." />
                                            </SelectTrigger>
                                            <SelectContent className="bg-slate-800 border-slate-700">
                                                {categories.map(c => (
                                                    <SelectItem key={c.category} value={c.category}>
                                                        {c.category} ({c.article_count} articles)
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    ) : (
                                        <Input
                                            placeholder="Middle East, Defense, Cyber..."
                                            value={selectedCategory}
                                            onChange={(e) => setSelectedCategory(e.target.value)}
                                            className="bg-slate-800 border-slate-600 text-white mt-1"
                                        />
                                    )}
                                </div>
                                <div>
                                    <Label className="text-slate-300">Region</Label>
                                    <Input
                                        value={selectedRegion}
                                        onChange={(e) => setSelectedRegion(e.target.value)}
                                        className="bg-slate-800 border-slate-600 text-white mt-1"
                                    />
                                </div>
                            </div>

                            {/* Action Buttons */}
                            <div className="grid grid-cols-2 gap-3">
                                <Button
                                    onClick={handleFetchSources}
                                    disabled={isFetchingSources || isRunning}
                                    variant="outline"
                                    className="w-full border-slate-600 text-slate-300 hover:text-white hover:bg-slate-700 font-medium py-6"
                                >
                                    {isFetchingSources ? (
                                        <><Loader2 className="w-5 h-5 mr-2 animate-spin" /> Fetching...</>
                                    ) : (
                                        <><Database className="w-5 h-5 mr-2" /> 1. Fetch Latest News</>
                                    )}
                                </Button>
                                <Button
                                    onClick={handleRunPipeline}
                                    disabled={isRunning || !selectedCategory}
                                    className="w-full bg-gradient-to-r from-[#C7A84A] to-[#d4b65c] hover:from-[#d4b65c] hover:to-[#e0c36d] text-[#0B1F3A] font-bold text-base py-6 shadow-lg shadow-[#C7A84A]/20"
                                >
                                    {isRunning ? (
                                        <><Loader2 className="w-5 h-5 mr-2 animate-spin" /> Factory Running...</>
                                    ) : (
                                        <><Play className="w-5 h-5 mr-2" /> 2. Run Factory</>
                                    )}
                                </Button>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Pipeline Results */}
                    {pipelineResult && (
                        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
                            <CardHeader className="pb-2">
                                <CardTitle className="text-lg text-white">
                                    {pipelineResult.error ? '❌ Pipeline Error' : pipelineResult.success_msg ? 'ℹ️ Information' : '✅ Factory Output'}
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                {pipelineResult.error ? (
                                    <p className="text-red-400 text-sm">{pipelineResult.error}</p>
                                ) : pipelineResult.success_msg ? (
                                    <p className="text-emerald-400 text-sm">{pipelineResult.success_msg}</p>
                                ) : (
                                    <div className="space-y-2">
                                        {pipelineResult.steps && Object.entries(pipelineResult.steps).map(([step, data]: [string, any]) => (
                                            <div key={step} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
                                                <div className="flex items-center gap-3">
                                                    {data.status === 'success' ? (
                                                        <CheckCircle className="w-4 h-4 text-emerald-400" />
                                                    ) : (
                                                        <XCircle className="w-4 h-4 text-red-400" />
                                                    )}
                                                    <span className="text-sm text-white capitalize">{step.replace(/_/g, ' ')}</span>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    {data.url && (
                                                        <a href={data.url} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-400 hover:underline flex items-center gap-1">
                                                            <Download className="w-3 h-3" /> Download
                                                        </a>
                                                    )}
                                                    <Badge className={
                                                        data.status === 'success' ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' :
                                                            data.status === 'skipped' ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' :
                                                                'bg-red-500/20 text-red-400 border-red-500/30'
                                                    }>{data.status}</Badge>
                                                </div>
                                            </div>
                                        ))}
                                        {pipelineResult.summary && (
                                            <div className="mt-3 p-3 bg-emerald-500/5 rounded-lg border border-emerald-500/20">
                                                <p className="text-sm text-slate-300">
                                                    Pipeline: <span className="text-white font-semibold">{pipelineResult.summary.overall_status}</span>
                                                    {' • '}{pipelineResult.summary.successful}/{pipelineResult.summary.total_steps} steps succeeded
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    )}
                </div>

                {/* Right: Distribution + TTS Status */}
                <div className="space-y-4">
                    {/* TTS Engine Card */}
                    <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm text-white flex items-center gap-2">
                                <Volume2 className="w-4 h-4 text-[#C7A84A]" />
                                Voice Engine
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            {pipelineStatus ? (
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-lg font-bold text-white">
                                            {TTS_INFO[pipelineStatus.tts_engine]?.label || pipelineStatus.tts_engine}
                                        </p>
                                        <p className="text-xs text-slate-500">Change in Settings → TTS & Video</p>
                                    </div>
                                    <Badge variant="outline" className={TTS_INFO[pipelineStatus.tts_engine]?.badgeClass || 'text-slate-400 border-slate-700'}>
                                        {TTS_INFO[pipelineStatus.tts_engine]?.badge || 'Unknown'}
                                    </Badge>
                                </div>
                            ) : (
                                <p className="text-sm text-slate-500">Loading...</p>
                            )}
                        </CardContent>
                    </Card>

                    {/* Distribution Platforms */}
                    <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm text-white flex items-center gap-2">
                                <Share2 className="w-4 h-4 text-[#C7A84A]" />
                                Upload To
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-2">
                                {platforms.map((platform) => {
                                    const Icon = PLATFORM_ICONS[platform.id] || Share2;
                                    const color = PLATFORM_COLORS[platform.id] || 'text-slate-400';
                                    const isSelected = selectedPlatforms.includes(platform.id);

                                    return (
                                        <button
                                            key={platform.id}
                                            onClick={() => platform.connected && togglePlatform(platform.id)}
                                            disabled={!platform.connected}
                                            className={cn(
                                                "w-full flex items-center justify-between px-3 py-2.5 rounded-lg border transition-all text-left",
                                                isSelected && platform.connected
                                                    ? "bg-[#C7A84A]/10 border-[#C7A84A]/30"
                                                    : platform.connected
                                                        ? "bg-slate-800/30 border-slate-700/50 hover:border-slate-500"
                                                        : "bg-slate-900/30 border-slate-800 opacity-50 cursor-not-allowed"
                                            )}
                                        >
                                            <div className="flex items-center gap-2.5">
                                                <div className={cn(
                                                    "w-8 h-8 rounded-lg flex items-center justify-center",
                                                    isSelected ? "bg-[#C7A84A]/20" : "bg-slate-800"
                                                )}>
                                                    <Icon className={cn("w-4 h-4", isSelected ? "text-[#C7A84A]" : color)} />
                                                </div>
                                                <div>
                                                    <p className={cn(
                                                        "text-sm font-medium",
                                                        isSelected ? "text-white" : "text-slate-400"
                                                    )}>{platform.name}</p>
                                                    {platform.channel_name && (
                                                        <p className="text-[10px] text-slate-500">{platform.channel_name}</p>
                                                    )}
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                {platform.connected ? (
                                                    <div className={cn(
                                                        "w-4 h-4 rounded border-2 flex items-center justify-center transition-all",
                                                        isSelected ? "bg-[#C7A84A] border-[#C7A84A]" : "border-slate-600"
                                                    )}>
                                                        {isSelected && <CheckCircle className="w-3 h-3 text-[#0B1F3A]" />}
                                                    </div>
                                                ) : (
                                                    <Badge variant="outline" className="text-[9px] border-slate-700 text-slate-600">
                                                        Not linked
                                                    </Badge>
                                                )}
                                            </div>
                                        </button>
                                    );
                                })}
                                {platforms.length === 0 && (
                                    <p className="text-xs text-slate-500 text-center py-4">
                                        {loadingPlatforms ? 'Loading platforms...' : 'Configure platforms in Settings → Distribution'}
                                    </p>
                                )}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Pipeline Capabilities */}
                    <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm text-white flex items-center gap-2">
                                <Zap className="w-4 h-4 text-[#C7A84A]" />
                                System Status
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-2">
                                {[
                                    { name: 'AI Script Engine', ready: pipelineStatus?.ai_configured, detail: 'Gemini / Ollama' },
                                    { name: 'TTS Audio', ready: pipelineStatus?.tts_configured, detail: pipelineStatus?.tts_engine || '-' },
                                    { name: 'Video Rendering', ready: true, detail: 'FFmpeg' },
                                    { name: 'Avatar Lip-Sync', ready: pipelineStatus?.avatar_configured, detail: pipelineStatus?.avatar_engine || 'none' },
                                ].map(({ name, ready, detail }) => (
                                    <div key={name} className="flex items-center justify-between py-1.5">
                                        <div className="flex items-center gap-2">
                                            {ready ? (
                                                <div className="w-2 h-2 rounded-full bg-emerald-400" />
                                            ) : (
                                                <div className="w-2 h-2 rounded-full bg-red-400" />
                                            )}
                                            <span className="text-xs text-slate-300">{name}</span>
                                        </div>
                                        <span className="text-[10px] text-slate-500">{detail}</span>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
