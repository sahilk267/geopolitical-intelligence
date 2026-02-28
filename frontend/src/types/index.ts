// ============================================
// STRATEGIC CONTEXT - GEOPOLITICAL INTELLIGENCE PLATFORM
// Type Definitions
// ============================================

// --------------------------------------------
// RISK GOVERNANCE ENGINE TYPES
// --------------------------------------------

export interface RiskScores {
  legalRisk: number;        // 0-100
  defamationRisk: number;   // 0-100
  platformRisk: number;     // 0-100
  politicalSensitivity: number; // 0-100
  overallScore: number;     // Weighted average
}

export interface RiskFactors {
  namedIndividual: boolean;
  criminalAllegation: boolean;
  singleAnonymousSource: boolean;
  electionPeriod: boolean;
  warTopic: boolean;
  religiousFraming: boolean;
  ethnicTension: boolean;
  activeConflict: boolean;
  terrorismDesignation: boolean;
  israelMentioned: boolean;
  iranMentioned: boolean;
  palestineMentioned: boolean;
  usMilitaryInvolved: boolean;
}

export interface RiskAssessment {
  id: string;
  contentId: string;
  scores: RiskScores;
  factors: RiskFactors;
  assessedAt: string;
  assessedBy: string;
  requiresSeniorReview: boolean;
  safeModeBlocked: boolean;
  notes: string;
}

// --------------------------------------------
// EDITORIAL WORKFLOW TYPES
// --------------------------------------------

export type WorkflowStage = 
  | 'ingestion'
  | 'preliminary_screening'
  | 'research_layering'
  | 'risk_scoring'
  | 'script_drafting'
  | 'editorial_review'
  | 'final_approval'
  | 'archive_publish'
  | 'post_publish_monitoring'
  | 'correction';

export type ContentLayer = 
  | 'factual_reporting'
  | 'historical_context'
  | 'analytical_assessment'
  | 'scenario_analysis';

export type SourceTier = 1 | 2 | 3 | 4;

export interface Source {
  id: string;
  url: string;
  title: string;
  tier: SourceTier;
  archivedScreenshot?: string;
  archivedLink?: string;
  timestamp: string;
  credibilityScore: number;
}

export interface ContentItem {
  id: string;
  headline: string;
  summary: string;
  currentStage: WorkflowStage;
  layers: ContentLayer[];
  sources: Source[];
  riskAssessment?: RiskAssessment;
  script?: Script;
  priority: PriorityLevel;
  assignedTo?: string;
  createdAt: string;
  updatedAt: string;
  publishedAt?: string;
  status: ContentStatus;
  tags: string[];
  region: string;
  topic: string;
}

export type PriorityLevel = 0 | 1 | 2 | 3;
export type ContentStatus = 'draft' | 'in_review' | 'approved' | 'published' | 'corrected' | 'archived';

export interface Script {
  id: string;
  contentId: string;
  segments: ScriptSegment[];
  wordCount: number;
  estimatedDuration: number;
  version: number;
  approvedBy?: string;
  approvedAt?: string;
}

export interface ScriptSegment {
  id: string;
  type: 'headline' | 'facts' | 'background' | 'stakeholders' | 'analysis' | 'scenario' | 'closing';
  content: string;
  sources: string[];
  approved: boolean;
}

// --------------------------------------------
// ERI (ESCALATION RISK INDEX) TYPES
// --------------------------------------------

export interface ERIDimension {
  name: string;
  score: number; // 0-100
  weight: number;
  indicators: ERIIndicator[];
}

export interface ERIIndicator {
  id: string;
  name: string;
  value: number;
  trend: 'up' | 'down' | 'stable';
  description: string;
}

export interface ERIAssessment {
  id: string;
  weekNumber: number;
  year: number;
  overallScore: number;
  classification: 'Low' | 'Moderate' | 'Elevated' | 'High' | 'Critical';
  dimensions: ERIDimension[];
  keyDevelopments: KeyDevelopment[];
  scenarioOutlook: Scenario[];
  indicatorsToWatch: string[];
  createdAt: string;
  updatedAt: string;
}

export interface KeyDevelopment {
  id: string;
  headline: string;
  whatHappened: string;
  whyItMatters: string;
  whoBenefits: string;
  whoLoses: string;
  escalationImpact: number;
}

export interface Scenario {
  id: string;
  name: string;
  probability: 'low' | 'moderate' | 'high';
  description: string;
  triggers: string[];
}

// --------------------------------------------
// WEEKLY INTELLIGENCE BRIEF TYPES
// --------------------------------------------

export interface WeeklyBrief {
  id: string;
  weekNumber: number;
  year: number;
  title: string;
  subtitle: string;
  eriScore: number;
  version: string;
  releaseDate: string;
  executiveSummary: ExecutiveSummary;
  eriSection: ERIAssessment;
  keyDevelopments: KeyDevelopment[];
  energyWatch: EnergyWatch;
  stakeholderPositions: StakeholderPosition[];
  scenarioOutlook: Scenario[];
  indicatorsToWatch: string[];
  methodology: string;
}

