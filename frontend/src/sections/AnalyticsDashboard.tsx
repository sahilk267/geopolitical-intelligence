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
  Trash2
} from 'lucide-react';
import { api } from '../lib/api';

export default function AnalyticsDashboard() {
  const [performance, setPerformance] = useState<any>(null);
  const [ragStats, setRagStats] = useState<any[]>([]);
  const [distribution, setDistribution] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchStats = async () => {
    try {
      setLoading(true);
      const [perfRes, ragRes, distRes] = await Promise.all([
        api.getPerformanceStats(),
        api.getRagStats(),
        api.getDistributionStats()
      ]);
      setPerformance(perfRes);
      setRagStats(ragRes as unknown as any[]);
      setDistribution(distRes);
      setError('');
    } catch (err: any) {
      console.error('Failed to load analytics:', err);
      setError('Failed to load analytics data.');
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
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'offline':
      case 'missing':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
      case 'available':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 border-green-200 dark:border-green-800';
      case 'offline':
      case 'missing':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400 border-red-200 dark:border-red-800';
      default:
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400 border-yellow-200 dark:border-yellow-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-500">
            Advanced Analytics & Monitoring
          </h2>
          <p className="text-muted-foreground mt-1">
            Real-time health telemetry for local AI services and RAG memory efficiency.
          </p>
        </div>
        <button
          onClick={fetchStats}
          disabled={loading}
          className="px-4 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 flex items-center space-x-2"
        >
          <Activity className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {error && (
        <div className="bg-destructive/10 text-destructive p-4 rounded-lg flex items-center">
          <AlertCircle className="w-5 h-5 mr-2" />
          {error}
        </div>
      )}

      {/* Local AI Services Grid */}
      <h3 className="text-lg font-semibold flex items-center">
        <Cpu className="w-5 h-5 mr-2" />
        Local AI Engine Status
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Ollama */}
        <div className="bg-card border rounded-lg p-5 shadow-sm relative overflow-hidden">
          <div className="flex justify-between items-start mb-4">
            <div className="flex items-center">
              <Server className="w-6 h-6 text-blue-500 mr-3" />
              <div>
                <h4 className="font-semibold text-lg">Ollama (LLM)</h4>
                <p className="text-sm text-muted-foreground font-mono truncate max-w-[150px]">
                  {performance?.ollama?.model || 'Unknown Model'}
                </p>
              </div>
            </div>
            {getStatusIcon(performance?.ollama?.status)}
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Status</span>
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(performance?.ollama?.status)}`}>
                {performance?.ollama?.status?.toUpperCase() || 'UNKNOWN'}
              </span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Ping Latency</span>
              <span className="font-mono">{performance?.ollama?.latency_ms || 0} ms</span>
            </div>
          </div>
          {performance?.ollama?.status === 'offline' && (
            <div className="mt-4 p-2 bg-red-500/10 text-red-500 text-xs rounded border border-red-500/20">
              Ensure Ollama is running locally and CORS is configured.
            </div>
          )}
        </div>

        {/* SD.Next */}
        <div className="bg-card border rounded-lg p-5 shadow-sm relative overflow-hidden">
          <div className="flex justify-between items-start mb-4">
            <div className="flex items-center">
              <Activity className="w-6 h-6 text-purple-500 mr-3" />
              <div>
                <h4 className="font-semibold text-lg">SD.Next (Images)</h4>
                <p className="text-sm text-muted-foreground">Local API</p>
              </div>
            </div>
            {getStatusIcon(performance?.sd_next?.status)}
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Status</span>
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(performance?.sd_next?.status)}`}>
                {performance?.sd_next?.status?.toUpperCase() || 'UNKNOWN'}
              </span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Ping Latency</span>
              <span className="font-mono">{performance?.sd_next?.latency_ms || 0} ms</span>
            </div>
          </div>
          {performance?.sd_next?.status === 'offline' && (
            <div className="mt-4 p-2 bg-red-500/10 text-red-500 text-xs rounded border border-red-500/20">
              Ensure SD.Next is running with --api flag enabled.
            </div>
          )}
        </div>

        {/* SadTalker */}
        <div className="bg-card border rounded-lg p-5 shadow-sm relative overflow-hidden">
          <div className="flex justify-between items-start mb-4">
            <div className="flex items-center">
              <Activity className="w-6 h-6 text-pink-500 mr-3" />
              <div>
                <h4 className="font-semibold text-lg">SadTalker (Video)</h4>
                <p className="text-sm text-muted-foreground">Local CLI</p>
              </div>
            </div>
            {getStatusIcon(performance?.sadtalker?.status)}
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Status</span>
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(performance?.sadtalker?.status)}`}>
                {performance?.sadtalker?.status?.toUpperCase() || 'UNKNOWN'}
              </span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Local Path</span>
            </div>
            <div className="text-xs bg-muted p-2 rounded truncate font-mono" title={performance?.sadtalker?.path}>
              {performance?.sadtalker?.path || '-'}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* RAG Memory Insights */}
        <div className="bg-card border rounded-lg shadow-sm flex flex-col">
          <div className="p-5 border-b flex justify-between items-center">
            <h3 className="text-lg font-semibold flex items-center">
              <Database className="w-5 h-5 mr-2 text-primary" />
              Persona RAG Memory
            </h3>
            <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full font-medium">
              ChromaDB
            </span>
          </div>
          <div className="p-0 overflow-auto max-h-[400px]">
            {ragStats.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground">
                <Database className="w-12 h-12 mx-auto mb-3 opacity-20" />
                <p>No personas found or RAG disabled.</p>
              </div>
            ) : (
              <table className="w-full text-sm">
                <thead className="bg-muted/50 text-muted-foreground text-left sticky top-0">
                  <tr>
                    <th className="px-5 py-3 font-medium">Persona</th>
                    <th className="px-5 py-3 font-medium">Collection</th>
                    <th className="px-5 py-3 font-medium text-right">Stored Chunks</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {ragStats.map((stat, i) => (
                    <tr key={i} className="hover:bg-muted/50 transition-colors">
                      <td className="px-5 py-3">
                        <div className="font-medium text-foreground">{stat.profile_name}</div>
                        <div className="text-xs text-muted-foreground capitalize">{stat.persona_type}</div>
                      </td>
                      <td className="px-5 py-3 text-xs font-mono text-muted-foreground">
                        {stat.collection_name || '-'}
                      </td>
                      <td className="px-5 py-3 text-right">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300">
                          {stat.total_memories !== undefined ? stat.total_memories : 'Error'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Global Pipeline Health */}
        <div className="bg-card border rounded-lg shadow-sm p-5">
          <h3 className="text-lg font-semibold flex items-center mb-6">
            <Network className="w-5 h-5 mr-2 text-primary" />
            Distribution Gateways
          </h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 border rounded-lg bg-card hover:bg-muted/30 transition-colors">
              <div className="flex items-center">
                <div className="w-10 h-10 rounded-full bg-[#1DA1F2]/10 flex items-center justify-center mr-4">
                  <span className="text-[#1DA1F2] font-bold text-xl">X</span>
                </div>
                <div>
                  <h4 className="font-medium">X (Twitter)</h4>
                  <p className="text-xs text-muted-foreground">OAuth 1.0a (v1.1 + v2)</p>
                </div>
              </div>
              <div>
                {distribution?.twitter ? (
                  <span className="px-3 py-1 bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 rounded-full text-xs font-medium flex items-center">
                    <CheckCircle2 className="w-3 h-3 mr-1" /> Configured
                  </span>
                ) : (
                  <span className="px-3 py-1 bg-muted text-muted-foreground rounded-full text-xs font-medium flex items-center">
                    <XCircle className="w-3 h-3 mr-1" /> Disabled
                  </span>
                )}
              </div>
            </div>

            <div className="flex items-center justify-between p-3 border rounded-lg bg-card hover:bg-muted/30 transition-colors">
              <div className="flex items-center">
                <div className="w-10 h-10 rounded-full bg-[#5865F2]/10 flex items-center justify-center mr-4">
                  <svg className="w-6 h-6 text-[#5865F2]" fill="currentColor" viewBox="0 0 24 24"><path d="M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.037 19.7363 19.7363 0 00-4.8852 1.515.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276 12.2986 12.2986 0 01-1.873.8914.0766.0766 0 00-.0407.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061 0 00-.0312-.0286zM8.02 15.3312c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9555-2.4189 2.157-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.9555 2.4189-2.1569 2.4189zm7.9748 0c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9554-2.4189 2.1569-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.946 2.4189-2.1568 2.4189Z"/></svg>
                </div>
                <div>
                  <h4 className="font-medium">Discord</h4>
                  <p className="text-xs text-muted-foreground">Webhook Integrations</p>
                </div>
              </div>
              <div>
                {distribution?.discord ? (
                  <span className="px-3 py-1 bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 rounded-full text-xs font-medium flex items-center">
                    <CheckCircle2 className="w-3 h-3 mr-1" /> Configured
                  </span>
                ) : (
                  <span className="px-3 py-1 bg-muted text-muted-foreground rounded-full text-xs font-medium flex items-center">
                    <XCircle className="w-3 h-3 mr-1" /> Disabled
                  </span>
                )}
              </div>
            </div>

            <div className="flex items-center justify-between p-3 border rounded-lg bg-card hover:bg-muted/30 transition-colors">
              <div className="flex items-center">
                <div className="w-10 h-10 rounded-full bg-[#0088cc]/10 flex items-center justify-center mr-4">
                  <svg className="w-5 h-5 text-[#0088cc]" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .38z"/></svg>
                </div>
                <div>
                  <h4 className="font-medium">Telegram</h4>
                  <p className="text-xs text-muted-foreground">Bot API</p>
                </div>
              </div>
              <div>
                {distribution?.telegram ? (
                  <span className="px-3 py-1 bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 rounded-full text-xs font-medium flex items-center">
                    <CheckCircle2 className="w-3 h-3 mr-1" /> Configured
                  </span>
                ) : (
                  <span className="px-3 py-1 bg-muted text-muted-foreground rounded-full text-xs font-medium flex items-center">
                    <XCircle className="w-3 h-3 mr-1" /> Disabled
                  </span>
                )}
              </div>
            </div>

            <div className="flex items-center justify-between p-3 border rounded-lg bg-card hover:bg-muted/30 transition-colors">
              <div className="flex items-center">
                <div className="w-10 h-10 rounded-full bg-[#FF0000]/10 flex items-center justify-center mr-4">
                  <svg className="w-5 h-5 text-[#FF0000]" fill="currentColor" viewBox="0 0 24 24"><path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z"/></svg>
                </div>
                <div>
                  <h4 className="font-medium">YouTube</h4>
                  <p className="text-xs text-muted-foreground">Data API v3</p>
                </div>
              </div>
              <div>
                {distribution?.youtube ? (
                  <span className="px-3 py-1 bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 rounded-full text-xs font-medium flex items-center">
                    <CheckCircle2 className="w-3 h-3 mr-1" /> Configured
                  </span>
                ) : (
                  <span className="px-3 py-1 bg-muted text-muted-foreground rounded-full text-xs font-medium flex items-center">
                    <XCircle className="w-3 h-3 mr-1" /> Disabled
                  </span>
                )}
              </div>
            </div>
            
          </div>
        </div>
      </div>
    </div>
  );
}
