// ============================================
// STRATEGIC CONTEXT - STATE MANAGEMENT
// Zustand Store
// ============================================

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  ContentItem,
  RiskAssessment,
  ERIAssessment,
  WeeklyBrief,
  EvidenceItem,
  AudienceFeedback,
  User,
  SystemSettings,
  DashboardStats,
  WorkflowStage,
  DataSource,
  SystemLog,
  FetchedArticle,
  SystemHealth,
  FetchTestResult,
  LogLevel,
} from '@/types';

// --------------------------------------------
// STORE STATE INTERFACE
// --------------------------------------------

interface AppState {
  // Content Management
  contents: ContentItem[];
  currentContent: ContentItem | null;
  
  // Risk Governance
  riskAssessments: RiskAssessment[];
  safeModeEnabled: boolean;
  riskThreshold: number;
  
  // ERI System
  eriHistory: ERIAssessment[];
  currentERI: ERIAssessment | null;
  
  // Weekly Briefs
  weeklyBriefs: WeeklyBrief[];
  currentBrief: WeeklyBrief | null;
  
  // Evidence Archive
  evidenceArchive: EvidenceItem[];
  
  // Audience Intelligence
  audienceFeedback: AudienceFeedback[];
  
  // Data Sources & Monitoring
  dataSources: DataSource[];
  fetchedArticles: FetchedArticle[];
  systemLogs: SystemLog[];
  systemHealth: SystemHealth;
  fetchTestResults: FetchTestResult[];
  isFetching: boolean;
  
  // Users
  currentUser: User | null;
  users: User[];
  
  // Settings
  settings: SystemSettings;
  
  // UI State
  activeTab: string;
  sidebarOpen: boolean;
  
  // Actions
  addContent: (content: ContentItem) => void;
  updateContent: (id: string, updates: Partial<ContentItem>) => void;
  deleteContent: (id: string) => void;
  setCurrentContent: (content: ContentItem | null) => void;
  moveToStage: (contentId: string, stage: WorkflowStage) => void;
  
  addRiskAssessment: (assessment: RiskAssessment) => void;
  updateRiskAssessment: (id: string, updates: Partial<RiskAssessment>) => void;
  toggleSafeMode: () => void;
  setRiskThreshold: (threshold: number) => void;
  
  addERIAssessment: (assessment: ERIAssessment) => void;
  setCurrentERI: (assessment: ERIAssessment | null) => void;
  
  addWeeklyBrief: (brief: WeeklyBrief) => void;
  setCurrentBrief: (brief: WeeklyBrief | null) => void;
  
  addEvidence: (evidence: EvidenceItem) => void;
  deleteEvidence: (id: string) => void;
  
  addAudienceFeedback: (feedback: AudienceFeedback) => void;
  
  // Data Source Actions
  addDataSource: (source: DataSource) => void;
  updateDataSource: (id: string, updates: Partial<DataSource>) => void;
  deleteDataSource: (id: string) => void;
  toggleDataSource: (id: string) => void;
  testDataSource: (id: string) => Promise<FetchTestResult>;
  fetchFromSource: (id: string) => Promise<void>;
  fetchAllSources: () => Promise<void>;
  
  // Log Actions
  addLog: (log: SystemLog) => void;
  clearLogs: () => void;
  resolveLog: (id: string) => void;
  
  // User Actions
  setCurrentUser: (user: User | null) => void;
  addUser: (user: User) => void;
  
  updateSettings: (settings: Partial<SystemSettings>) => void;
  setActiveTab: (tab: string) => void;
  toggleSidebar: () => void;
  
  // Computed
  getDashboardStats: () => DashboardStats;
  getContentsByStage: (stage: WorkflowStage) => ContentItem[];
  getContentsByRisk: (minRisk: number) => ContentItem[];
  getPendingApprovals: () => ContentItem[];
  getActiveSources: () => DataSource[];
  getErrorSources: () => DataSource[];
  getLogsByLevel: (level: LogLevel) => SystemLog[];
}

// --------------------------------------------
// INITIAL DATA
// --------------------------------------------

