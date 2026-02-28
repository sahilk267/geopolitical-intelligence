// ============================================
// MAIN LAYOUT COMPONENT
// Dashboard Shell with Sidebar Navigation
// ============================================

import { useAppStore } from '@/store';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { Dashboard } from '@/sections/Dashboard';
import { ContentWorkflow } from '@/sections/ContentWorkflow';
import { RiskAnalysis } from '@/sections/RiskAnalysis';
import { ERIDashboard } from '@/sections/ERIDashboard';
import { WeeklyBriefSection } from '@/sections/WeeklyBrief';
import { EvidenceArchive } from '@/sections/EvidenceArchive';
import { AudienceIntelligence } from '@/sections/AudienceIntelligence';
import { SystemMonitor } from '@/sections/SystemMonitor';
import { Settings } from '@/sections/Settings';

export function Layout() {
  const { activeTab, sidebarOpen } = useAppStore();

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'content':
        return <ContentWorkflow />;
      case 'risk':
        return <RiskAnalysis />;
      case 'eri':
        return <ERIDashboard />;
      case 'briefs':
        return <WeeklyBriefSection />;
      case 'evidence':
        return <EvidenceArchive />;
      case 'audience':
        return <AudienceIntelligence />;
      case 'monitor':
        return <SystemMonitor />;
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
    </div>
  );
}
