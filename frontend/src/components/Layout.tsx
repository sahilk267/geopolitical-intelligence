// ============================================
// MAIN LAYOUT COMPONENT
// Dashboard Shell with Sidebar Navigation
// ============================================

import { useEffect, useState } from 'react';
import { useAppStore } from '@/store';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { Login } from './Login';
import { Dashboard } from '@/sections/Dashboard';
import { ContentWorkflow } from '@/sections/ContentWorkflow';
import { ContentFactory } from '@/sections/ContentFactory';
import { RiskAnalysis } from '@/sections/RiskAnalysis';
import { ERIDashboard } from '@/sections/ERIDashboard';
import { WeeklyBriefSection } from '@/sections/WeeklyBrief';
import { EvidenceArchive } from '@/sections/EvidenceArchive';
import { AudienceIntelligence } from '@/sections/AudienceIntelligence';
import { VideoProduction } from '@/sections/VideoProduction';
import { ProfileManagement } from '@/sections/ProfileManagement';
import { CampaignControl } from '@/sections/CampaignControl';
import { SystemMonitor } from '@/sections/SystemMonitor';
import { Settings } from '@/sections/Settings';
import AnalyticsDashboard from '@/sections/AnalyticsDashboard';
import { NewContentDialog } from './NewContentDialog';

export function Layout() {
  const { activeTab, sidebarOpen, currentUser, fetchAllData, fetchCurrentUser } = useAppStore();
  const [authLoaded, setAuthLoaded] = useState(false);

  useEffect(() => {
    fetchCurrentUser().finally(() => setAuthLoaded(true));
  }, [fetchCurrentUser]);

  useEffect(() => {
    if (currentUser) {
      fetchAllData();
    }
  }, [currentUser, fetchAllData]);

  if (!authLoaded) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-950 text-slate-100">
        <div className="animate-pulse rounded-2xl border border-slate-700 bg-slate-900/95 px-10 py-8 text-center text-lg">
          Initializing session...
        </div>
      </div>
    );
  }

  if (!currentUser) {
    return <Login />;
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'content':
        return <ContentWorkflow />;
      case 'factory':
        return <ContentFactory />;
      case 'risk':
        return <RiskAnalysis />;
      case 'eri':
        return <ERIDashboard />;
      case 'briefs':
        return <WeeklyBriefSection />;
      case 'profiles':
        return <ProfileManagement />;
      case 'campaigns':
        return <CampaignControl />;
      case 'evidence':
        return <EvidenceArchive />;
      case 'audience':
        return <AudienceIntelligence />;
      case 'video':
        return <VideoProduction />;
      case 'monitor':
        return <SystemMonitor />;
      case 'analytics':
        return <AnalyticsDashboard />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };


  return (
    <div className="flex h-screen bg-[#0a0f1a] text-slate-200 overflow-hidden">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className={`flex-1 flex flex-col transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-16'}`}>
        <Header />
        <main className="flex-1 overflow-auto p-6">
          {renderContent()}
        </main>
      </div>
      <NewContentDialog />
    </div>
  );
}