const initialSettings: SystemSettings = {
  safeModeEnabled: false,
  riskThreshold: 40,
  autoPublishEnabled: false,
  defaultPriority: 0,
  emailNotifications: true,
  slackNotifications: false,
  weeklyBriefDay: 'Friday',
  brandName: 'Strategic Context',
  tagline: 'Context. Evidence. Strategy.',
};

const sampleERI: ERIAssessment = {
  id: 'eri-001',
  weekNumber: 12,
  year: 2026,
  overallScore: 58,
  classification: 'Elevated',
  dimensions: [
    {
      name: 'Military',
      score: 62,
      weight: 0.25,
      indicators: [
        { id: 'm1', name: 'Troop Movements', value: 65, trend: 'up', description: 'Increased activity along border regions' },
        { id: 'm2', name: 'Airstrikes', value: 58, trend: 'stable', description: 'Continued operations at similar pace' },
      ],
    },
    {
      name: 'Political',
      score: 55,
      weight: 0.25,
      indicators: [
        { id: 'p1', name: 'Diplomatic Statements', value: 45, trend: 'down', description: 'Harsher rhetoric from key actors' },
        { id: 'p2', name: 'Sanctions Activity', value: 65, trend: 'up', description: 'New sanctions announced' },
      ],
    },
    {
      name: 'Proxy',
      score: 60,
      weight: 0.20,
      indicators: [
        { id: 'px1', name: 'Militia Activity', value: 62, trend: 'up', description: 'Increased proxy engagements' },
      ],
    },
    {
      name: 'Economic',
      score: 52,
      weight: 0.15,
      indicators: [
        { id: 'e1', name: 'Oil Price Volatility', value: 55, trend: 'up', description: 'Brent crude showing instability' },
      ],
    },
    {
      name: 'Diplomatic',
      score: 48,
      weight: 0.15,
      indicators: [
        { id: 'd1', name: 'Negotiation Progress', value: 40, trend: 'down', description: 'Stalled talks' },
      ],
    },
  ],
  keyDevelopments: [
    {
      id: 'kd1',
      headline: 'Strait of Hormuz Tensions',
      whatHappened: 'Naval presence increased in critical chokepoint',
      whyItMatters: 'Global energy security implications',
      whoBenefits: 'Alternative energy exporters',
      whoLoses: 'Import-dependent economies',
      escalationImpact: 7,
    },
  ],
  scenarioOutlook: [
    {
      id: 's1',
      name: 'Stabilization Path',
      probability: 'low',
      description: 'Diplomatic breakthrough reduces tensions',
      triggers: ['Negotiation resumption', 'Third-party mediation'],
    },
    {
      id: 's2',
      name: 'Controlled Escalation',
      probability: 'high',
      description: 'Limited conflict with contained scope',
      triggers: ['Proxy escalation', 'Retaliatory strikes'],
    },
    {
      id: 's3',
      name: 'Expanded Regional Conflict',
      probability: 'moderate',
      description: 'Multi-actor involvement broadens conflict',
      triggers: ['Alliance activation', 'Critical infrastructure attack'],
    },
  ],
  indicatorsToWatch: [
    'Diplomatic meeting scheduled',
    'Military drill announcements',
    'Sanctions vote in UN',
    'OPEC production decision',
  ],
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
};

