// ============================================
// SYSTEM MONITOR SECTION
// Data Sources, RSS Feeds, Error Logs & Health Monitoring
// ============================================

import { useState } from 'react';
import { useAppStore } from '@/store';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import {
  Activity,
  AlertCircle,
  CheckCircle,
  XCircle,
  RefreshCw,
  Plus,
  Trash2,
  Globe,
  Rss,
  Zap,
  Server,
  Database,
  Wifi,
  WifiOff,
  AlertTriangle,
  Check,
  X,
  ExternalLink,
  FileText,
  Filter,
  Search,
  Trash,
} from 'lucide-react';
import type { DataSource, LogLevel, DataSourceType, DataSourceStatus } from '@/types';

const statusColors: Record<DataSourceStatus, string> = {
  active: 'bg-green-500/20 text-green-400 border-green-500/30',
  inactive: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
  error: 'bg-red-500/20 text-red-400 border-red-500/30',
  paused: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  testing: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
};

const logLevelColors: Record<LogLevel, string> = {
  info: 'bg-blue-500/20 text-blue-400',
  warning: 'bg-amber-500/20 text-amber-400',
  error: 'bg-red-500/20 text-red-400',
  critical: 'bg-purple-500/20 text-purple-400',
  success: 'bg-green-500/20 text-green-400',
};

const typeIcons: Record<DataSourceType, React.ElementType> = {
  rss: Rss,
  api: Zap,
  webhook: Server,
  manual: FileText,
  scraping: Globe,
};

