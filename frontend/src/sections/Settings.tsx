// ============================================
// SUPERADMIN CONTROL PANEL
// Complete platform management dashboard
// ============================================

import { useState, useEffect } from 'react';
import { useAppStore } from '@/store';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Shield,
  Bell,
  Globe,
  Users,
  Save,
  RefreshCw,
  Database,
  Lock,
  Key,
  Mic,
  Video,
  Play,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Settings2,
  Zap,
  Rss,
  Plus,
  Trash2,
  Eye,
  EyeOff,
  TestTube,
  Loader2,
  Volume2,
  Share2,
  Youtube,
  Send,
  Twitter,
  Facebook,
  Instagram,
  Linkedin,
  MessageSquare,
} from 'lucide-react';

// ── Types ──
interface ApiKeyStatus {
  gemini: { status: string; key_set: boolean; error?: string };
  elevenlabs: { status: string; key_set: boolean; error?: string };
  did: { status: string; key_set: boolean; error?: string };
  heygen: { status: string; key_set: boolean; error?: string };
  ollama?: { status: string; error?: string };
}

interface PipelineStatus {
  ai_configured: boolean;
  tts_engine: string;
  tts_configured: boolean;
  avatar_engine: string;
  avatar_configured: boolean;
}

interface DistributionPlatform {
  id: string;
  name: string;
  connected: boolean;
  channel_name?: string;
}

interface SourceItem {
  id: string;
  name: string;
  url: string;
  type: string;
  category: string;
  region: string;
  is_enabled: boolean;
  status: string;
  success_rate: number;
  items_fetched: number;
}