// Sample Data Sources
const sampleDataSources: DataSource[] = [
  {
    id: 'source-reuters',
    name: 'Reuters World News',
    url: 'https://www.reuters.com/world/rss.xml',
    type: 'rss',
    status: 'active',
    category: 'International News',
    region: 'Global',
    lastFetchAt: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
    lastFetchStatus: 'success',
    lastFetchError: null,
    fetchCount: 156,
    successCount: 152,
    errorCount: 4,
    averageResponseTime: 1200,
    itemsFetched: 2847,
    isEnabled: true,
    fetchInterval: 30,
    createdAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'source-aljazeera',
    name: 'Al Jazeera Middle East',
    url: 'https://www.aljazeera.com/xml/rss/all.xml',
    type: 'rss',
    status: 'active',
    category: 'Regional News',
    region: 'Middle East',
    lastFetchAt: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
    lastFetchStatus: 'success',
    lastFetchError: null,
    fetchCount: 142,
    successCount: 138,
    errorCount: 4,
    averageResponseTime: 1500,
    itemsFetched: 2156,
    isEnabled: true,
    fetchInterval: 30,
    createdAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'source-bbc',
    name: 'BBC World',
    url: 'http://feeds.bbci.co.uk/news/world/rss.xml',
    type: 'rss',
    status: 'error',
    category: 'International News',
    region: 'Global',
    lastFetchAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    lastFetchStatus: 'error',
    lastFetchError: 'Connection timeout after 30000ms',
    fetchCount: 200,
    successCount: 185,
    errorCount: 15,
    averageResponseTime: 2800,
    itemsFetched: 3421,
    isEnabled: true,
    fetchInterval: 30,
    createdAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'source-ft',
    name: 'Financial Times',
    url: 'https://www.ft.com/world?format=rss',
    type: 'rss',
    status: 'paused',
    category: 'Financial News',
    region: 'Global',
    lastFetchAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    lastFetchStatus: 'success',
    lastFetchError: null,
    fetchCount: 89,
    successCount: 85,
    errorCount: 4,
    averageResponseTime: 2100,
    itemsFetched: 1245,
    isEnabled: false,
    fetchInterval: 60,
    createdAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'source-mea',
    name: 'MEA World News API',
    url: 'https://api.mea-news.com/v1/headlines',
    type: 'api',
    status: 'active',
    category: 'Regional News',
    region: 'Middle East',
    lastFetchAt: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
    lastFetchStatus: 'success',
    lastFetchError: null,
    fetchCount: 320,
    successCount: 318,
    errorCount: 2,
    averageResponseTime: 800,
    itemsFetched: 4520,
    isEnabled: true,
    fetchInterval: 15,
    headers: { 'Authorization': 'Bearer ***', 'Content-Type': 'application/json' },
    createdAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

// Sample System Logs
const sampleSystemLogs: SystemLog[] = [
  {
    id: 'log-001',
    timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
    level: 'success',
    category: 'Data Fetch',
    message: 'Successfully fetched 23 articles from Reuters World News',
    source: 'source-reuters',
    resolved: true,
    resolvedAt: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
  },
  {
    id: 'log-002',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    level: 'error',
    category: 'Data Fetch',
    message: 'Failed to fetch from BBC World',
    details: 'Connection timeout after 30000ms. The server may be temporarily unavailable.',
    source: 'source-bbc',
    resolved: false,
  },
  {
    id: 'log-003',
    timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
    level: 'warning',
    category: 'Risk Assessment',
    message: 'High-risk content detected requiring senior review',
    details: 'Content ID: content-003 has risk score of 67, above threshold of 40',
    resolved: false,
  },
  {
    id: 'log-004',
    timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
    level: 'info',
    category: 'System',
    message: 'Weekly ERI assessment generated',
    resolved: true,
    resolvedAt: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'log-005',
    timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
    level: 'error',
    category: 'API',
    message: 'API rate limit exceeded for MEA World News',
    details: 'Received 429 Too Many Requests. Retry after 3600 seconds.',
    source: 'source-mea',
    resolved: true,
    resolvedAt: new Date(Date.now() - 11 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'log-006',
    timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    level: 'critical',
    category: 'System',
    message: 'Database backup failed',
    details: 'Insufficient storage space for backup. Please free up at least 5GB.',
    resolved: true,
    resolvedAt: new Date(Date.now() - 23 * 60 * 60 * 1000).toISOString(),
    resolvedBy: 'Admin',
  },
];

// Sample Fetched Articles
const sampleFetchedArticles: FetchedArticle[] = [
  {
    id: 'article-001',
    sourceId: 'source-reuters',
    title: 'Iran says it has begun enriching uranium to 60% purity at Fordow plant',
    summary: 'Iran has begun enriching uranium to 60% purity at its underground Fordow nuclear facility, the country\'s nuclear chief said on Saturday.',
    url: 'https://www.reuters.com/world/middle-east/',
    publishedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    fetchedAt: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
    status: 'new',
    tags: ['iran', 'nuclear', 'uranium'],
    relevanceScore: 85,
  },
  {
    id: 'article-002',
    sourceId: 'source-aljazeera',
    title: 'Saudi Arabia and Iran agree to restore diplomatic ties',
    summary: 'Saudi Arabia and Iran have agreed to restore diplomatic relations and reopen embassies within two months.',
    url: 'https://www.aljazeera.com/news/',
    publishedAt: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
    fetchedAt: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
    status: 'processed',
    tags: ['saudi-arabia', 'iran', 'diplomacy'],
    relevanceScore: 92,
  },
  {
    id: 'article-003',
    sourceId: 'source-mea',
    title: 'Israel conducts airstrikes in Syria, targets Iranian positions',
    summary: 'Israeli warplanes conducted airstrikes in Syria targeting positions associated with Iranian-backed militias.',
    url: 'https://api.mea-news.com/article/12345',
    publishedAt: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
    fetchedAt: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
    status: 'flagged',
    tags: ['israel', 'syria', 'iran', 'airstrike'],
    relevanceScore: 95,
  },
];

// System Health
const sampleSystemHealth: SystemHealth = {
  overall: 'healthy',
  lastCheck: new Date().toISOString(),
  services: [
    { name: 'RSS Feed Service', status: 'up', responseTime: 120, lastChecked: new Date().toISOString() },
    { name: 'API Gateway', status: 'up', responseTime: 85, lastChecked: new Date().toISOString() },
    { name: 'Risk Assessment Engine', status: 'up', responseTime: 250, lastChecked: new Date().toISOString() },
    { name: 'Database', status: 'up', responseTime: 45, lastChecked: new Date().toISOString() },
    { name: 'Storage', status: 'degraded', responseTime: 500, lastChecked: new Date().toISOString(), errorMessage: 'High disk usage (87%)' },
  ],
};

const sampleContents: ContentItem[] = [
  {
    id: 'content-001',
    headline: 'Understanding the Israel-Iran Strategic Rivalry: A Timeline Analysis',
    summary: 'Foundational context video examining the evolution of deterrence structure between Israel and Iran.',
    currentStage: 'archive_publish',
    layers: ['factual_reporting', 'historical_context', 'analytical_assessment'],
    sources: [
      {
        id: 'src1',
        url: 'https://example.com/source1',
        title: 'Official Treaty Document',
        tier: 1,
        timestamp: new Date().toISOString(),
        credibilityScore: 95,
      },
    ],
    priority: 1,
    assignedTo: 'editor-001',
    createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date().toISOString(),
    publishedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    status: 'published',
    tags: ['israel', 'iran', 'strategic-rivalry', 'foundational'],
    region: 'Middle East',
    topic: 'Strategic Analysis',
  },
  {
    id: 'content-002',
    headline: 'The Strait of Hormuz: Why This Chokepoint Shapes Global Energy Markets',
    summary: 'Analysis of the strategic importance of the Strait of Hormuz for global energy security.',
    currentStage: 'editorial_review',
    layers: ['factual_reporting', 'analytical_assessment'],
    sources: [],
    priority: 2,
    assignedTo: 'editor-002',
    createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date().toISOString(),
    status: 'in_review',
    tags: ['hormuz', 'energy', 'oil', 'chokepoint'],
    region: 'Middle East',
    topic: 'Energy Security',
  },
  {
    id: 'content-003',
    headline: 'Proxy Warfare in the Middle-East: Structure, Strategy, and Escalation Risk',
    summary: 'Structured mapping of proxy warfare dynamics in the region.',
    currentStage: 'risk_scoring',
    layers: ['factual_reporting', 'analytical_assessment', 'scenario_analysis'],
    sources: [],
    priority: 1,
    assignedTo: 'editor-001',
    createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date().toISOString(),
    status: 'draft',
    tags: ['proxy-warfare', 'escalation', 'militias'],
    region: 'Middle East',
    topic: 'Conflict Analysis',
  },
];

// --------------------------------------------
// STORE CREATION
// --------------------------------------------

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Initial State
      contents: sampleContents,
      currentContent: null,
      riskAssessments: [],
      safeModeEnabled: false,
      riskThreshold: 40,
      eriHistory: [sampleERI],
      currentERI: sampleERI,
      weeklyBriefs: [],
      currentBrief: null,
      evidenceArchive: [],
      audienceFeedback: [],
      dataSources: sampleDataSources,
      fetchedArticles: sampleFetchedArticles,
      systemLogs: sampleSystemLogs,
      systemHealth: sampleSystemHealth,
      fetchTestResults: [],
      isFetching: false,
      currentUser: null,
      users: [],
      settings: initialSettings,
      activeTab: 'dashboard',
      sidebarOpen: true,

      // Content Actions
      addContent: (content) => {
        set((state) => ({
          contents: [content, ...state.contents],
        }));
      },

      updateContent: (id, updates) => {
        set((state) => ({
          contents: state.contents.map((c) =>
            c.id === id ? { ...c, ...updates, updatedAt: new Date().toISOString() } : c
          ),
        }));
      },

      deleteContent: (id) => {
        set((state) => ({
          contents: state.contents.filter((c) => c.id !== id),
        }));
      },

      setCurrentContent: (content) => {
        set({ currentContent: content });
      },

      moveToStage: (contentId, stage) => {
        set((state) => ({
          contents: state.contents.map((c) =>
            c.id === contentId
              ? { ...c, currentStage: stage, updatedAt: new Date().toISOString() }
              : c
          ),
        }));
      },

      // Risk Actions
      addRiskAssessment: (assessment) => {
        set((state) => ({
          riskAssessments: [assessment, ...state.riskAssessments],
        }));
      },

      updateRiskAssessment: (id, updates) => {
        set((state) => ({
          riskAssessments: state.riskAssessments.map((ra) =>
            ra.id === id ? { ...ra, ...updates } : ra
          ),
        }));
      },

      toggleSafeMode: () => {
        set((state) => ({
          safeModeEnabled: !state.safeModeEnabled,
        }));
      },

      setRiskThreshold: (threshold) => {
        set({ riskThreshold: threshold });
      },

      // ERI Actions
      addERIAssessment: (assessment) => {
        set((state) => ({
          eriHistory: [assessment, ...state.eriHistory],
        }));
      },

      setCurrentERI: (assessment) => {
        set({ currentERI: assessment });
      },

      // Weekly Brief Actions
      addWeeklyBrief: (brief) => {
        set((state) => ({
          weeklyBriefs: [brief, ...state.weeklyBriefs],
        }));
      },

      setCurrentBrief: (brief) => {
        set({ currentBrief: brief });
      },

      // Evidence Actions
      addEvidence: (evidence) => {
        set((state) => ({
          evidenceArchive: [evidence, ...state.evidenceArchive],
        }));
      },

      deleteEvidence: (id) => {
        set((state) => ({
          evidenceArchive: state.evidenceArchive.filter((e) => e.id !== id),
        }));
      },

      // Audience Actions
      addAudienceFeedback: (feedback) => {
        set((state) => ({
          audienceFeedback: [feedback, ...state.audienceFeedback],
        }));
      },

      // Data Source Actions
      addDataSource: (source) => {
        set((state) => ({
          dataSources: [source, ...state.dataSources],
        }));
      },

      updateDataSource: (id, updates) => {
        set((state) => ({
          dataSources: state.dataSources.map((s) =>
            s.id === id ? { ...s, ...updates, updatedAt: new Date().toISOString() } : s
          ),
        }));
      },

      deleteDataSource: (id) => {
        set((state) => ({
          dataSources: state.dataSources.filter((s) => s.id !== id),
        }));
      },

      toggleDataSource: (id) => {
        set((state) => ({
          dataSources: state.dataSources.map((s) =>
            s.id === id ? { ...s, isEnabled: !s.isEnabled, updatedAt: new Date().toISOString() } : s
          ),
        }));
      },

      testDataSource: async (id) => {
        const source = get().dataSources.find((s) => s.id === id);
        if (!source) {
          throw new Error('Source not found');
        }

        const startTime = Date.now();
        
        // Simulate API test
        await new Promise((resolve) => setTimeout(resolve, 1000 + Math.random() * 2000));
        
        const success = Math.random() > 0.3; // 70% success rate for demo
        const responseTime = Date.now() - startTime;
        
        const result: FetchTestResult = {
          sourceId: id,
          timestamp: new Date().toISOString(),
          success,
          responseTime,
          itemsFound: success ? Math.floor(Math.random() * 50) + 10 : 0,
          errorMessage: success ? undefined : 'Connection timeout or invalid response format',
          sampleData: success ? { title: 'Sample Article', url: source.url } : undefined,
        };

        set((state) => ({
          fetchTestResults: [result, ...state.fetchTestResults].slice(0, 50),
        }));

        // Update source status
        get().updateDataSource(id, {
          lastFetchStatus: success ? 'success' : 'error',
          lastFetchError: success ? null : result.errorMessage || 'Unknown error',
          averageResponseTime: Math.round(
            (source.averageResponseTime * source.fetchCount + responseTime) / (source.fetchCount + 1)
          ),
        });

        // Add log entry
        get().addLog({
          id: `log-${Date.now()}`,
          timestamp: new Date().toISOString(),
          level: success ? 'success' : 'error',
          category: 'Data Source Test',
          message: success ? `Test successful for ${source.name}` : `Test failed for ${source.name}`,
          details: success ? `Found ${result.itemsFound} items in ${responseTime}ms` : result.errorMessage,
          source: id,
          resolved: success,
        });

        return result;
      },

      fetchFromSource: async (id) => {
        set({ isFetching: true });
        const source = get().dataSources.find((s) => s.id === id);
        if (!source) {
          set({ isFetching: false });
          throw new Error('Source not found');
        }

        const startTime = Date.now();
        
        // Simulate fetch
        await new Promise((resolve) => setTimeout(resolve, 2000 + Math.random() * 3000));
        
        const success = Math.random() > 0.2; // 80% success rate
        const responseTime = Date.now() - startTime;
        const itemsFound = success ? Math.floor(Math.random() * 30) + 5 : 0;

        // Update source
        set((state) => ({
          dataSources: state.dataSources.map((s) =>
            s.id === id
              ? {
                  ...s,
                  lastFetchAt: new Date().toISOString(),
                  lastFetchStatus: success ? 'success' : 'error',
                  lastFetchError: success ? null : 'Fetch failed',
                  fetchCount: s.fetchCount + 1,
                  successCount: success ? s.successCount + 1 : s.successCount,
                  errorCount: success ? s.errorCount : s.errorCount + 1,
                  itemsFetched: s.itemsFetched + itemsFound,
                  averageResponseTime: Math.round(
                    (s.averageResponseTime * s.fetchCount + responseTime) / (s.fetchCount + 1)
                  ),
                  updatedAt: new Date().toISOString(),
                }
              : s
          ),
        }));

        // Add fetched articles if successful
        if (success) {
          const newArticles: FetchedArticle[] = Array.from({ length: itemsFound }, (_, i) => ({
            id: `article-${Date.now()}-${i}`,
            sourceId: id,
            title: `Fetched Article ${i + 1} from ${source.name}`,
            summary: 'This is a sample fetched article for demonstration purposes.',
            url: `${source.url}/article/${Date.now()}-${i}`,
            publishedAt: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString(),
            fetchedAt: new Date().toISOString(),
            status: 'new',
            tags: source.region === 'Middle East' ? ['middle-east'] : ['global'],
            relevanceScore: Math.floor(Math.random() * 40) + 60,
          }));

          set((state) => ({
            fetchedArticles: [...newArticles, ...state.fetchedArticles].slice(0, 100),
          }));
        }

        // Add log
        get().addLog({
          id: `log-${Date.now()}`,
          timestamp: new Date().toISOString(),
          level: success ? 'success' : 'error',
          category: 'Data Fetch',
          message: success 
            ? `Fetched ${itemsFound} articles from ${source.name}` 
            : `Failed to fetch from ${source.name}`,
          source: id,
          resolved: success,
        });

        set({ isFetching: false });
      },

      fetchAllSources: async () => {
        set({ isFetching: true });
        const activeSources = get().dataSources.filter((s) => s.isEnabled);
        
        for (const source of activeSources) {
          await get().fetchFromSource(source.id);
        }
        
        set({ isFetching: false });
      },

      // Log Actions
      addLog: (log) => {
        set((state) => ({
          systemLogs: [log, ...state.systemLogs].slice(0, 500),
        }));
      },

      clearLogs: () => {
        set({ systemLogs: [] });
      },

      resolveLog: (id) => {
        set((state) => ({
          systemLogs: state.systemLogs.map((log) =>
            log.id === id
              ? { ...log, resolved: true, resolvedAt: new Date().toISOString() }
              : log
          ),
        }));
      },

      // User Actions
      setCurrentUser: (user) => {
        set({ currentUser: user });
      },

      addUser: (user) => {
        set((state) => ({
          users: [user, ...state.users],
        }));
      },

      // Settings Actions
      updateSettings: (newSettings) => {
        set((state) => ({
          settings: { ...state.settings, ...newSettings },
        }));
      },

      // UI Actions
      setActiveTab: (tab) => {
        set({ activeTab: tab });
      },

      toggleSidebar: () => {
        set((state) => ({
          sidebarOpen: !state.sidebarOpen,
        }));
      },

      // Computed
      getDashboardStats: () => {
        const state = get();
        const publishedThisWeek = state.contents.filter(
          (c) =>
            c.publishedAt &&
            new Date(c.publishedAt) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
        ).length;

        const pendingRisk = state.contents.filter(
          (c) => c.currentStage === 'risk_scoring'
        ).length;

        const avgRisk =
          state.riskAssessments.length > 0
            ? state.riskAssessments.reduce((acc, ra) => acc + ra.scores.overallScore, 0) /
              state.riskAssessments.length
            : 0;

        return {
          totalContent: state.contents.length,
          inReview: state.contents.filter((c) => c.status === 'in_review').length,
          publishedThisWeek,
          pendingRiskAssessment: pendingRisk,
          averageRiskScore: Math.round(avgRisk),
          currentERI: state.currentERI?.overallScore || 0,
          weeklySubscribers: 2847,
          monthlyRevenue: 425000,
        };
      },

      getContentsByStage: (stage) => {
        return get().contents.filter((c) => c.currentStage === stage);
      },

      getContentsByRisk: (minRisk) => {
        return get().contents.filter((c) => {
          const risk = get().riskAssessments.find((ra) => ra.contentId === c.id);
          return risk && risk.scores.overallScore >= minRisk;
        });
      },

      getPendingApprovals: () => {
        return get().contents.filter(
          (c) => c.currentStage === 'final_approval' || c.currentStage === 'editorial_review'
        );
      },

      getActiveSources: () => {
        return get().dataSources.filter((s) => s.isEnabled && s.status === 'active');
      },

      getErrorSources: () => {
        return get().dataSources.filter((s) => s.status === 'error' || s.lastFetchStatus === 'error');
      },

      getLogsByLevel: (level) => {
        return get().systemLogs.filter((log) => log.level === level);
      },
    }),
    {
      name: 'strategic-context-storage',
      partialize: (state) => ({
        contents: state.contents,
        riskAssessments: state.riskAssessments,
        safeModeEnabled: state.safeModeEnabled,
        riskThreshold: state.riskThreshold,
        eriHistory: state.eriHistory,
        weeklyBriefs: state.weeklyBriefs,
        evidenceArchive: state.evidenceArchive,
        dataSources: state.dataSources,
        fetchedArticles: state.fetchedArticles,
        systemLogs: state.systemLogs,
        settings: state.settings,
      }),
    }
  )
);