export interface ExecutiveSummary {
  whatChanged: string;
  whatIsStable: string;
  riskIncreased: string;
  riskDecreased: string;
  militaryActivity: string;
  proxyActivity: string;
  diplomaticTrack: string;
}

export interface EnergyWatch {
  oilMovement: string;
  shippingRisk: string;
  sanctionsUpdate: string;
  currencyAdjustments: string;
  indiaAngle?: string;
}

export interface StakeholderPosition {
  actor: string;
  currentPosition: string;
  weeklyMovement: string;
  escalationImpact: number;
}

// --------------------------------------------
// EVIDENCE ARCHIVE TYPES
// --------------------------------------------

export interface EvidenceItem {
  id: string;
  contentId: string;
  type: 'screenshot' | 'document' | 'video' | 'audio' | 'link';
  url: string;
  archivedUrl?: string;
  timestamp: string;
  sourceTier: SourceTier;
  description: string;
  tags: string[];
  uploadedBy: string;
  uploadedAt: string;
}

// --------------------------------------------
// AUDIENCE INTELLIGENCE TYPES
// --------------------------------------------

export interface AudienceFeedback {
  id: string;
  contentId: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  sentimentScore: number;
  topic: string;
  comment: string;
  platform: string;
  timestamp: string;
}

export interface ViewerHeatmap {
  topic: string;
  demandScore: number;
  controversyScore: number;
  engagementDrop: number;
  trend: 'rising' | 'stable' | 'falling';
}

// --------------------------------------------
// USER & PERMISSION TYPES
// --------------------------------------------

export type UserRole = 'junior_editor' | 'senior_editor' | 'editor_in_chief' | 'admin';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  permissions: Permission[];
  createdAt: string;
}

export type Permission = 
  | 'view_content'
  | 'create_content'
  | 'edit_content'
  | 'approve_content'
  | 'publish_content'
  | 'delete_content'
  | 'manage_users'
  | 'view_analytics'
  | 'manage_settings'
  | 'override_safe_mode';

// --------------------------------------------
// SYSTEM SETTINGS
// --------------------------------------------

export interface SystemSettings {
  safeModeEnabled: boolean;
  riskThreshold: number;
  autoPublishEnabled: boolean;
  defaultPriority: PriorityLevel;
  emailNotifications: boolean;
  slackNotifications: boolean;
  weeklyBriefDay: string;
  brandName: string;
  tagline: string;
}

// --------------------------------------------
// DASHBOARD STATS
// --------------------------------------------

export interface DashboardStats {
  totalContent: number;
  inReview: number;
  publishedThisWeek: number;
  pendingRiskAssessment: number;
  averageRiskScore: number;
  currentERI: number;
  weeklySubscribers: number;
  monthlyRevenue: number;
}

// --------------------------------------------
// DATA SOURCE & SYSTEM MONITORING TYPES
// --------------------------------------------

export type DataSourceType = 'rss' | 'api' | 'webhook' | 'manual' | 'scraping';
export type DataSourceStatus = 'active' | 'inactive' | 'error' | 'paused' | 'testing';
export type LogLevel = 'info' | 'warning' | 'error' | 'critical' | 'success';

export interface DataSource {
  id: string;
  name: string;
  url: string;
  type: DataSourceType;
  status: DataSourceStatus;
  category: string;
  region: string;
  lastFetchAt: string | null;
  lastFetchStatus: 'success' | 'error' | 'pending' | null;
  lastFetchError: string | null;
  fetchCount: number;
  successCount: number;
  errorCount: number;
  averageResponseTime: number;
  itemsFetched: number;
  isEnabled: boolean;
  fetchInterval: number; // in minutes
  headers?: Record<string, string>;
  createdAt: string;
  updatedAt: string;
}

export interface FetchedArticle {
  id: string;
  sourceId: string;
  title: string;
  summary: string;
  url: string;
  publishedAt: string;
  fetchedAt: string;
  status: 'new' | 'processed' | 'rejected' | 'flagged';
  tags: string[];
  relevanceScore: number;
}

export interface SystemLog {
  id: string;
  timestamp: string;
  level: LogLevel;
  category: string;
  message: string;
  details?: string;
  source?: string;
  metadata?: Record<string, unknown>;
  resolved: boolean;
  resolvedAt?: string;
  resolvedBy?: string;
}

export interface SystemHealth {
  overall: 'healthy' | 'degraded' | 'critical';
  lastCheck: string;
  services: {
    name: string;
    status: 'up' | 'down' | 'degraded';
    responseTime: number;
    lastChecked: string;
    errorMessage?: string;
  }[];
}

export interface FetchTestResult {
  sourceId: string;
  timestamp: string;
  success: boolean;
  responseTime: number;
  itemsFound: number;
  errorMessage?: string;
  sampleData?: unknown;
}