export function Settings() {
  const {
    settings,
    updateSettings: updateLocalSettings,
    safeModeEnabled,
    toggleSafeMode,
    riskThreshold,
    setRiskThreshold,
  } = useAppStore();

  // ── State ──
  const [activeTab, setActiveTab] = useState<'api-keys' | 'sources' | 'pipeline' | 'tts-video' | 'distribution' | 'governance' | 'general'>('api-keys');

  // API Keys
  const [geminiKey, setGeminiKey] = useState('');
  const [elevenlabsKey, setElevenlabsKey] = useState('');
  const [didKey, setDidKey] = useState('');
  const [heygenKey, setHeygenKey] = useState('');
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({});
  const [keyStatus, setKeyStatus] = useState<ApiKeyStatus | null>(null);
  const [testingKeys, setTestingKeys] = useState(false);
  const [savingKeys, setSavingKeys] = useState(false);
  const [telegramBotToken, setTelegramBotToken] = useState('');
  const [telegramChatId, setTelegramChatId] = useState('');

  // AI Provider Settings
  const [aiProvider, setAiProvider] = useState('gemini');
  const [ollamaBaseUrl, setOllamaBaseUrl] = useState('http://localhost:11434');
  const [ollamaModel, setOllamaModel] = useState('llama3.2');

  // Pipeline
  const [pipelineStatus, setPipelineStatus] = useState<PipelineStatus | null>(null);
  const [pipelineCategory, setPipelineCategory] = useState('');
  const [pipelineRegion, setPipelineRegion] = useState('Global');
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [pipelineResult, setPipelineResult] = useState<any>(null);
  const [categories, setCategories] = useState<{ category: string; article_count: number }[]>([]);

  // Sources
  const [sources, setSources] = useState<SourceItem[]>([]);
  const [loadingSources, setLoadingSources] = useState(false);
  const [newSource, setNewSource] = useState({ name: '', url: '', category: '', region: '', type: 'rss' });
  const [showAddSource, setShowAddSource] = useState(false);

  // TTS
  const [ttsEngine, setTtsEngine] = useState('gtts');
  const [voices, setVoices] = useState<any[]>([]);
  const [selectedVoice, setSelectedVoice] = useState('default');
  const [ttsTestText, setTtsTestText] = useState('This is a test of the text-to-speech engine for your intelligence platform.');
  const [ttsGenerating, setTtsGenerating] = useState(false);
  const [ttsResult, setTtsResult] = useState<any>(null);

  // Video
  const [avatarEngine, setAvatarEngine] = useState('did');
  const [videoResolution, setVideoResolution] = useState('1920x1080');
  const [shortClipDuration, setShortClipDuration] = useState(45);

  // Distribution
  const [distributionPlatforms, setDistributionPlatforms] = useState<DistributionPlatform[]>([]);
  const [loadingPlatforms, setLoadingPlatforms] = useState(false);
  const [testingPlatform, setTestingPlatform] = useState<string | null>(null);
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);

  // Saving
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');

  // ── Load data ──
  useEffect(() => {
    loadPipelineStatus();
    loadSources();
    loadVoices();
    loadCategories();
    loadAISettings();
    loadDistributionPlatforms();
  }, []);

  const loadAISettings = async () => {
    try {
      const aiSettings = await api.getSettings('ai') as any[];
      aiSettings.forEach(s => {
        if (s.key === 'ai_provider') setAiProvider(s.value);
        if (s.key === 'ollama_base_url') setOllamaBaseUrl(s.value);
        if (s.key === 'ollama_model') setOllamaModel(s.value);
      });

      const distSettings = await api.getSettings('distribution') as any[];
      distSettings.forEach(s => {
        if (s.key === 'telegram_bot_token') setTelegramBotToken(s.value);
        if (s.key === 'telegram_chat_id') setTelegramChatId(s.value);
      });
    } catch { /* ignore */ }
  };

  const loadPipelineStatus = async () => {
    try {
      const status = await api.getPipelineCapabilities() as PipelineStatus;
      setPipelineStatus(status);
      setTtsEngine(status.tts_engine || 'gtts');
      setAvatarEngine(status.avatar_engine || 'did');
    } catch { /* ignore */ }
  };

  const loadSources = async () => {
    setLoadingSources(true);
    try {
      const data = await api.getDataSources() as any[];
      setSources(data as SourceItem[]);
    } catch { /* ignore */ }
    setLoadingSources(false);
  };

  const loadVoices = async () => {
    try {
      const v = await api.getVoices() as any[];
      setVoices(v);
    } catch { /* ignore */ }
  };

  const loadCategories = async () => {
    try {
      const cats = await api.getReportCategories() as any[];
      setCategories(cats);
    } catch { /* ignore */ }
  };

  // ── Actions ──
  const handleSaveApiKeys = async () => {
    setSavingKeys(true);
    try {
      const keys: any = {};
      if (geminiKey) keys.gemini_key = geminiKey;
      if (elevenlabsKey) keys.elevenlabs_key = elevenlabsKey;
      if (didKey) keys.did_key = didKey;
      if (heygenKey) keys.heygen_key = heygenKey;

      if (Object.keys(keys).length > 0) {
        await api.updateApiKeys(keys);
        setGeminiKey('');
        setElevenlabsKey('');
        setDidKey('');
        setHeygenKey('');
      }

      // Always update distribution settings if they are touched
      await api.updateSettings({
        telegram_bot_token: telegramBotToken,
        telegram_chat_id: telegramChatId,
      });

      alert('✅ Settings saved successfully!');
      loadPipelineStatus();
    } catch (err: any) {
      alert('❌ Failed to save settings: ' + (err.message || 'Unknown error'));
    }
    setSavingKeys(false);
  };

  const handleTestApiKeys = async () => {
    setTestingKeys(true);
    try {
      const result = await api.testApiKeys() as ApiKeyStatus;
      setKeyStatus(result);
    } catch (err: any) {
      alert('❌ Failed to test API keys: ' + (err.message || 'Unknown error'));
    }
    setTestingKeys(false);
  };

  const handleRunPipeline = async () => {
    if (!pipelineCategory) {
      alert('Please enter or select a category to run the pipeline.');
      return;
    }
    setPipelineRunning(true);
    setPipelineResult(null);
    try {
      const result = await api.runFullPipeline(
        pipelineCategory,
        pipelineRegion,
        selectedVoice,
        true, // generate_short
        true, // generate_presenter
        selectedPlatforms // distribute_to
      );
      setPipelineResult(result);
    } catch (err: any) {
      setPipelineResult({ error: err.message });
    }
    setPipelineRunning(false);
  };

  const handleAddSource = async () => {
    if (!newSource.name || !newSource.url) {
      alert('Please enter source name and URL.');
      return;
    }
    try {
      await api.createSource(newSource);
      alert('✅ Source added successfully!');
      setNewSource({ name: '', url: '', category: '', region: '', type: 'rss' });
      setShowAddSource(false);
      loadSources();
    } catch (err: any) {
      alert('❌ Failed to add source: ' + (err.message || 'Unknown error'));
    }
  };

  const handleToggleSource = async (id: string) => {
    try {
      await api.toggleSource(id);
      loadSources();
    } catch { /* ignore */ }
  };

  const handleDeleteSource = async (id: string) => {
    if (!confirm('Are you sure you want to delete this source?')) return;
    try {
      await api.deleteSource(id);
      loadSources();
    } catch (err: any) {
      alert('❌ Failed to delete: ' + (err.message || 'Unknown error'));
    }
  };

  const handleFetchAllSources = async () => {
    try {
      await api.fetchAllSources();
      alert('✅ Fetching started for all enabled sources!');
      loadSources();
    } catch (err: any) {
      alert('❌ Fetch failed: ' + (err.message || 'Unknown error'));
    }
  };

  const loadDistributionPlatforms = async () => {
    try {
      setLoadingPlatforms(true);
      const data = await api.get('/distribution/platforms') as DistributionPlatform[];
      setDistributionPlatforms(data);
    } catch (err: any) {
      console.error('Failed to load distribution platforms:', err);
    } finally {
      setLoadingPlatforms(false);
    }
  };

  const handleTestPlatform = async (platformId: string) => {
    setTestingPlatform(platformId);
    try {
      const result = await api.post(`/distribution/test/${platformId}`, {}) as any;
      if (result.status === 'success') {
        alert(`✅ ${platformId} test successful! ${result.channel_name ? 'Channel: ' + result.channel_name : ''}`);
      } else {
        alert(`❌ ${platformId} test failed: ${result.message || 'Unknown error'}`);
      }
    } catch (err: any) {
      alert(`❌ Error testing ${platformId}: ${err.message || 'Unknown error'}`);
    } finally {
      setTestingPlatform(null);
    }
  };

  const handleConnectPlatform = async (platformId: string) => {
    if (platformId === 'telegram') {
      setActiveTab('api-keys');
      setTimeout(() => {
        alert('To connect Telegram, set your Bot Token and Chat ID in the Distribution section of the API Keys tab.');
      }, 100);
      return;
    }

    if (platformId === 'youtube') {
      alert('YouTube OAuth connection will be available in the next update. For now, please ensure YOUTUBE_CLIENT_ID is set in the backend.');
      return;
    }

    alert(`${platformId} connection is coming soon!`);
  };

  const handleTestTTS = async () => {
    setTtsGenerating(true);
    setTtsResult(null);
    try {
      const result = await api.generateAudioFromText(ttsTestText, selectedVoice);
      setTtsResult(result);
    } catch (err: any) {
      alert('❌ TTS test failed: ' + (err.message || 'Unknown error'));
    }
    setTtsGenerating(false);
  };

  const handleSaveAllSettings = async () => {
    setSaveStatus('saving');
    try {
      await api.updateSettings({
        tts_engine: ttsEngine,
        tts_voice_id: selectedVoice,
        avatar_engine: avatarEngine,
        default_video_resolution: videoResolution,
        short_clip_duration: String(shortClipDuration),
        risk_threshold: String(riskThreshold),
        safe_mode_enabled: String(safeModeEnabled),
        auto_publish_enabled: String(settings.autoPublishEnabled),
        ai_provider: aiProvider,
        ollama_base_url: ollamaBaseUrl,
        ollama_model: ollamaModel,
      });
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch {
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    }
  };

  // ── Status helpers ──
  const StatusBadge = ({ status }: { status: string }) => {
    const colors: Record<string, string> = {
      valid: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
      invalid: 'bg-red-500/20 text-red-400 border-red-500/30',
      not_configured: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      error: 'bg-red-500/20 text-red-400 border-red-500/30',
    };
    const icons: Record<string, any> = {
      valid: <CheckCircle className="w-3 h-3" />,
      invalid: <XCircle className="w-3 h-3" />,
      not_configured: <AlertTriangle className="w-3 h-3" />,
      error: <XCircle className="w-3 h-3" />,
    };
    return (
      <Badge className={`${colors[status] || colors.error} border flex items-center gap-1`}>
        {icons[status] || icons.error}
        {status.replace('_', ' ').toUpperCase()}
      </Badge>
    );
  };

  // ── TAB BUTTONS ──
  const tabs = [
    { id: 'api-keys' as const, label: 'API Keys', icon: Key },
    { id: 'sources' as const, label: 'Sources', icon: Rss },
    { id: 'pipeline' as const, label: 'Pipeline', icon: Zap },
    { id: 'tts-video' as const, label: 'TTS & Video', icon: Video },
    { id: 'distribution' as const, label: 'Distribution', icon: Share2 },
    { id: 'governance' as const, label: 'Governance', icon: Shield },
    { id: 'general' as const, label: 'General', icon: Settings2 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Settings2 className="w-7 h-7 text-[#C7A84A]" />
            SuperAdmin Control Panel
          </h1>
          <p className="text-slate-400">Manage API keys, sources, pipeline, audio/video settings — everything in one place</p>
        </div>
        <Button
          onClick={handleSaveAllSettings}
          disabled={saveStatus === 'saving'}
          className="bg-[#C7A84A] hover:bg-[#d4b65c] text-[#0B1F3A] font-medium"
        >
          {saveStatus === 'saving' ? (
            <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Saving...</>
          ) : saveStatus === 'saved' ? (
            <><CheckCircle className="w-4 h-4 mr-2" /> Saved!</>
          ) : saveStatus === 'error' ? (
            <><XCircle className="w-4 h-4 mr-2" /> Error</>
          ) : (
            <><Save className="w-4 h-4 mr-2" /> Save All Settings</>
          )}
        </Button>
      </div>

      {/* Tab Navigation */}
      <div className="flex flex-wrap gap-2 p-1 bg-[#0B1F3A]/70 rounded-lg border border-slate-700/50">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-md text-sm font-medium transition-all ${activeTab === id
              ? 'bg-[#C7A84A] text-[#0B1F3A] shadow-lg shadow-[#C7A84A]/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
              }`}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </div>

      {/* ════════════════════════════════════════ */}
      {/* TAB: API KEYS                           */}
      {/* ════════════════════════════════════════ */}
      {activeTab === 'api-keys' && (
        <div className="space-y-6">
          {/* Status Overview */}
          <Card className="bg-gradient-to-r from-[#0B1F3A] to-[#162d50] border-slate-700/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-white flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <Key className="w-5 h-5 text-[#C7A84A]" />
                  API Key & AI Provider Status
                </span>
                <Button
                  size="sm"
                  onClick={handleTestApiKeys}
                  disabled={testingKeys}
                  className="bg-slate-700 hover:bg-slate-600 text-white"
                >
                  {testingKeys ? <Loader2 className="w-3 h-3 mr-1 animate-spin" /> : <TestTube className="w-3 h-3 mr-1" />}
                  Test All Keys
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
                {[
                  { name: 'Gemini AI', key: 'gemini', required: aiProvider === 'gemini', purpose: 'AI Reports & Scripts' },
                  { name: 'Ollama (Local)', key: 'ollama', required: aiProvider === 'ollama', purpose: 'Open Source AI' },
                  { name: 'ElevenLabs', key: 'elevenlabs', required: false, purpose: 'Premium TTS' },
                  { name: 'D-ID', key: 'did', required: false, purpose: 'Presenter Lip-Sync' },
                  { name: 'HeyGen', key: 'heygen', required: false, purpose: 'Alt. Lip-Sync' },
                ].map(({ name, key, required, purpose }) => (
                  <div key={key} className="p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
                    <div className="flex items-center justify-between mb-1">
                      <p className="text-sm font-medium text-white">{name}</p>
                      {required && <Badge className="bg-red-500/20 text-red-400 border border-red-500/30 text-[10px]">REQUIRED</Badge>}
                    </div>
                    <p className="text-xs text-slate-500 mb-2">{purpose}</p>
                    {keyStatus && keyStatus[key as keyof ApiKeyStatus] ? (
                      <StatusBadge status={keyStatus[key as keyof ApiKeyStatus].status} />
                    ) : (
                      <Badge className="bg-slate-600/30 text-slate-500 border border-slate-600/30">NOT TESTED</Badge>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* AI Provider Settings */}
          <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg text-white font-medium">Core AI Provider</CardTitle>
              <p className="text-xs text-slate-400">Select which AI engine to use for intelligence analysis and script generation.</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="text-slate-300">Select AI Engine</Label>
                <Select value={aiProvider} onValueChange={setAiProvider}>
                  <SelectTrigger className="bg-slate-800 border-slate-600 text-white mt-1 w-full md:w-1/2">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-slate-700">
                    <SelectItem value="gemini">Google Gemini (Cloud)</SelectItem>
                    <SelectItem value="ollama">Ollama (Local/Self-Hosted)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {aiProvider === 'ollama' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                  <div>
                    <Label className="text-slate-300">Ollama Base URL</Label>
                    <Input
                      value={ollamaBaseUrl}
                      onChange={(e) => setOllamaBaseUrl(e.target.value)}
                      className="bg-slate-800 border-slate-600 text-white mt-1"
                      placeholder="http://localhost:11434"
                    />
                    <p className="text-xs text-slate-500 mt-1">💡 Must include protocol (e.g., http://) and port.</p>
                  </div>
                  <div>
                    <Label className="text-slate-300">Ollama Model</Label>
                    <Input
                      value={ollamaModel}
                      onChange={(e) => setOllamaModel(e.target.value)}
                      className="bg-slate-800 border-slate-600 text-white mt-1"
                      placeholder="llama3.2"
                    />
                    <p className="text-xs text-slate-500 mt-1">💡 The model name exactly as pulled in Ollama.</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Key Input Forms */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {[
              { label: 'Google Gemini API Key', placeholder: 'AIzaSy...', value: geminiKey, setter: setGeminiKey, key: 'gemini', hint: 'Get from console.cloud.google.com → API & Services → Credentials' },
              { label: 'ElevenLabs API Key', placeholder: 'sk-...', value: elevenlabsKey, setter: setElevenlabsKey, key: 'elevenlabs', hint: 'Get from elevenlabs.io → Profile → API Key' },
              { label: 'D-ID API Key', placeholder: 'Basic ...', value: didKey, setter: setDidKey, key: 'did', hint: 'Get from studio.d-id.com → Settings → API' },
              { label: 'HeyGen API Key', placeholder: 'hg-...', value: heygenKey, setter: setHeygenKey, key: 'heygen', hint: 'Get from app.heygen.com → Settings → API' },
            ].map(({ label, placeholder, value, setter, key, hint }) => (
              <Card key={key} className="bg-[#0B1F3A]/50 border-slate-700/50">
                <CardContent className="pt-4">
                  <Label className="text-slate-300">{label}</Label>
                  <div className="relative mt-1">
                    <Input
                      type={showKeys[key] ? 'text' : 'password'}
                      placeholder={placeholder}
                      value={value}
                      onChange={(e) => setter(e.target.value)}
                      className="bg-slate-800 border-slate-600 text-white pr-10"
                    />
                    <button
                      onClick={() => setShowKeys(p => ({ ...p, [key]: !p[key] }))}
                      className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
                    >
                      {showKeys[key] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">💡 {hint}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="flex justify-end">
            <Button
              onClick={handleSaveApiKeys}
              disabled={savingKeys}
              className="bg-emerald-600 hover:bg-emerald-700 text-white"
            >
              {savingKeys ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Key className="w-4 h-4 mr-2" />}
              Save API Keys
            </Button>
          </div>

          <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
            <CardHeader>
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <Share2 className="w-5 h-5 text-[#C7A84A]" />
                Direct Distribution Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-slate-300">Telegram Bot Token</Label>
                  <Input
                    type="password"
                    placeholder="Enter Bot Token from @BotFather"
                    value={telegramBotToken}
                    onChange={(e) => setTelegramBotToken(e.target.value)}
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300">Telegram Chat ID</Label>
                  <Input
                    placeholder="Enter Channel/Group ID (e.g. -100...)"
                    value={telegramChatId}
                    onChange={(e) => setTelegramChatId(e.target.value)}
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                </div>
              </div>
              <p className="text-xs text-slate-500">
                Note: These values are used for direct Telegram posting. You can test the connection in the Distribution tab.
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* ════════════════════════════════════════ */}
      {/* TAB: SOURCES                            */}
      {/* ════════════════════════════════════════ */}
      {activeTab === 'sources' && (
        <div className="space-y-4">
          {/* Actions Bar */}
          <div className="flex items-center justify-between">
            <div className="flex gap-2">
              <Button
                onClick={() => setShowAddSource(!showAddSource)}
                className="bg-[#C7A84A] hover:bg-[#d4b65c] text-[#0B1F3A]"
              >
                <Plus className="w-4 h-4 mr-1" />
                Add Source
              </Button>
              <Button onClick={handleFetchAllSources} variant="outline" className="border-slate-600 text-slate-300">
                <RefreshCw className="w-4 h-4 mr-1" />
                Fetch All Now
              </Button>
              <Button onClick={loadSources} variant="outline" className="border-slate-600 text-slate-300">
                <RefreshCw className="w-4 h-4 mr-1" />
                Refresh List
              </Button>
            </div>
            <Badge className="bg-slate-700/50 text-slate-300 border-slate-600">
              {sources.length} sources configured
            </Badge>
          </div>

          {/* Add Source Form */}
          {showAddSource && (
            <Card className="bg-emerald-900/20 border-emerald-500/30">
              <CardContent className="pt-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div>
                    <Label className="text-slate-300">Source Name *</Label>
                    <Input
                      placeholder="BBC World News"
                      value={newSource.name}
                      onChange={(e) => setNewSource(p => ({ ...p, name: e.target.value }))}
                      className="bg-slate-800 border-slate-600 text-white mt-1"
                    />
                  </div>
                  <div>
                    <Label className="text-slate-300">RSS/API URL *</Label>
                    <Input
                      placeholder="https://feeds.bbci.co.uk/news/world/rss.xml"
                      value={newSource.url}
                      onChange={(e) => setNewSource(p => ({ ...p, url: e.target.value }))}
                      className="bg-slate-800 border-slate-600 text-white mt-1"
                    />
                  </div>
                  <div>
                    <Label className="text-slate-300">Type</Label>
                    <Select value={newSource.type} onValueChange={(v) => setNewSource(p => ({ ...p, type: v }))}>
                      <SelectTrigger className="bg-slate-800 border-slate-600 text-white mt-1">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-800 border-slate-700">
                        <SelectItem value="rss">RSS Feed</SelectItem>
                        <SelectItem value="api">API</SelectItem>
                        <SelectItem value="scraping">Web Scraping</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label className="text-slate-300">Category</Label>
                    <Input
                      placeholder="Middle East, Defense, Energy..."
                      value={newSource.category}
                      onChange={(e) => setNewSource(p => ({ ...p, category: e.target.value }))}
                      className="bg-slate-800 border-slate-600 text-white mt-1"
                    />
                  </div>
                  <div>
                    <Label className="text-slate-300">Region</Label>
                    <Input
                      placeholder="Global, Asia, Europe..."
                      value={newSource.region}
                      onChange={(e) => setNewSource(p => ({ ...p, region: e.target.value }))}
                      className="bg-slate-800 border-slate-600 text-white mt-1"
                    />
                  </div>
                  <div className="flex items-end">
                    <Button onClick={handleAddSource} className="bg-emerald-600 hover:bg-emerald-700 text-white w-full">
                      <Plus className="w-4 h-4 mr-1" />
                      Add Source
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Sources List */}
          {loadingSources ? (
            <div className="flex items-center justify-center p-8 text-slate-400">
              <Loader2 className="w-6 h-6 animate-spin mr-2" /> Loading sources...
            </div>
          ) : (
            <div className="space-y-2">
              {sources.map((source) => (
                <Card key={source.id} className="bg-[#0B1F3A]/50 border-slate-700/50">
                  <CardContent className="py-3 px-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3 flex-1">
                        <Switch
                          checked={source.is_enabled}
                          onCheckedChange={() => handleToggleSource(source.id)}
                        />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-white truncate">{source.name}</p>
                          <p className="text-xs text-slate-500 truncate">{source.url}</p>
                        </div>
                        {source.category && (
                          <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30">{source.category}</Badge>
                        )}
                        {source.region && (
                          <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30">{source.region}</Badge>
                        )}
                        <Badge className="bg-slate-700/50 text-slate-300 border-slate-600">
                          {source.items_fetched} articles
                        </Badge>
                        <Badge className={
                          source.status === 'success'
                            ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                            : source.status === 'error'
                              ? 'bg-red-500/20 text-red-400 border-red-500/30'
                              : 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
                        }>
                          {source.status || 'pending'}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-1 ml-3">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => api.fetchFromSource(source.id).then(() => { alert('✅ Fetching...'); loadSources(); })}
                          className="text-slate-400 hover:text-emerald-400"
                        >
                          <RefreshCw className="w-3.5 h-3.5" />
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleDeleteSource(source.id)}
                          className="text-slate-400 hover:text-red-400"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
              {sources.length === 0 && (
                <div className="text-center py-12 text-slate-500">
                  <Rss className="w-12 h-12 mx-auto mb-3 opacity-30" />
                  <p>No sources configured. Add your first RSS feed above.</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ════════════════════════════════════════ */}
      {/* TAB: PIPELINE                           */}
      {/* ════════════════════════════════════════ */}
      {activeTab === 'pipeline' && (
        <div className="space-y-6">
          {/* Pipeline Status */}
          <Card className="bg-gradient-to-r from-[#0B1F3A] to-[#162d50] border-slate-700/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <Zap className="w-5 h-5 text-[#C7A84A]" />
                Pipeline Capabilities
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {[
                  { name: 'AI Reports', ready: pipelineStatus?.ai_configured, detail: 'Gemini' },
                  { name: 'TTS Audio', ready: pipelineStatus?.tts_configured, detail: pipelineStatus?.tts_engine || 'none' },
                  { name: 'Video Rendering', ready: true, detail: 'FFmpeg' },
                  { name: 'Lip-Sync', ready: pipelineStatus?.avatar_configured, detail: pipelineStatus?.avatar_engine || 'none' },
                ].map(({ name, ready, detail }) => (
                  <div key={name} className={`p-3 rounded-lg border ${ready ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-red-500/10 border-red-500/30'}`}>
                    <div className="flex items-center gap-2 mb-1">
                      {ready ? <CheckCircle className="w-4 h-4 text-emerald-400" /> : <XCircle className="w-4 h-4 text-red-400" />}
                      <p className="text-sm font-medium text-white">{name}</p>
                    </div>
                    <p className="text-xs text-slate-400">{detail}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Run Pipeline */}
          <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <Play className="w-5 h-5 text-[#C7A84A]" />
                Run Full Pipeline
              </CardTitle>
              <p className="text-xs text-slate-500">Fetches articles → Generates journalist report → Creates audio → Renders video</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div>
                  <Label className="text-slate-300">Category *</Label>
                  {categories.length > 0 ? (
                    <Select value={pipelineCategory} onValueChange={setPipelineCategory}>
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
                      placeholder="Middle East, Defense..."
                      value={pipelineCategory}
                      onChange={(e) => setPipelineCategory(e.target.value)}
                      className="bg-slate-800 border-slate-600 text-white mt-1"
                    />
                  )}
                </div>
                <div>
                  <Label className="text-slate-300">Region</Label>
                  <Input
                    value={pipelineRegion}
                    onChange={(e) => setPipelineRegion(e.target.value)}
                    className="bg-slate-800 border-slate-600 text-white mt-1"
                  />
                </div>
                <div className="flex items-end">
                  <Button
                    onClick={handleRunPipeline}
                    disabled={pipelineRunning}
                    className="bg-emerald-600 hover:bg-emerald-700 text-white w-full"
                  >
                    {pipelineRunning ? (
                      <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Running Pipeline...</>
                    ) : (
                      <><Play className="w-4 h-4 mr-2" /> Run Pipeline</>
                    )}
                  </Button>
                </div>
              </div>

              {/* Distribution Selection */}
              <div className="pt-2">
                <Label className="text-slate-300 mb-2 block">Automated Distribution (Optional)</Label>
                <div className="flex flex-wrap gap-3">
                  {distributionPlatforms.filter(p => p.connected).map(platform => (
                    <div
                      key={platform.id}
                      onClick={() => {
                        if (selectedPlatforms.includes(platform.id)) {
                          setSelectedPlatforms(selectedPlatforms.filter(id => id !== platform.id));
                        } else {
                          setSelectedPlatforms([...selectedPlatforms, platform.id]);
                        }
                      }}
                      className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium cursor-pointer transition-all border ${selectedPlatforms.includes(platform.id)
                        ? 'bg-[#C7A84A] text-[#0B1F3A] border-[#C7A84A]'
                        : 'bg-slate-800 text-slate-400 border-slate-700 hover:border-slate-500'
                        }`}
                    >
                      {platform.id === 'telegram' && <Send className="w-3 h-3" />}
                      {platform.id === 'youtube' && <Youtube className="w-3 h-3" />}
                      {platform.name}
                    </div>
                  ))}
                  {distributionPlatforms.filter(p => p.connected).length === 0 && (
                    <p className="text-xs text-slate-500 italic">No platforms connected. Configure them in the Distribution tab.</p>
                  )}
                </div>
              </div>

              {/* Pipeline Results */}
              {pipelineResult && (
                <div className="mt-4 p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                  <h4 className="text-sm font-medium text-white mb-3">Pipeline Results</h4>
                  {pipelineResult.error ? (
                    <p className="text-red-400 text-sm">❌ {pipelineResult.error}</p>
                  ) : (
                    <div className="space-y-2">
                      {pipelineResult.steps && Object.entries(pipelineResult.steps).map(([step, data]: [string, any]) => (
                        <div key={step} className="flex items-center justify-between p-2 bg-slate-900/50 rounded">
                          <span className="text-sm text-slate-300 capitalize">{step.replace('_', ' ')}</span>
                          <div className="flex items-center gap-2">
                            {data.url && <a href={data.url} target="_blank" className="text-xs text-blue-400 hover:underline">Download</a>}
                            <Badge className={
                              data.status === 'success' ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                                : data.status === 'skipped' ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
                                  : 'bg-red-500/20 text-red-400 border-red-500/30'
                            }>
                              {data.status}
                            </Badge>
                          </div>
                        </div>
                      ))}
                      {pipelineResult.summary && (
                        <div className="mt-2 pt-2 border-t border-slate-700/50">
                          <p className="text-xs text-slate-400">
                            Overall: <span className="text-white font-medium">{pipelineResult.summary.overall_status}</span>
                            {' • '}{pipelineResult.summary.successful}/{pipelineResult.summary.total_steps} steps succeeded
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* ════════════════════════════════════════ */}
      {/* TAB: TTS & VIDEO                        */}
      {/* ════════════════════════════════════════ */}
      {activeTab === 'tts-video' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* TTS Settings */}
          <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <Mic className="w-5 h-5 text-[#C7A84A]" />
                Text-to-Speech Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="text-slate-300">TTS Engine</Label>
                <Select value={ttsEngine} onValueChange={setTtsEngine}>
                  <SelectTrigger className="bg-slate-800 border-slate-600 text-white mt-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-slate-700">
                    <SelectItem value="edge_tts">Edge-TTS (Free, High Quality) ⭐</SelectItem>
                    <SelectItem value="elevenlabs">ElevenLabs (Premium, Paid)</SelectItem>
                    <SelectItem value="piper">Piper TTS (Free, Offline)</SelectItem>
                    <SelectItem value="gtts">Google TTS (Free, Basic)</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-slate-500 mt-1">
                  {ttsEngine === 'edge_tts' ? '🎙️ Microsoft neural voices — free, no API key, 300+ voices, near-premium quality.' :
                    ttsEngine === 'elevenlabs' ? '🎤 Premium quality neural voices. Requires paid API key.' :
                      ttsEngine === 'piper' ? '🔒 Runs fully offline on your server. Good quality, no internet needed.' :
                        '🆓 Free but robotic. Emergency fallback only.'}
                </p>
              </div>


              <div>
                <Label className="text-slate-300">Default Voice</Label>
                <Select value={selectedVoice} onValueChange={setSelectedVoice}>
                  <SelectTrigger className="bg-slate-800 border-slate-600 text-white mt-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-slate-700">
                    {voices.length > 0 ? voices.map((v: any) => (
                      <SelectItem key={v.id} value={v.id}>{v.name}</SelectItem>
                    )) : (
                      <SelectItem value="default">Default Voice</SelectItem>
                    )}
                  </SelectContent>
                </Select>
              </div>

              {/* TTS Test */}
              <div className="pt-3 border-t border-slate-700/50">
                <Label className="text-slate-300">Test TTS</Label>
                <textarea
                  value={ttsTestText}
                  onChange={(e) => setTtsTestText(e.target.value)}
                  rows={3}
                  className="w-full mt-1 bg-slate-800 border border-slate-600 text-white rounded-md p-2 text-sm resize-none"
                />
                <Button
                  onClick={handleTestTTS}
                  disabled={ttsGenerating}
                  className="mt-2 bg-emerald-600 hover:bg-emerald-700 text-white"
                  size="sm"
                >
                  {ttsGenerating ? <Loader2 className="w-3 h-3 mr-1 animate-spin" /> : <Volume2 className="w-3 h-3 mr-1" />}
                  Generate Test Audio
                </Button>
                {ttsResult && !ttsResult.error && (
                  <div className="mt-2 p-2 bg-emerald-900/20 rounded border border-emerald-500/30">
                    <audio controls src={ttsResult.url} className="w-full h-8" />
                    <p className="text-xs text-slate-400 mt-1">Duration: {ttsResult.duration_seconds}s • Engine: {ttsResult.engine}</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Video Settings */}
          <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <Video className="w-5 h-5 text-[#C7A84A]" />
                Video Production Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="text-slate-300">Avatar/Lip-Sync Engine</Label>
                <Select value={avatarEngine} onValueChange={setAvatarEngine}>
                  <SelectTrigger className="bg-slate-800 border-slate-600 text-white mt-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-slate-700">
                    <SelectItem value="did">D-ID (Recommended)</SelectItem>
                    <SelectItem value="heygen">HeyGen</SelectItem>
                    <SelectItem value="none">None (Short clips only)</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-slate-500 mt-1">
                  Lip-sync engine creates presenter videos from audio. Requires API key.
                </p>
              </div>

              <div>
                <Label className="text-slate-300">Presenter Video Resolution</Label>
                <Select value={videoResolution} onValueChange={setVideoResolution}>
                  <SelectTrigger className="bg-slate-800 border-slate-600 text-white mt-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-slate-700">
                    <SelectItem value="1920x1080">1920×1080 (Full HD)</SelectItem>
                    <SelectItem value="1280x720">1280×720 (HD)</SelectItem>
                    <SelectItem value="3840x2160">3840×2160 (4K)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label className="text-slate-300">Short Clip Duration</Label>
                  <span className="text-sm text-white">{shortClipDuration}s</span>
                </div>
                <Slider
                  value={[shortClipDuration]}
                  onValueChange={([v]) => setShortClipDuration(v)}
                  min={15}
                  max={90}
                  step={5}
                />
                <p className="text-xs text-slate-500 mt-1">Duration for auto-generated short clips (Reels/Shorts format)</p>
              </div>

              <div className="pt-3 border-t border-slate-700/50">
                <p className="text-sm text-slate-300 mb-2">Video Output Format</p>
                <div className="grid grid-cols-2 gap-2">
                  <div className="p-2 bg-slate-800/50 rounded border border-slate-700/50">
                    <p className="text-xs font-medium text-white">Short Clips</p>
                    <p className="text-xs text-slate-500">1080×1920 (Vertical)</p>
                    <p className="text-xs text-slate-500">No presenter</p>
                  </div>
                  <div className="p-2 bg-slate-800/50 rounded border border-slate-700/50">
                    <p className="text-xs font-medium text-white">Presenter Videos</p>
                    <p className="text-xs text-slate-500">{videoResolution} (Landscape)</p>
                    <p className="text-xs text-slate-500">With lip-sync</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* ════════════════════════════════════════ */}
      {/* TAB: GOVERNANCE                         */}
      {/* ════════════════════════════════════════ */}
      {activeTab === 'governance' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <Shield className="w-5 h-5 text-[#C7A84A]" />
                Risk Governance
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                <div>
                  <Label className="text-slate-300">Safe Mode</Label>
                  <p className="text-xs text-slate-500">Block high-risk content from publishing</p>
                </div>
                <Switch checked={safeModeEnabled} onCheckedChange={toggleSafeMode} />
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label className="text-slate-300">Risk Threshold</Label>
                  <span className="text-sm text-white font-medium">{riskThreshold}</span>
                </div>
                <Slider
                  value={[riskThreshold]}
                  onValueChange={([v]) => setRiskThreshold(v)}
                  max={100}
                  step={5}
                />
                <p className="text-xs text-slate-500 mt-1">Content above this score requires senior review before publishing</p>
              </div>

              <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                <div>
                  <Label className="text-slate-300">Auto-Publish</Label>
                  <p className="text-xs text-slate-500">Automatically publish approved content</p>
                </div>
                <Switch
                  checked={settings.autoPublishEnabled}
                  onCheckedChange={(checked) => updateLocalSettings({ autoPublishEnabled: checked })}
                />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <Lock className="w-5 h-5 text-[#C7A84A]" />
                Security & Data
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Database className="w-5 h-5 text-slate-400" />
                  <div>
                    <p className="text-sm text-white">Database</p>
                    <p className="text-xs text-slate-500">PostgreSQL</p>
                  </div>
                </div>
                <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30">Connected</Badge>
              </div>

              <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Users className="w-5 h-5 text-slate-400" />
                  <div>
                    <p className="text-sm text-white">Active Sessions</p>
                    <p className="text-xs text-slate-500">Currently logged in</p>
                  </div>
                </div>
                <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30">1 session</Badge>
              </div>

              <div className="pt-3 border-t border-slate-700/50">
                <p className="text-sm font-medium text-red-400 mb-2">⚠️ Danger Zone</p>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => {
                    if (confirm('Are you sure? This will clear all local data and reload the app.')) {
                      useAppStore.getState().resetState();
                    }
                  }}
                  className="bg-red-500/20 hover:bg-red-500 text-red-400 hover:text-white border border-red-500/50"
                >
                  Reset Local State
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* ════════════════════════════════════════ */}
      {/* TAB: GENERAL                            */}
      {/* ════════════════════════════════════════ */}
      {activeTab === 'general' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <Globe className="w-5 h-5 text-[#C7A84A]" />
                Brand Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="text-slate-300">Brand Name</Label>
                <Input
                  value={settings.brandName}
                  onChange={(e) => updateLocalSettings({ brandName: e.target.value })}
                  className="bg-slate-800 border-slate-600 text-white mt-1"
                />
              </div>
              <div>
                <Label className="text-slate-300">Tagline</Label>
                <Input
                  value={settings.tagline}
                  onChange={(e) => updateLocalSettings({ tagline: e.target.value })}
                  className="bg-slate-800 border-slate-600 text-white mt-1"
                />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <Bell className="w-5 h-5 text-[#C7A84A]" />
                Notifications
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-slate-300">Email Notifications</Label>
                  <p className="text-xs text-slate-500">Receive alerts for important events</p>
                </div>
                <Switch
                  checked={settings.emailNotifications}
                  onCheckedChange={(checked) => updateLocalSettings({ emailNotifications: checked })}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-slate-300">Slack Notifications</Label>
                  <p className="text-xs text-slate-500">Send alerts to Slack channel</p>
                </div>
                <Switch
                  checked={settings.slackNotifications}
                  onCheckedChange={(checked) => updateLocalSettings({ slackNotifications: checked })}
                />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <RefreshCw className="w-5 h-5 text-[#C7A84A]" />
                Weekly Brief Schedule
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Label className="text-slate-300">Release Day</Label>
              <Select
                value={settings.weeklyBriefDay}
                onValueChange={(v) => updateLocalSettings({ weeklyBriefDay: v })}
              >
                <SelectTrigger className="bg-slate-800 border-slate-600 text-white mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-slate-700">
                  {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].map(d => (
                    <SelectItem key={d} value={d}>{d}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </CardContent>
          </Card>

          <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <Database className="w-5 h-5 text-[#C7A84A]" />
                Content Defaults
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Label className="text-slate-300">Default Priority</Label>
              <Select
                value={settings.defaultPriority.toString()}
                onValueChange={(v) => updateLocalSettings({ defaultPriority: parseInt(v) as 0 | 1 | 2 | 3 })}
              >
                <SelectTrigger className="bg-slate-800 border-slate-600 text-white mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-slate-700">
                  <SelectItem value="0">Normal</SelectItem>
                  <SelectItem value="1">Important</SelectItem>
                  <SelectItem value="2">Breaking</SelectItem>
                  <SelectItem value="3">Emergency</SelectItem>
                </SelectContent>
              </Select>
            </CardContent>
          </Card>
        </div>
      )}
      {/* ════════════════════════════════════════ */}
      {/* TAB: DISTRIBUTION                        */}
      {/* ════════════════════════════════════════ */}
      {activeTab === 'distribution' && (
        <div className="space-y-6">
          {/* Header Action */}
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">Social Media Distribution</h2>
            <Button
              onClick={loadDistributionPlatforms}
              variant="outline"
              size="sm"
              className="border-slate-700 text-slate-300"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${loadingPlatforms ? 'animate-spin' : ''}`} />
              Refresh Status
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {distributionPlatforms.map((platform) => (
              <Card key={platform.id} className="bg-[#0B1F3A]/50 border-slate-700/50 hover:border-slate-400/30 transition-all group">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-slate-800 rounded-lg group-hover:scale-110 transition-transform">
                        {platform.id === 'telegram' && <Send className="w-5 h-5 text-sky-400" />}
                        {platform.id === 'youtube' && <Youtube className="w-5 h-5 text-red-500" />}
                        {platform.id === 'twitter' && <Twitter className="w-5 h-5 text-blue-400" />}
                        {platform.id === 'facebook' && <Facebook className="w-5 h-5 text-blue-600" />}
                        {platform.id === 'instagram' && <Instagram className="w-5 h-5 text-pink-500" />}
                        {platform.id === 'linkedin' && <Linkedin className="w-5 h-5 text-blue-700" />}
                        {platform.id === 'whatsapp' && <MessageSquare className="w-5 h-5 text-emerald-500" />}
                      </div>
                      <div>
                        <CardTitle className="text-md text-white">{platform.name}</CardTitle>
                        <Badge variant="outline" className={platform.connected ? "text-emerald-400 border-emerald-500/30 bg-emerald-500/5" : "text-slate-500 border-slate-700"}>
                          {platform.connected ? 'Connected' : 'Not Connected'}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-2">
                  <div className="min-h-[40px] mb-4">
                    {platform.channel_name ? (
                      <p className="text-xs text-slate-400 line-clamp-2">
                        Active: <span className="text-white font-medium">{platform.channel_name}</span>
                      </p>
                    ) : (
                      <p className="text-xs text-slate-500 italic">No channel info available</p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      onClick={() => handleConnectPlatform(platform.id)}
                      className={`flex-1 ${platform.connected ? 'bg-slate-700 hover:bg-slate-600 text-white' : 'bg-[#C7A84A] hover:bg-[#d4b65c] text-[#0B1F3A]'}`}
                    >
                      {platform.connected ? 'Manage' : 'Connect'}
                    </Button>
                    {platform.connected && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleTestPlatform(platform.id)}
                        disabled={testingPlatform === platform.id}
                        className="border-slate-700 text-slate-300 hover:bg-slate-800"
                        title="Test Connection"
                      >
                        {testingPlatform === platform.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <TestTube className="w-4 h-4" />}
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card className="bg-gradient-to-br from-[#0B1F3A]/80 to-[#162d50]/80 border-slate-700/50 shadow-xl">
            <CardHeader className="border-b border-slate-700/50 pb-4">
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <Zap className="w-5 h-5 text-[#C7A84A]" />
                Automated Distribution Rules
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="space-y-4 max-w-2xl">
                <div className="flex items-center justify-between p-4 bg-slate-900/40 rounded-xl border border-slate-800 hover:border-slate-700 transition-all">
                  <div className="flex gap-4 items-start">
                    <div className="p-2 bg-sky-500/10 rounded-lg">
                      <Send className="w-5 h-5 text-sky-400" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-white">Auto-post to Telegram</p>
                      <p className="text-xs text-slate-400 mt-0.5">Push new intelligence reports to Telegram channel immediately</p>
                    </div>
                  </div>
                  <Switch checked={false} />
                </div>

                <div className="flex items-center justify-between p-4 bg-slate-900/40 rounded-xl border border-slate-800 opacity-60">
                  <div className="flex gap-4 items-start">
                    <div className="p-2 bg-red-500/10 rounded-lg">
                      <Youtube className="w-5 h-5 text-red-500" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-white">Auto-upload to YouTube</p>
                      <p className="text-xs text-slate-400 mt-0.5">Upload finished videos as Unlisted (Draft mode)</p>
                    </div>
                  </div>
                  <Switch checked={false} disabled />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