export function SystemMonitor() {
  const {
    dataSources,
    systemLogs,
    systemHealth,
    fetchedArticles,
    fetchTestResults,
    isFetching,
    addDataSource,
    deleteDataSource,
    toggleDataSource,
    testDataSource,
    fetchFromSource,
    fetchAllSources,
    addLog,
    clearLogs,
    resolveLog,
    getActiveSources,
    getErrorSources,
  } = useAppStore();

  const [activeTab, setActiveTab] = useState('sources');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [testingSourceId, setTestingSourceId] = useState<string | null>(null);
  const [logFilter, setLogFilter] = useState<LogLevel | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const activeSources = getActiveSources();
  const errorSources = getErrorSources();

  const filteredLogs = systemLogs.filter((log) => {
    const matchesLevel = logFilter === 'all' || log.level === logFilter;
    const matchesSearch =
      log.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.category.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesLevel && matchesSearch;
  });

  const handleTestSource = async (sourceId: string) => {
    setTestingSourceId(sourceId);
    try {
      await testDataSource(sourceId);
    } finally {
      setTestingSourceId(null);
    }
  };

  const handleAddSource = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);

    const newSource: DataSource = {
      id: `source-${Date.now()}`,
      name: formData.get('name') as string,
      url: formData.get('url') as string,
      type: formData.get('type') as DataSourceType,
      status: 'active',
      category: formData.get('category') as string,
      region: formData.get('region') as string,
      lastFetchAt: null,
      lastFetchStatus: null,
      lastFetchError: null,
      fetchCount: 0,
      successCount: 0,
      errorCount: 0,
      averageResponseTime: 0,
      itemsFetched: 0,
      isEnabled: true,
      fetchInterval: parseInt(formData.get('fetchInterval') as string),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    addDataSource(newSource);
    setIsAddDialogOpen(false);

    addLog({
      id: `log-${Date.now()}`,
      timestamp: new Date().toISOString(),
      level: 'info',
      category: 'Data Source',
      message: `New data source added: ${newSource.name}`,
      resolved: true,
    });
  };

  const handleClearResolvedLogs = () => {
    const unresolvedLogs = systemLogs.filter((log) => !log.resolved);
    clearLogs();
    unresolvedLogs.forEach((log) => addLog(log));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">System Monitor</h1>
          <p className="text-slate-400">Monitor data sources, RSS feeds, and system health</p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            onClick={fetchAllSources}
            disabled={isFetching}
            className="bg-[#C7A84A] hover:bg-[#d4b65c] text-[#0B1F3A]"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isFetching ? 'animate-spin' : ''}`} />
            {isFetching ? 'Fetching...' : 'Fetch All Sources'}
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-400">Total Sources</p>
                <p className="text-2xl font-bold text-white">{dataSources.length}</p>
              </div>
              <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                <Database className="w-5 h-5 text-blue-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-400">Active Sources</p>
                <p className="text-2xl font-bold text-green-400">{activeSources.length}</p>
              </div>
              <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-green-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-400">Error Sources</p>
                <p className="text-2xl font-bold text-red-400">{errorSources.length}</p>
              </div>
              <div className="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center">
                <XCircle className="w-5 h-5 text-red-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-400">System Status</p>
                <p className={`text-lg font-bold ${systemHealth.overall === 'healthy' ? 'text-green-400' : systemHealth.overall === 'degraded' ? 'text-amber-400' : 'text-red-400'}`}>
                  {systemHealth.overall.toUpperCase()}
                </p>
              </div>
              <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                <Activity className="w-5 h-5 text-purple-400" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-slate-800 border border-slate-700">
          <TabsTrigger value="sources" className="data-[state=active]:bg-[#C7A84A] data-[state=active]:text-[#0B1F3A]">
            <Database className="w-4 h-4 mr-2" />
            Data Sources
          </TabsTrigger>
          <TabsTrigger value="logs" className="data-[state=active]:bg-[#C7A84A] data-[state=active]:text-[#0B1F3A]">
            <AlertCircle className="w-4 h-4 mr-2" />
            Error Logs
            {systemLogs.filter((l) => !l.resolved && (l.level === 'error' || l.level === 'critical')).length > 0 && (
              <span className="ml-2 px-1.5 py-0.5 text-[10px] bg-red-500 text-white rounded-full">
                {systemLogs.filter((l) => !l.resolved && (l.level === 'error' || l.level === 'critical')).length}
              </span>
            )}
          </TabsTrigger>
          <TabsTrigger value="health" className="data-[state=active]:bg-[#C7A84A] data-[state=active]:text-[#0B1F3A]">
            <Activity className="w-4 h-4 mr-2" />
            System Health
          </TabsTrigger>
          <TabsTrigger value="articles" className="data-[state=active]:bg-[#C7A84A] data-[state=active]:text-[#0B1F3A]">
            <FileText className="w-4 h-4 mr-2" />
            Fetched Articles
          </TabsTrigger>
        </TabsList>

        {/* Data Sources Tab */}
        <TabsContent value="sources" className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <Input
                  type="text"
                  placeholder="Search sources..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 bg-slate-800 border-slate-700 text-white w-64"
                />
              </div>
            </div>
            <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-[#C7A84A] hover:bg-[#d4b65c] text-[#0B1F3A]">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Source
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-[#0B1F3A] border-slate-700 max-w-2xl">
                <DialogHeader>
                  <DialogTitle className="text-white">Add New Data Source</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleAddSource} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-slate-300">Source Name</Label>
                      <Input name="name" required className="bg-slate-800 border-slate-600 text-white" />
                    </div>
                    <div>
                      <Label className="text-slate-300">Source Type</Label>
                      <Select name="type" defaultValue="rss">
                        <SelectTrigger className="bg-slate-800 border-slate-600 text-white">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-slate-800 border-slate-700">
                          <SelectItem value="rss">RSS Feed</SelectItem>
                          <SelectItem value="api">API</SelectItem>
                          <SelectItem value="webhook">Webhook</SelectItem>
                          <SelectItem value="scraping">Web Scraping</SelectItem>
                          <SelectItem value="manual">Manual</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div>
                    <Label className="text-slate-300">URL / Endpoint</Label>
                    <Input name="url" required className="bg-slate-800 border-slate-600 text-white" placeholder="https://..." />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-slate-300">Category</Label>
                      <Input name="category" required className="bg-slate-800 border-slate-600 text-white" />
                    </div>
                    <div>
                      <Label className="text-slate-300">Region</Label>
                      <Select name="region" defaultValue="Global">
                        <SelectTrigger className="bg-slate-800 border-slate-600 text-white">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-slate-800 border-slate-700">
                          <SelectItem value="Global">Global</SelectItem>
                          <SelectItem value="Middle East">Middle East</SelectItem>
                          <SelectItem value="South Asia">South Asia</SelectItem>
                          <SelectItem value="Europe">Europe</SelectItem>
                          <SelectItem value="Asia-Pacific">Asia-Pacific</SelectItem>
                          <SelectItem value="Americas">Americas</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div>
                    <Label className="text-slate-300">Fetch Interval (minutes)</Label>
                    <Input name="fetchInterval" type="number" defaultValue="30" min="5" className="bg-slate-800 border-slate-600 text-white" />
                  </div>
                  <Button type="submit" className="w-full bg-[#C7A84A] hover:bg-[#d4b65c] text-[#0B1F3A]">
                    Add Data Source
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          {/* Sources Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {dataSources
              .filter((s) => s.name.toLowerCase().includes(searchQuery.toLowerCase()))
              .map((source) => {
                const Icon = typeIcons[source.type];
                const lastTest = fetchTestResults.find((r) => r.sourceId === source.id);

                return (
                  <Card key={source.id} className="bg-[#0B1F3A]/50 border-slate-700/50">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3">
                          <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center">
                            <Icon className="w-5 h-5 text-slate-400" />
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <h3 className="font-medium text-white">{source.name}</h3>
                              <Badge variant="outline" className={`text-[10px] ${statusColors[source.status]}`}>
                                {source.status}
                              </Badge>
                            </div>
                            <p className="text-xs text-slate-500 mt-0.5">{source.category} • {source.region}</p>
                            <a
                              href={source.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-[#C7A84A] hover:underline flex items-center gap-1 mt-1"
                            >
                              {source.url.slice(0, 40)}...
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          </div>
                        </div>
                        <div className="flex items-center gap-1">
                          <Switch
                            checked={source.isEnabled}
                            onCheckedChange={() => toggleDataSource(source.id)}
                          />
                        </div>
                      </div>

                      {/* Stats */}
                      <div className="grid grid-cols-4 gap-2 mt-4 pt-4 border-t border-slate-700/50">
                        <div className="text-center">
                          <p className="text-lg font-bold text-white">{source.fetchCount}</p>
                          <p className="text-[10px] text-slate-500">Fetches</p>
                        </div>
                        <div className="text-center">
                          <p className="text-lg font-bold text-green-400">{source.successCount}</p>
                          <p className="text-[10px] text-slate-500">Success</p>
                        </div>
                        <div className="text-center">
                          <p className="text-lg font-bold text-red-400">{source.errorCount}</p>
                          <p className="text-[10px] text-slate-500">Errors</p>
                        </div>
                        <div className="text-center">
                          <p className="text-lg font-bold text-blue-400">{source.itemsFetched}</p>
                          <p className="text-[10px] text-slate-500">Items</p>
                        </div>
                      </div>

                      {/* Last Fetch Info */}
                      <div className="mt-3 pt-3 border-t border-slate-700/50">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-slate-500">
                            Last fetch: {source.lastFetchAt ? new Date(source.lastFetchAt).toLocaleString() : 'Never'}
                          </span>
                          <span className="text-slate-500">
                            Avg response: {source.averageResponseTime}ms
                          </span>
                        </div>
                        {source.lastFetchError && (
                          <p className="text-xs text-red-400 mt-1">Error: {source.lastFetchError}</p>
                        )}
                      </div>

                      {/* Actions */}
                      <div className="flex items-center gap-2 mt-4">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleTestSource(source.id)}
                          disabled={testingSourceId === source.id}
                          className="border-slate-600 text-slate-300 flex-1"
                        >
                          {testingSourceId === source.id ? (
                            <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
                          ) : (
                            <Activity className="w-3 h-3 mr-1" />
                          )}
                          Test
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => fetchFromSource(source.id)}
                          disabled={isFetching || !source.isEnabled}
                          className="border-slate-600 text-slate-300 flex-1"
                        >
                          <RefreshCw className={`w-3 h-3 mr-1 ${isFetching ? 'animate-spin' : ''}`} />
                          Fetch
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => deleteDataSource(source.id)}
                          className="border-red-600/50 text-red-400 hover:bg-red-500/10"
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>

                      {/* Test Result */}
                      {lastTest && lastTest.sourceId === source.id && (
                        <div className={`mt-3 p-2 rounded text-xs ${lastTest.success ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
                          <div className="flex items-center gap-1">
                            {lastTest.success ? <Check className="w-3 h-3" /> : <X className="w-3 h-3" />}
                            <span>{lastTest.success ? 'Test passed' : 'Test failed'}</span>
                            <span className="text-slate-500 ml-2">({lastTest.responseTime}ms)</span>
                          </div>
                          {lastTest.itemsFound > 0 && (
                            <p className="mt-1">Found {lastTest.itemsFound} items</p>
                          )}
                          {lastTest.errorMessage && (
                            <p className="mt-1">{lastTest.errorMessage}</p>
                          )}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
          </div>
        </TabsContent>

        {/* Error Logs Tab */}
        <TabsContent value="logs" className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Select value={logFilter} onValueChange={(v) => setLogFilter(v as LogLevel | 'all')}>
                <SelectTrigger className="w-40 bg-slate-800 border-slate-700 text-white">
                  <Filter className="w-4 h-4 mr-2" />
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-slate-700">
                  <SelectItem value="all">All Levels</SelectItem>
                  <SelectItem value="success">Success</SelectItem>
                  <SelectItem value="info">Info</SelectItem>
                  <SelectItem value="warning">Warning</SelectItem>
                  <SelectItem value="error">Error</SelectItem>
                  <SelectItem value="critical">Critical</SelectItem>
                </SelectContent>
              </Select>
              <span className="text-sm text-slate-500">
                {filteredLogs.length} logs
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                onClick={handleClearResolvedLogs}
                className="border-slate-600 text-slate-300"
              >
                <Trash className="w-4 h-4 mr-2" />
                Clear Resolved
              </Button>
              <Button
                variant="outline"
                onClick={() => clearLogs()}
                className="border-red-600/50 text-red-400"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Clear All
              </Button>
            </div>
          </div>

          {/* Logs List */}
          <div className="space-y-2 max-h-[600px] overflow-y-auto">
            {filteredLogs.map((log) => (
              <div
                key={log.id}
                className={`p-3 rounded-lg border ${
                  log.resolved ? 'border-slate-700/30 bg-slate-800/30' : 'border-slate-700/50 bg-slate-800/50'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <Badge className={`${logLevelColors[log.level]} text-[10px]`}>
                      {log.level}
                    </Badge>
                    <div>
                      <p className={`text-sm ${log.resolved ? 'text-slate-500 line-through' : 'text-white'}`}>
                        {log.message}
                      </p>
                      {log.details && (
                        <p className="text-xs text-slate-500 mt-1">{log.details}</p>
                      )}
                      <div className="flex items-center gap-3 mt-1">
                        <span className="text-[10px] text-slate-500">{log.category}</span>
                        <span className="text-[10px] text-slate-500">
                          {new Date(log.timestamp).toLocaleString()}
                        </span>
                        {log.source && (
                          <span className="text-[10px] text-slate-500">Source: {log.source}</span>
                        )}
                      </div>
                    </div>
                  </div>
                  {!log.resolved && log.level !== 'success' && log.level !== 'info' && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => resolveLog(log.id)}
                      className="border-green-600/50 text-green-400"
                    >
                      <Check className="w-3 h-3 mr-1" />
                      Resolve
                    </Button>
                  )}
                  {log.resolved && (
                    <Badge variant="outline" className="text-[10px] border-green-500/30 text-green-400">
                      Resolved
                    </Badge>
                  )}
                </div>
              </div>
            ))}
            {filteredLogs.length === 0 && (
              <div className="text-center py-12 text-slate-500">
                <CheckCircle className="w-12 h-12 mx-auto mb-3 text-green-500/50" />
                <p>No logs to display</p>
              </div>
            )}
          </div>
        </TabsContent>

        {/* System Health Tab */}
        <TabsContent value="health" className="space-y-4">
          <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <Activity className="w-5 h-5 text-[#C7A84A]" />
                Service Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {systemHealth.services.map((service) => (
                  <div
                    key={service.name}
                    className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      {service.status === 'up' ? (
                        <Wifi className="w-5 h-5 text-green-400" />
                      ) : service.status === 'degraded' ? (
                        <AlertTriangle className="w-5 h-5 text-amber-400" />
                      ) : (
                        <WifiOff className="w-5 h-5 text-red-400" />
                      )}
                      <div>
                        <p className="text-sm font-medium text-white">{service.name}</p>
                        {service.errorMessage && (
                          <p className="text-xs text-amber-400">{service.errorMessage}</p>
                        )}
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge
                        variant="outline"
                        className={`text-xs ${
                          service.status === 'up'
                            ? 'border-green-500/30 text-green-400'
                            : service.status === 'degraded'
                            ? 'border-amber-500/30 text-amber-400'
                            : 'border-red-500/30 text-red-400'
                        }`}
                      >
                        {service.status.toUpperCase()}
                      </Badge>
                      <p className="text-xs text-slate-500 mt-1">{service.responseTime}ms</p>
                    </div>
                  </div>
                ))}
              </div>
              <p className="text-xs text-slate-500 mt-3">
                Last checked: {new Date(systemHealth.lastCheck).toLocaleString()}
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Fetched Articles Tab */}
        <TabsContent value="articles" className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-400">
              Total articles fetched: <span className="text-white font-bold">{fetchedArticles.length}</span>
            </p>
          </div>

          <div className="space-y-3">
            {fetchedArticles.slice(0, 20).map((article) => {
              const source = dataSources.find((s) => s.id === article.sourceId);
              return (
                <Card key={article.id} className="bg-[#0B1F3A]/50 border-slate-700/50">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h3 className="font-medium text-white">{article.title}</h3>
                          <Badge
                            variant="outline"
                            className={`text-[10px] ${
                              article.status === 'new'
                                ? 'border-blue-500/30 text-blue-400'
                                : article.status === 'processed'
                                ? 'border-green-500/30 text-green-400'
                                : article.status === 'flagged'
                                ? 'border-amber-500/30 text-amber-400'
                                : 'border-red-500/30 text-red-400'
                            }`}
                          >
                            {article.status}
                          </Badge>
                        </div>
                        <p className="text-sm text-slate-400 mt-1 line-clamp-2">{article.summary}</p>
                        <div className="flex items-center gap-3 mt-2">
                          <span className="text-xs text-slate-500">Source: {source?.name || article.sourceId}</span>
                          <span className="text-xs text-slate-500">
                            Fetched: {new Date(article.fetchedAt).toLocaleString()}
                          </span>
                          <span className="text-xs text-[#C7A84A]">Relevance: {article.relevanceScore}%</span>
                        </div>
                        <div className="flex items-center gap-1 mt-2">
                          {article.tags.map((tag) => (
                            <span key={tag} className="px-2 py-0.5 text-[10px] bg-slate-800 text-slate-400 rounded">
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
            {fetchedArticles.length === 0 && (
              <div className="text-center py-12 text-slate-500">
                <FileText className="w-12 h-12 mx-auto mb-3 text-slate-600" />
                <p>No articles fetched yet</p>
                <p className="text-sm">Use the Fetch buttons to retrieve articles from sources</p>
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
