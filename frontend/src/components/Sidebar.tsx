// ============================================
// SIDEBAR NAVIGATION COMPONENT
// ============================================

import { useAppStore } from '@/store';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  FileText,
  ShieldAlert,
  TrendingUp,
  Newspaper,
  Archive,
  Users,
  Activity,
  Settings,
  ChevronLeft,
  ChevronRight,
  Globe,
} from 'lucide-react';
import { Button } from '@/components/ui/button';

interface NavItem {
  id: string;
  label: string;
  icon: React.ElementType;
  badge?: number;
}

const navItems: NavItem[] = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'content', label: 'Content Workflow', icon: FileText, badge: 3 },
  { id: 'risk', label: 'Risk Analysis', icon: ShieldAlert },
  { id: 'eri', label: 'ERI Dashboard', icon: TrendingUp },
  { id: 'briefs', label: 'Weekly Briefs', icon: Newspaper },
  { id: 'evidence', label: 'Evidence Archive', icon: Archive },
  { id: 'audience', label: 'Audience Intel', icon: Users },
  { id: 'monitor', label: 'System Monitor', icon: Activity },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export function Sidebar() {
  const { activeTab, setActiveTab, sidebarOpen, toggleSidebar, settings } = useAppStore();

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 h-full bg-[#0B1F3A] border-r border-slate-700/50 transition-all duration-300 z-50',
        sidebarOpen ? 'w-64' : 'w-16'
      )}
    >
      {/* Logo Section */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-slate-700/50">
        {sidebarOpen ? (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#C7A84A] to-[#5A6A7A] flex items-center justify-center">
              <Globe className="w-4 h-4 text-white" />
            </div>
            <div>
              <h1 className="text-sm font-semibold text-white">{settings.brandName}</h1>
              <p className="text-[10px] text-slate-400">{settings.tagline}</p>
            </div>
          </div>
        ) : (
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#C7A84A] to-[#5A6A7A] flex items-center justify-center mx-auto">
            <Globe className="w-4 h-4 text-white" />
          </div>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleSidebar}
          className={cn(
            'text-slate-400 hover:text-white hover:bg-slate-700/50',
            !sidebarOpen && 'hidden'
          )}
        >
          <ChevronLeft className="w-4 h-4" />
        </Button>
      </div>

      {/* Toggle Button (when collapsed) */}
      {!sidebarOpen && (
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleSidebar}
          className="absolute -right-3 top-20 w-6 h-6 rounded-full bg-[#C7A84A] text-[#0B1F3A] hover:bg-[#d4b65c]"
        >
          <ChevronRight className="w-3 h-3" />
        </Button>
      )}

      {/* Navigation */}
      <nav className="p-2 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={cn(
                'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group relative',
                isActive
                  ? 'bg-[#C7A84A]/20 text-[#C7A84A] border border-[#C7A84A]/30'
                  : 'text-slate-400 hover:bg-slate-700/30 hover:text-slate-200',
                !sidebarOpen && 'justify-center px-2'
              )}
            >
              <Icon className={cn('w-5 h-5 flex-shrink-0', isActive && 'text-[#C7A84A]')} />
              {sidebarOpen && (
                <>
                  <span className="flex-1 text-left text-sm">{item.label}</span>
                  {item.badge && (
                    <span className="px-2 py-0.5 text-xs bg-red-500/20 text-red-400 rounded-full">
                      {item.badge}
                    </span>
                  )}
                </>
              )}
              {/* Tooltip for collapsed state */}
              {!sidebarOpen && (
                <div className="absolute left-full ml-2 px-2 py-1 bg-slate-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50">
                  {item.label}
                </div>
              )}
            </button>
          );
        })}
      </nav>

      {/* Safe Mode Indicator */}
      {sidebarOpen && (
        <div className="absolute bottom-4 left-4 right-4">
          <div className={cn(
            'p-3 rounded-lg border text-xs',
            useAppStore.getState().safeModeEnabled
              ? 'bg-green-500/10 border-green-500/30 text-green-400'
              : 'bg-amber-500/10 border-amber-500/30 text-amber-400'
          )}>
            <div className="flex items-center gap-2">
              <div className={cn(
                'w-2 h-2 rounded-full',
                useAppStore.getState().safeModeEnabled ? 'bg-green-500' : 'bg-amber-500'
              )} />
              <span className="font-medium">
                Safe Mode: {useAppStore.getState().safeModeEnabled ? 'ON' : 'OFF'}
              </span>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}
