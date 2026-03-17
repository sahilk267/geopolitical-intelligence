// ============================================
// STRATEGIC CONTEXT - STATE MANAGEMENT
// Zustand Store
// ============================================

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { api } from '@/lib/api';
import type {
  ContentItem,
  RiskAssessment,
  RiskFactors,
  RiskScores,
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
  VideoJob,
  VideoPipelineStatus,
  AutomationSchedule,
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

  // Video Production
  videoJobs: VideoJob[];
  videoPipelineStatus: VideoPipelineStatus | null;
  automationSchedules: AutomationSchedule[];

  // Users
  currentUser: User | null;
  users: User[];

  // Profiles & Campaigns
  profiles: any[];
  campaigns: any[];

  // Settings
  settings: SystemSettings;

  // UI State
  activeTab: string;
  sidebarOpen: boolean;
  createDialogOpen: boolean;

  // Actions
  addContent: (content: ContentItem) => Promise<void>;
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
  setCreateDialogOpen: (open: boolean) => void;

  // Computed
  getDashboardStats: () => DashboardStats;
  getContentsByStage: (stage: WorkflowStage) => ContentItem[];
  getContentsByRisk: (minRisk: number) => ContentItem[];
  getPendingApprovals: () => ContentItem[];
  getActiveSources: () => DataSource[];
  getErrorSources: () => DataSource[];
  getLogsByLevel: (level: LogLevel) => SystemLog[];

  // Data Fetching Actions
  fetchAllData: () => Promise<void>;
  fetchDashboardStats: () => Promise<void>;
  fetchERIHistory: () => Promise<void>;
  fetchDataSources: () => Promise<void>;
  fetchArticles: () => Promise<void>;
  fetchContents: () => Promise<void>;
  fetchVideoJobs: (status?: string, scriptId?: string) => Promise<void>;
  createVideoJob: (data: { script_id: string; priority?: number; resolution?: string }) => Promise<void>;
  cancelVideoJob: (jobId: string) => Promise<void>;
  fetchVideoPipelineStatus: () => Promise<void>;
  fetchAutomationSchedules: () => Promise<void>;
  createAutomationSchedule: (data: any) => Promise<void>;
  updateAutomationSchedule: (id: string, data: any) => Promise<void>;
  deleteAutomationSchedule: (id: string) => Promise<void>;
  runAutomationScheduleNow: (id: string) => Promise<void>;

  // Profile Actions
  fetchProfiles: () => Promise<void>;
  createProfile: (data: any) => Promise<void>;
  updateProfile: (id: string, data: any) => Promise<void>;
  deleteProfile: (id: string) => Promise<void>;

  // Campaign Actions
  fetchCampaigns: () => Promise<void>;
  createCampaign: (data: any) => Promise<void>;
  updateCampaign: (id: string, data: any) => Promise<void>;
  deleteCampaign: (id: string) => Promise<void>;
  triggerCampaign: (id: string) => Promise<void>;

  resetState: () => void;
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
const mapArticleToContentItem = (article: any): ContentItem => ({
  id: article.id,
  headline: article.headline,
  summary: article.summary,
  currentStage: article.status as WorkflowStage,
  status: article.status as any,
  priority: (article.priority || 0) as any,
  region: article.region || 'Global',
  topic: article.category || 'General',
  tags: article.tags || [],
  layers: [],
  sources: [],
  createdAt: article.created_at,
  updatedAt: article.created_at,
  publishedAt: article.published_at,
});

const normalizeRiskAssessment = (risk: any): RiskAssessment => {
  const scores = risk.scores || {
    legalRisk: risk.legal_risk ?? 0,
    defamationRisk: risk.defamation_risk ?? 0,
    platformRisk: risk.platform_risk ?? 0,
    politicalSensitivity: risk.political_risk ?? risk.politicalSensitivity ?? 0,
    overallScore: risk.overall_score ?? risk.overallScore ?? 0,
  };

  const factors: RiskFactors = risk.factors || risk.riskFactors || risk.risk_factors || {
    namedIndividual: false,
    criminalAllegation: false,
    singleAnonymousSource: false,
    electionPeriod: false,
    warTopic: false,
    religiousFraming: false,
    ethnicTension: false,
    activeConflict: false,
    terrorismDesignation: false,
    israelMentioned: false,
    iranMentioned: false,
    palestineMentioned: false,
    usMilitaryInvolved: false,
  };

  return {
    ...risk,
    scores,
    factors,
    riskFactors: risk.riskFactors || factors,
  };
};

const initialState: Partial<AppState> = {
  contents: [] as ContentItem[],
  currentContent: null,
  riskAssessments: [] as RiskAssessment[],
  safeModeEnabled: false,
  riskThreshold: 40,
  eriHistory: [] as ERIAssessment[],
  currentERI: null,
  weeklyBriefs: [] as WeeklyBrief[],
  currentBrief: null,
  evidenceArchive: [] as EvidenceItem[],
  audienceFeedback: [] as AudienceFeedback[],
  dataSources: [] as DataSource[],
  fetchedArticles: [] as FetchedArticle[],
  systemLogs: [] as SystemLog[],
  systemHealth: {
    overall: 'healthy',
    lastCheck: new Date().toISOString(),
    services: [],
  },
  fetchTestResults: [] as FetchTestResult[],
  isFetching: false,
  videoJobs: [] as VideoJob[],
  videoPipelineStatus: null,
  automationSchedules: [] as AutomationSchedule[],
  profiles: [],
  campaigns: [],
  currentUser: null,
  users: [] as User[],
  settings: initialSettings,
  activeTab: 'dashboard',
  sidebarOpen: true,
  createDialogOpen: false,
};

// --------------------------------------------
// STORE CREATION
// --------------------------------------------

export const useAppStore = create<AppState>()(
  persist(
    (set: any, get: any) => ({
      ...initialState as any,

      // Content Actions
      addContent: async (content: ContentItem) => {
        try {
          const newArticle = await api.createContent({
            headline: content.headline,
            content: content.summary, // Model uses 'content' for the body
            summary: content.summary,
            category: content.topic,
            region: content.region,
            priority: content.priority,
            tags: content.tags,
          }) as any;

          set((state: AppState) => ({
            contents: [{
              ...content,
              id: newArticle.id,
              createdAt: newArticle.created_at,
              updatedAt: newArticle.created_at,
            }, ...state.contents],
          }));
        } catch (error) {
          console.error('Failed to create content:', error);
          throw error;
        }
      },

      updateContent: (id: string, updates: Partial<ContentItem>) => {
        set((state: AppState) => ({
          contents: state.contents.map((c: ContentItem) =>
            c.id === id ? { ...c, ...updates, updatedAt: new Date().toISOString() } : c
          ),
        }));
      },

      deleteContent: (id: string) => {
        set((state: AppState) => ({
          contents: state.contents.filter((c: ContentItem) => c.id !== id),
        }));
      },

      setCurrentContent: (content: ContentItem | null) => {
        set({ currentContent: content });
      },

      moveToStage: (contentId: string, stage: WorkflowStage) => {
        set((state: AppState) => ({
          contents: state.contents.map((c: ContentItem) =>
            c.id === contentId
              ? { ...c, currentStage: stage, updatedAt: new Date().toISOString() }
              : c
          ),
        }));
      },

      // Risk Actions
      addRiskAssessment: (assessment: RiskAssessment) => {
        const normalized = normalizeRiskAssessment(assessment);
        set((state: AppState) => ({
          riskAssessments: [normalized, ...state.riskAssessments],
        }));
      },

      updateRiskAssessment: (id: string, updates: Partial<RiskAssessment>) => {
        set((state: AppState) => ({
          riskAssessments: state.riskAssessments.map((ra: RiskAssessment) =>
            ra.id === id ? { ...ra, ...updates } : ra
          ),
        }));
      },

      toggleSafeMode: async () => {
        const currentStatus = get().safeModeEnabled;
        try {
          const result = await api.toggleSafeMode(!currentStatus) as { enabled: boolean };
          set({ safeModeEnabled: result.enabled });
        } catch (error) {
          console.error('Failed to toggle safe mode:', error);
        }
      },

      setRiskThreshold: (threshold: number) => {
        set({ riskThreshold: threshold });
      },

      resetState: () => {
        localStorage.removeItem('strategic-context-storage');
        window.location.reload();
      },

      // ERI Actions
      addERIAssessment: (assessment: ERIAssessment) => {
        set((state: AppState) => ({
          eriHistory: [assessment, ...state.eriHistory],
        }));
      },

      setCurrentERI: (assessment: ERIAssessment | null) => {
        set({ currentERI: assessment });
      },

      // Weekly Brief Actions
      addWeeklyBrief: (brief: WeeklyBrief) => {
        set((state: AppState) => ({
          weeklyBriefs: [brief, ...state.weeklyBriefs],
        }));
      },

      setCurrentBrief: (brief: WeeklyBrief | null) => {
        set({ currentBrief: brief });
      },

      // Evidence Actions
      addEvidence: (evidence: EvidenceItem) => {
        set((state: AppState) => ({
          evidenceArchive: [evidence, ...state.evidenceArchive],
        }));
      },

      deleteEvidence: (id: string) => {
        set((state: AppState) => ({
          evidenceArchive: state.evidenceArchive.filter((e: EvidenceItem) => e.id !== id),
        }));
      },

      // Audience Actions
      addAudienceFeedback: (feedback: AudienceFeedback) => {
        set((state: AppState) => ({
          audienceFeedback: [feedback, ...state.audienceFeedback],
        }));
      },

      // Data Source Actions
      addDataSource: (source: DataSource) => {
        set((state: AppState) => ({
          dataSources: [source, ...state.dataSources],
        }));
      },

      updateDataSource: (id: string, updates: Partial<DataSource>) => {
        set((state: AppState) => ({
          dataSources: state.dataSources.map((s: DataSource) =>
            s.id === id ? { ...s, ...updates, updatedAt: new Date().toISOString() } : s
          ),
        }));
      },

      deleteDataSource: (id: string) => {
        set((state: AppState) => ({
          dataSources: state.dataSources.filter((s: DataSource) => s.id !== id),
        }));
      },

      toggleDataSource: (id: string) => {
        set((state: AppState) => ({
          dataSources: state.dataSources.map((s: DataSource) =>
            s.id === id ? { ...s, isEnabled: !s.isEnabled, updatedAt: new Date().toISOString() } : s
          ),
        }));
      },

      testDataSource: async (id: string) => {
        const source = get().dataSources.find((s: DataSource) => s.id === id);
        if (!source) throw new Error('Source not found');

        const startTime = Date.now();
        try {
          const result = await api.testDataSource(id) as FetchTestResult;

          set((state: AppState) => ({
            fetchTestResults: [result, ...state.fetchTestResults].slice(0, 50),
          }));

          // Update source status
          get().updateDataSource(id, {
            lastFetchStatus: result.success ? 'success' : 'error',
            lastFetchError: result.success ? null : result.errorMessage || 'Unknown error',
          });

          return result;
        } catch (error: any) {
          const result: FetchTestResult = {
            sourceId: id,
            timestamp: new Date().toISOString(),
            success: false,
            responseTime: Date.now() - startTime,
            itemsFound: 0,
            errorMessage: error.message,
          };
          set((state: AppState) => ({
            fetchTestResults: [result, ...state.fetchTestResults].slice(0, 50),
          }));
          return result;
        }
      },

      fetchFromSource: async (id: string) => {
        set({ isFetching: true });
        try {
          await api.fetchFromSource(id);
          // Reload sources and articles after fetch
          await Promise.all([get().fetchDataSources(), get().fetchArticles()]);
        } catch (error) {
          console.error('Fetch failed:', error);
        } finally {
          set({ isFetching: false });
        }
      },

      fetchAllSources: async () => {
        set({ isFetching: true });
        try {
          const activeSources = get().dataSources.filter((s: DataSource) => s.isEnabled);
          await Promise.all(activeSources.map((s: DataSource) => api.fetchFromSource(s.id)));
          await Promise.all([get().fetchDataSources(), get().fetchArticles()]);
        } catch (error) {
          console.error('Batch fetch failed:', error);
        } finally {
          set({ isFetching: false });
        }
      },

      // Fetching Actions
      fetchAllData: async () => {
        set({ isFetching: true });
        try {
          if (!localStorage.getItem('token')) {
            console.log('No token found, attempting auto-login...');
            await api.login();
          }

          // Fetch all data, but handle individual failures gracefully
          const fetchResults = await Promise.allSettled([
            api.getDataSources(),
            api.getContents(),
            api.getDashboardStats(),
            api.getCurrentERI(),
            api.getERIAssessments(),
            api.getRiskAssessments(),
            api.getSystemHealth(),
            api.getVideoPipelineStatus(),
            api.getProfiles(),
            api.getCampaigns(),
            api.getAutomationSchedules()
          ]);

          const [sources, contents, _stats, eri, history, risk, health, videoStatus, profiles, campaigns, schedules] = fetchResults;
          const normalizedRiskAssessments =
            risk.status === 'fulfilled'
              ? (risk.value as any[]).map(normalizeRiskAssessment)
              : [];

          set({
            dataSources: sources.status === 'fulfilled' ? sources.value : [],
            contents: contents.status === 'fulfilled' ? (contents.value as any[]).map(mapArticleToContentItem) : [],
            currentERI: eri.status === 'fulfilled' ? eri.value : null,
            eriHistory: history.status === 'fulfilled' ? (history.value as any[]) : [],
            riskAssessments: normalizedRiskAssessments,
            systemHealth: health.status === 'fulfilled' ? health.value : initialState.systemHealth,
            videoPipelineStatus: videoStatus.status === 'fulfilled' ? videoStatus.value : null,
            automationSchedules: schedules.status === 'fulfilled' ? (schedules.value as any[]) : [],
            profiles: profiles.status === 'fulfilled' ? (profiles.value as any[]) : [],
            campaigns: campaigns.status === 'fulfilled' ? (campaigns.value as any[]) : [],
            isFetching: false
          });

          // Log failures for debugging
          fetchResults.forEach((result, index) => {
            if (result.status === 'rejected') {
              console.warn(`Parallel fetch item ${index} failed:`, result.reason);
            }
          });

        } catch (error) {
          console.error('Failed to fetch data:', error);
          set({ isFetching: false });
        }
      },

      fetchDashboardStats: async () => {
        try {
          await api.getDashboardStats();
          // We don't have a specific state for dashboard stats, they are computed from other state items
          // but we can at least ensure we have the underlying data
          await Promise.all([get().fetchContents(), get().fetchDataSources()]);
        } catch (error) {
          console.error('Failed to fetch dashboard stats:', error);
        }
      },

      fetchERIHistory: async () => {
        try {
          const history = await api.getERIAssessments() as ERIAssessment[];
          set({
            eriHistory: history,
            currentERI: history.length > 0 ? history[0] : null
          });
        } catch (error) {
          console.error('Failed to fetch ERI history:', error);
        }
      },

      fetchDataSources: async () => {
        try {
          const sources = await api.getDataSources() as DataSource[];
          set({ dataSources: sources });
        } catch (error) {
          console.error('Failed to fetch data sources:', error);
        }
      },

      fetchArticles: async () => {
        try {
          const articles = await api.getArticles() as FetchedArticle[];
          set({ fetchedArticles: articles });
        } catch (error) {
          console.error('Failed to fetch articles:', error);
        }
      },

      fetchContents: async () => {
        try {
          const contents = await api.getContents() as any[];
          set({ contents: contents.map(mapArticleToContentItem) });
        } catch (error) {
          console.error('Failed to fetch contents:', error);
        }
      },

      fetchVideoJobs: async (status?: string, scriptId?: string) => {
        try {
          const jobs = await api.getVideoJobs(status, scriptId) as VideoJob[];
          set({ videoJobs: jobs });
        } catch (error) {
          console.error('Failed to fetch video jobs:', error);
        }
      },

      createVideoJob: async (data: { script_id: string; priority?: number; resolution?: string }) => {
        try {
          await api.createVideoJob(data);
          get().fetchVideoJobs();
        } catch (error) {
          console.error('Failed to create video job:', error);
        }
      },

      cancelVideoJob: async (jobId: string) => {
        try {
          await api.cancelVideoJob(jobId);
          await Promise.all([get().fetchVideoJobs(), get().fetchVideoPipelineStatus()]);
        } catch (error) {
          console.error('Failed to cancel video job:', error);
          throw error;
        }
      },

      fetchVideoPipelineStatus: async () => {
        try {
          const status = await api.getVideoPipelineStatus() as VideoPipelineStatus;
          set({ videoPipelineStatus: status });
        } catch (error) {
          console.error('Failed to fetch video pipeline status:', error);
        }
      },

      fetchAutomationSchedules: async () => {
        try {
          const schedules = await api.getAutomationSchedules() as AutomationSchedule[];
          set({ automationSchedules: schedules });
        } catch (error) {
          console.error('Failed to fetch schedules:', error);
        }
      },

      createAutomationSchedule: async (data: any) => {
        try {
          await api.createAutomationSchedule(data);
          get().fetchAutomationSchedules();
        } catch (error) {
          console.error('Failed to create schedule:', error);
        }
      },

      updateAutomationSchedule: async (id: string, data: any) => {
        try {
          await api.updateAutomationSchedule(id, data);
          get().fetchAutomationSchedules();
        } catch (error) {
          console.error('Failed to update schedule:', error);
        }
      },

      deleteAutomationSchedule: async (id: string) => {
        try {
          await api.deleteAutomationSchedule(id);
          get().fetchAutomationSchedules();
        } catch (error) {
          console.error('Failed to delete schedule:', error);
        }
      },

      runAutomationScheduleNow: async (id: string) => {
        try {
          await api.runAutomationScheduleNow(id);
          get().fetchAutomationSchedules();
        } catch (error) {
          console.error('Failed to run schedule:', error);
        }
      },

      // Profile Actions
      fetchProfiles: async () => {
        try {
          const profiles = await api.getProfiles();
          set({ profiles: profiles as any[] });
        } catch (error) {
          console.error('Failed to fetch profiles:', error);
        }
      },
      createProfile: async (data: any) => {
        try {
          await api.createProfile(data);
          get().fetchProfiles();
        } catch (error) {
          console.error('Failed to create profile:', error);
        }
      },
      updateProfile: async (id: string, data: any) => {
        try {
          await api.updateProfile(id, data);
          get().fetchProfiles();
        } catch (error) {
          console.error('Failed to update profile:', error);
        }
      },
      deleteProfile: async (id: string) => {
        try {
          await api.deleteProfile(id);
          get().fetchProfiles();
        } catch (error) {
          console.error('Failed to delete profile:', error);
        }
      },

      // Campaign Actions
      fetchCampaigns: async () => {
        try {
          const campaigns = await api.getCampaigns();
          set({ campaigns: campaigns as any[] });
        } catch (error) {
          console.error('Failed to fetch campaigns:', error);
        }
      },
      createCampaign: async (data: any) => {
        try {
          await api.createCampaign(data);
          get().fetchCampaigns();
        } catch (error) {
          console.error('Failed to create campaign:', error);
        }
      },
      updateCampaign: async (id: string, data: any) => {
        try {
          await api.updateCampaign(id, data);
          get().fetchCampaigns();
        } catch (error) {
          console.error('Failed to update campaign:', error);
        }
      },
      deleteCampaign: async (id: string) => {
        try {
          await api.deleteCampaign(id);
          get().fetchCampaigns();
        } catch (error) {
          console.error('Failed to delete campaign:', error);
        }
      },
      triggerCampaign: async (id: string) => {
        try {
          await api.triggerCampaign(id);
          get().fetchCampaigns();
        } catch (error) {
          console.error('Failed to trigger campaign:', error);
        }
      },

      // Log Actions
      addLog: (log: SystemLog) => {
        set((state: AppState) => ({
          systemLogs: [log, ...state.systemLogs].slice(0, 100),
        }));
      },

      clearLogs: () => {
        set({ systemLogs: [] });
      },

      resolveLog: (id: string) => {
        set((state: AppState) => ({
          systemLogs: state.systemLogs.map((log: SystemLog) =>
            log.id === id ? { ...log, status: 'resolved' as const } : log
          ),
        }));
      },

      // User Actions
      setCurrentUser: (user: User | null) => {
        set({ currentUser: user });
      },

      addUser: (user: User) => {
        set((state: AppState) => ({
          users: [...state.users, user],
        }));
      },

      // Settings & UI Actions
      updateSettings: (newSettings: Partial<SystemSettings>) => {
        set((state: AppState) => ({
          settings: { ...state.settings, ...newSettings },
        }));
      },

      setActiveTab: (tab: string) => {
        set({ activeTab: tab });
      },

      toggleSidebar: () => {
        set((state: AppState) => ({ sidebarOpen: !state.sidebarOpen }));
      },

      setCreateDialogOpen: (open: boolean) => {
        console.log('Setting createDialogOpen to:', open);
        set({ createDialogOpen: open });
      },
      // Computed
      getDashboardStats: () => {
        const state = get() as AppState;
        const total = state.contents.length;
        const inReview = state.contents.filter((c: ContentItem) =>
          ['editorial_review', 'final_approval'].includes(c.currentStage)
        ).length;
        const riskAverage = state.riskAssessments.length > 0
          ? state.riskAssessments.reduce((acc: number, ra: RiskAssessment) => acc + ra.scores.overallScore, 0) / state.riskAssessments.length
          : 0;
        const publishedThisWeek = state.contents.filter((c: ContentItem) =>
          c.publishedAt && new Date(c.publishedAt) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
        ).length;

        return {
          totalContent: total,
          inReview: inReview,
          publishedThisWeek: publishedThisWeek,
          pendingRiskAssessment: state.contents.filter((c: ContentItem) => c.currentStage === 'risk_scoring').length,
          averageRiskScore: Math.round(riskAverage),
          currentERI: state.currentERI?.overallScore || 0,
        };
      },

      getContentsByStage: (stage: WorkflowStage) => {
        return (get() as AppState).contents.filter((c: ContentItem) => c.currentStage === stage);
      },

      getContentsByRisk: (minRisk: number) => {
        const state = get() as AppState;
        return state.contents.filter((c: ContentItem) => {
          const assessment = state.riskAssessments.find((ra: RiskAssessment) => ra.contentId === c.id);
          return assessment ? assessment.scores.overallScore >= minRisk : false;
        });
      },

      getPendingApprovals: () => {
        return (get() as AppState).contents.filter((c: ContentItem) =>
          ['editorial_review', 'final_approval'].includes(c.currentStage)
        );
      },

      getActiveSources: () => {
        return (get() as AppState).dataSources.filter((s: DataSource) => s.isEnabled);
      },

      getErrorSources: () => {
        return (get() as AppState).dataSources.filter((s: DataSource) => s.lastFetchStatus === 'error');
      },

      getLogsByLevel: (level: LogLevel) => {
        return (get() as AppState).systemLogs.filter((log: SystemLog) => log.level === level);
      },
    }),
    {
      name: 'strategic-context-storage',
      partialize: (state: AppState) => ({
        settings: state.settings,
        sidebarOpen: state.sidebarOpen,
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
        videoJobs: state.videoJobs,
        automationSchedules: state.automationSchedules,
      }),
    }
  )
);
