// ============================================
// HEADER COMPONENT
// Top Bar with Stats and User Actions
// ============================================

import { useAppStore } from '@/store';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Bell,
  Search,
  User,
  Shield,
  AlertTriangle,
} from 'lucide-react';
import { getRiskColor, classifyRisk } from '@/lib/riskEngine';

export function Header() {
  const { currentERI, safeModeEnabled, getDashboardStats } = useAppStore();
  const stats = getDashboardStats();

  return (
    <header className="h-16 bg-[#0B1F3A]/80 backdrop-blur-sm border-b border-slate-700/50 flex items-center justify-between px-6">
      {/* Left: Search and Quick Actions */}
      <div className="flex items-center gap-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search content, risks, evidence..."
            className="w-80 pl-10 pr-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-[#C7A84A]/50"
          />
        </div>
      </div>

      {/* Center: Live Stats */}
      <div className="flex items-center gap-6">
        {/* ERI Badge */}
        {currentERI && (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-800/50 rounded-lg border border-slate-700">
            <TrendingUp className="w-4 h-4 text-slate-400" />
            <span className="text-xs text-slate-400">ERI</span>
            <span
              className="text-sm font-bold"
              style={{ color: getRiskColor(currentERI.overallScore) }}
            >
              {currentERI.overallScore}
            </span>
            <Badge
              variant="outline"
              className="text-[10px]"
              style={{ borderColor: getRiskColor(currentERI.overallScore), color: getRiskColor(currentERI.overallScore) }}
            >
              {classifyRisk(currentERI.overallScore)}
            </Badge>
          </div>
        )}

        {/* Pending Reviews */}
        {stats.inReview > 0 && (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-amber-500/10 rounded-lg border border-amber-500/30">
            <AlertTriangle className="w-4 h-4 text-amber-500" />
            <span className="text-xs text-amber-400">{stats.inReview} Pending Review</span>
          </div>
        )}

        {/* Safe Mode Status */}
        {safeModeEnabled && (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 rounded-lg border border-green-500/30">
            <Shield className="w-4 h-4 text-green-500" />
            <span className="text-xs text-green-400">Safe Mode Active</span>
          </div>
        )}
      </div>

      {/* Right: User Actions */}
      <div className="flex items-center gap-3">
        <Button
          variant="ghost"
          size="icon"
          className="relative text-slate-400 hover:text-white hover:bg-slate-700/50"
        >
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
        </Button>

        <div className="flex items-center gap-3 pl-3 border-l border-slate-700">
          <div className="text-right">
            <p className="text-sm font-medium text-white">Editor-in-Chief</p>
            <p className="text-xs text-slate-400">Admin</p>
          </div>
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[#5A6A7A] to-[#0B1F3A] flex items-center justify-center border border-slate-600">
            <User className="w-4 h-4 text-slate-300" />
          </div>
        </div>
      </div>
    </header>
  );
}

// Need to import this for the header
import { TrendingUp } from 'lucide-react';
