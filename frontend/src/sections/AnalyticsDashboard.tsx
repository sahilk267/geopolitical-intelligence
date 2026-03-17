import React, { useEffect, useState } from 'react';
import { 
  Activity, 
  Database, 
  Server, 
  Cpu, 
  Network,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Clock,
  Trash2,
  Cloud,
  FileVideo,
  MonitorPlay,
  HelpCircle
} from 'lucide-react';
import { api } from '../lib/api';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function AnalyticsDashboard() {
  const [performance, setPerformance] = useState<any>(null);
  const [ragStats, setRagStats] = useState<any[]>([]);
  const [distribution, setDistribution] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchStats = async () => {
    try {
      setLoading(true);
      const results = await Promise.allSettled([
        api.getPerformanceStats(),
        api.getRagStats(),
        api.getDistributionStats()
      ]);

      if (results[0].status === 'fulfilled') {
        setPerformance(results[0].value);
      } else {
        console.error('Performance stats failed:', results[0].reason);
      }

      if (results[1].status === 'fulfilled') {
        const value = results[1].value;
        setRagStats(Array.isArray(value) ? (value as any[]) : []);
      } else {
        console.error('RAG stats failed:', results[1].reason);
        setRagStats([]);
      }

      if (results[2].status === 'fulfilled') {
        setDistribution(results[2].value);
      } else {
        console.error('Distribution stats failed:', results[2].reason);
      }

      // Only show error bar if ALL failed
      if (results.every(r => r.status === 'rejected')) {
        const firstError = (results[0] as PromiseRejectedResult).reason;
        setError(`Failed to load ALL analytics data: ${firstError.message || 'Server connection error'}`);
      } else {
        setError('');
      }
    } catch (err: any) {
      console.error('Failed to load analytics:', err);
      setError(`Unexpected error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !performance) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
      case 'available':
      case 'configured':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'offline':
      case 'missing':
      case 'missing_key':
      case 'path_mismatch':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
      case 'available':
      case 'configured':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 border-green-200 dark:border-green-800';
      case 'offline':
      case 'missing':
      case 'missing_key':
      case 'path_mismatch':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400 border-red-200 dark:border-red-800';
      default:
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400 border-yellow-200 dark:border-yellow-800';
    }
  };

  // Helper to safely access nested performance data
  const localStats = performance?.local || performance;
  const cloudStats = performance?.cloud || {};

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-500">
            Advanced Analytics & Monitoring
          </h2>
          <p className="text-muted-foreground mt-1">
            Real-time health telemetry for AI services and pipeline efficiency.
          </p>
        </div>
        <button
          onClick={fetchStats}
          disabled={loading}
          className="px-4 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 flex items-center space-x-2 transition-all active:scale-95"
        >
          <Activity className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {error && (
        <div className="bg-destructive/10 text-destructive p-4 rounded-lg flex items-center border border-destructive/20 animate-in fade-in slide-in-from-top-4">
          <AlertCircle className="w-5 h-5 mr-2" />
          {error}
        </div>
      )}

      <Tabs defaultValue="local" className="space-y-6">
        <TabsList className="bg-muted/50 p-1">
          <TabsTrigger value="local" className="flex items-center gap-2">
            <Cpu className="w-4 h-4" />
            Local AI Engines
          </TabsTrigger>
          <TabsTrigger value="cloud" className="flex items-center gap-2">
            <Cloud className="w-4 h-4" />
            Cloud & External APIs
          </TabsTrigger>
          <TabsTrigger value="memory" className="flex items-center gap-2">
            <Database className="w-4 h-4" />
            RAG Memory
          </TabsTrigger>
        </TabsList>

        <TabsContent value="local" className="space-y-6 animate-in fade-in duration-300">
           <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Ollama */}
              <Card>
                <CardHeader className="pb-2">
                  <div className="flex justify-between items-start">
                    <Server className="w-5 h-5 text-blue-500" />
                    {getStatusIcon(localStats?.ollama?.status)}
                  </div>
                  <CardTitle className="text-base mt-2">Ollama (LLM)</CardTitle>
                  <CardDescription className="truncate font-mono text-[10px]">
                    {localStats?.ollama?.model || 'llama2'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold font-mono">
                    {localStats?.ollama?.latency_ms || 0}ms
                  </div>
                  <Badge variant="outline" className={`mt-2 text-[10px] ${getStatusColor(localStats?.ollama?.status)}`}>
                    {localStats?.ollama?.status?.toUpperCase() || 'OFFLINE'}
                  </Badge>
                </CardContent>
              </Card>

              {/* SD.Next */}
              <Card>
                <CardHeader className="pb-2">
                  <div className="flex justify-between items-start">
                    <Activity className="w-5 h-5 text-purple-500" />
                    {getStatusIcon(localStats?.sd_next?.status)}
                  </div>
                  <CardTitle className="text-base mt-2">SD.Next (Image)</CardTitle>
                  <CardDescription className="text-xs">
                    Local Diffusion API
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold font-mono">
                    {localStats?.sd_next?.latency_ms || 0}ms
                  </div>
                  <Badge variant="outline" className={`mt-2 text-[10px] ${getStatusColor(localStats?.sd_next?.status)}`}>
                    {localStats?.sd_next?.status?.toUpperCase() || 'OFFLINE'}
                  </Badge>
                </CardContent>
              </Card>

              {/* SadTalker */}
              <Card>
                <CardHeader className="pb-2">
                  <div className="flex justify-between items-start">
                    <MonitorPlay className="w-5 h-5 text-pink-500" />
                    {getStatusIcon(localStats?.sadtalker?.status)}
                  </div>
                  <CardTitle className="text-base mt-2">SadTalker (Video)</CardTitle>
                  <CardDescription className="text-xs truncate" title={localStats?.sadtalker?.path}>
                    {localStats?.sadtalker?.path ? 'Installed' : 'Not Configured'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-xs font-medium truncate text-muted-foreground mb-1">
                    {localStats?.sadtalker?.status === 'path_mismatch' ? 'PATH ERROR' : 'STATUS'}
                  </div>
                  <Badge variant="outline" className={`text-[10px] ${getStatusColor(localStats?.sadtalker?.status)}`}>
                    {localStats?.sadtalker?.status?.replace('_', ' ').toUpperCase() || 'MISSING'}
                  </Badge>
                  {localStats?.sadtalker?.warning && (
                     <p className="mt-2 text-[9px] text-red-500 leading-tight">
                       {localStats.sadtalker.warning}
                     </p>
                  )}
                </CardContent>
              </Card>

              {/* FFmpeg */}
              <Card>
                <CardHeader className="pb-2">
                  <div className="flex justify-between items-start">
                    <FileVideo className="w-5 h-5 text-amber-500" />
                    {getStatusIcon(localStats?.ffmpeg?.status)}
                  </div>
                  <CardTitle className="text-base mt-2">FFmpeg (Render)</CardTitle>
                  <CardDescription className="text-xs truncate">
                    {localStats?.ffmpeg?.version !== 'unknown' ? localStats?.ffmpeg?.version : 'System Tool'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                   <div className="text-xs font-medium text-muted-foreground mb-1">VERSION</div>
                   <div className="text-xs font-mono truncate mb-2">{localStats?.ffmpeg?.version || 'N/A'}</div>
                   <Badge variant="outline" className={`text-[10px] ${getStatusColor(localStats?.ffmpeg?.status)}`}>
                    {localStats?.ffmpeg?.status?.toUpperCase() || 'MISSING'}
                  </Badge>
                </CardContent>
              </Card>
           </div>

           {/* Docker Troubleshooting Tips */}
           <Card className="border-blue-200 bg-blue-50/30 dark:bg-blue-900/10 dark:border-blue-900/30 mt-6 animate-in slide-in-from-bottom-2">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <HelpCircle className="w-4 h-4 text-blue-500" />
                  Docker Connectivity Troubleshooting
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="text-xs space-y-2 text-muted-foreground">
                  <li className="flex gap-2">
                    <span className="font-bold text-blue-500 text-[10px] mt-0.5 whitespace-nowrap">OLLAMA / SD:</span>
                    If status is <b>OFFLINE</b>, ensure your local tools are configured to listen on <b>0.0.0.0</b> (not just 127.0.0.1) so <b>host.docker.internal</b> can reach them.
                  </li>
                  <li className="flex gap-2">
                    <span className="font-bold text-blue-500 text-[10px] mt-0.5 whitespace-nowrap">SADTALKER:</span>
                    If <b>MISSING</b>, you must mount your local SadTalker folder as a volume in <b>docker-compose.yml</b>. See the commented line in that file.
                  </li>
                </ul>
              </CardContent>
            </Card>
        </TabsContent>

        <TabsContent value="cloud" className="space-y-6 animate-in fade-in duration-300">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Cloud className="w-5 h-5 text-primary" />
                  AI Intelligence & Voice
                </CardTitle>
                <CardDescription>Status of paid cloud provider configurations.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                 {[
                   { name: 'Gemini (LLM)', icon: Cloud, key: 'gemini', color: 'text-blue-500' },
                   { name: 'ElevenLabs (TTS)', icon: Activity, key: 'elevenlabs', color: 'text-green-500' },
                   { name: 'D-ID (Avatar)', icon: MonitorPlay, key: 'did', color: 'text-indigo-500' },
                   { name: 'HeyGen (Avatar)', icon: Activity, key: 'heygen', color: 'text-purple-500' },
                 ].map(service => (
                   <div key={service.key} className="flex items-center justify-between p-3 border rounded-lg bg-card hover:bg-muted/30 transition-colors">
                      <div className="flex items-center gap-3">
                        <service.icon className={`w-5 h-5 ${service.color}`} />
                        <span className="font-medium text-sm">{service.name}</span>
                      </div>
                      <Badge variant="outline" className={`text-[10px] ${getStatusColor(cloudStats[service.key]?.status)}`}>
                         {(cloudStats[service.key]?.status || 'NOT SETUP').replace('_', ' ').toUpperCase()}
                      </Badge>
                   </div>
                 ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Network className="w-5 h-5 text-primary" />
                  Distribution Services
                </CardTitle>
                <CardDescription>Social media platform connectivity status.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                 {[
                   { name: 'Telegram Bot', key: 'telegram', icon: 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .38z' },
                   { name: 'YouTube API', key: 'youtube', icon: 'M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z' },
                   { name: 'X / Twitter', key: 'twitter', icon: 'M13.202 10.566 19.3.5h-1.446l-5.304 6.166L8.3 .5H3.42l6.393 9.305-6.393 7.39h1.445l5.59-6.499 4.803 6.499h4.881l-6.945-10.13Z' },
                   { name: 'Discord Webhook', key: 'discord', icon: 'M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.' },
                 ].map(platform => (
                   <div key={platform.key} className="flex items-center justify-between p-3 border rounded-lg bg-card hover:bg-muted/30 transition-colors">
                      <div className="flex items-center gap-3">
                        <svg className="w-5 h-5 opacity-70" fill="currentColor" viewBox="0 0 24 24">
                          <path d={platform.icon} />
                        </svg>
                        <span className="font-medium text-sm">{platform.name}</span>
                      </div>
                      <Badge variant="outline" className={`text-[10px] ${distribution?.[platform.key] ? getStatusColor('online') : getStatusColor('offline')}`}>
                         {distribution?.[platform.key] ? 'CONNECTED' : 'DISABLED'}
                      </Badge>
                   </div>
                 ))}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="memory" className="animate-in fade-in duration-300">
           <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                   <div>
                    <CardTitle>RAG Memory Statistics</CardTitle>
                    <CardDescription>Document vector distribution across personas.</CardDescription>
                   </div>
                   <Badge variant="outline" className="bg-primary/5 text-primary border-primary/20">ChromaDB</Badge>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                <div className="overflow-auto max-h-[600px]">
                  {ragStats.length === 0 ? (
                    <div className="p-12 text-center text-muted-foreground">
                      <Database className="w-12 h-12 mx-auto mb-3 opacity-20" />
                      <p>No personas found or RAG disabled.</p>
                    </div>
                  ) : (
                    <table className="w-full text-sm">
                      <thead className="bg-muted/50 text-muted-foreground text-left sticky top-0">
                        <tr>
                          <th className="px-5 py-4 font-medium">Persona</th>
                          <th className="px-5 py-4 font-medium">Collection Name</th>
                          <th className="px-5 py-4 font-medium text-right">Knowledge Chunks</th>
                          <th className="px-5 py-4 font-medium text-right">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y">
                        {ragStats.map((stat: any, i: number) => (
                          <tr key={i} className="hover:bg-muted/50 transition-colors group">
                            <td className="px-5 py-4">
                              <div className="font-semibold text-foreground">{stat.profile_name}</div>
                              <div className="text-[10px] uppercase tracking-wider text-muted-foreground mt-0.5">{stat.persona_type || 'Custom Persona'}</div>
                            </td>
                            <td className="px-5 py-4 text-xs font-mono text-muted-foreground opacity-70">
                              {stat.collection_name || 'persona_memory_v1'}
                            </td>
                            <td className="px-5 py-4 text-right">
                               <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold ${stat.error ? 'bg-red-500/10 text-red-600' : 'bg-blue-500/10 text-blue-600 dark:text-blue-400'}`}>
                                 {stat.error ? 'ERROR' : (stat.total_memories !== undefined ? stat.total_memories.toLocaleString() : '??')}
                               </span>
                               {stat.error && <div className="text-[10px] text-red-500 mt-1 max-w-[200px] truncate" title={stat.error}>{stat.error}</div>}
                            </td>
                            <td className="px-5 py-4 text-right">
                              <button className="p-2 text-muted-foreground hover:text-destructive transition-colors opacity-0 group-hover:opacity-100">
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              </CardContent>
           </Card>
        </TabsContent>
      </Tabs>

      <div className="text-center p-4">
        <p className="text-[10px] text-muted-foreground uppercase tracking-[0.2em] opacity-50">
          Telemetry Feed v2.0 • Last Sync: {new Date().toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}
