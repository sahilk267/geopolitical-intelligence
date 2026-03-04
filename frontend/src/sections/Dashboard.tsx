// ============================================
// DASHBOARD SECTION
// Main Overview with Stats and Charts
// ============================================

import { useAppStore } from '@/store';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
  FileText,
  ShieldAlert,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
} from 'lucide-react';
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
} from 'recharts';
import { getRiskColor } from '@/lib/riskEngine';
import { getERIColor, classifyERI } from '@/lib/eriEngine';

export function Dashboard() {
  const { contents, currentERI, eriHistory, getDashboardStats, setCreateDialogOpen, safeModeEnabled, settings } = useAppStore();
  const stats = getDashboardStats();

  const eriHistoryData = eriHistory?.slice(-5).map(eri => ({
    week: `W${eri.weekNumber}`,
    score: eri.overallScore
  })) || [];

  const contentPipelineData = [
    { stage: 'Ingestion', count: contents.filter(c => c.currentStage === 'ingestion').length },
    { stage: 'Screening', count: contents.filter(c => c.currentStage === 'preliminary_screening').length },
    { stage: 'Research', count: contents.filter(c => c.currentStage === 'research_layering').length },
    { stage: 'Risk scoring', count: contents.filter(c => c.currentStage === 'risk_scoring').length },
    { stage: 'Review', count: contents.filter(c => c.currentStage === 'editorial_review').length },
    { stage: 'Approved', count: contents.filter(c => c.currentStage === 'final_approval').length },
  ];

  const pendingApprovals = contents.filter(
    (c) => c.currentStage === 'final_approval' || c.currentStage === 'editorial_review'
  );

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-slate-400">Overview of your geopolitical intelligence platform</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-800">
            <Clock className="w-4 h-4 mr-2" />
            Last 7 Days
          </Button>
          <Button
            className="bg-[#C7A84A] hover:bg-[#d4b65c] text-[#0B1F3A] font-medium"
            onClick={() => setCreateDialogOpen(true)}
          >
            <FileText className="w-4 h-4 mr-2" />
            New Content
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* ERI Card */}
        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Current ERI</p>
                <div className="flex items-baseline gap-2 mt-1">
                  <span
                    className="text-3xl font-bold"
                    style={{ color: getERIColor(currentERI?.overallScore || 0) }}
                  >
                    {currentERI?.overallScore || 0}
                  </span>
                  <Badge
                    variant="outline"
                    className="text-xs"
                    style={{
                      borderColor: getERIColor(currentERI?.overallScore || 0),
                      color: getERIColor(currentERI?.overallScore || 0),
                    }}
                  >
                    {classifyERI(currentERI?.overallScore || 0)}
                  </Badge>
                </div>
              </div>
              <div
                className="w-12 h-12 rounded-lg flex items-center justify-center"
                style={{ backgroundColor: `${getERIColor(currentERI?.overallScore || 0)}20` }}
              >
                <TrendingUp
                  className="w-6 h-6"
                  style={{ color: getERIColor(currentERI?.overallScore || 0) }}
                />
              </div>
            </div>
            <div className="flex items-center gap-1 mt-4 text-xs">
              <span className="text-slate-500">Stability Index:</span>
              <span className={currentERI && currentERI.overallScore > 75 ? "text-red-400" : "text-green-400"}>
                {classifyERI(currentERI?.overallScore || 0)}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Content Stats */}
        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Total Content</p>
                <p className="text-3xl font-bold text-white mt-1">{stats.totalContent}</p>
              </div>
              <div className="w-12 h-12 rounded-lg bg-blue-500/20 flex items-center justify-center">
                <FileText className="w-6 h-6 text-blue-400" />
              </div>
            </div>
            <div className="flex items-center gap-1 mt-4 text-xs">
              <CheckCircle className="w-3 h-3 text-green-400" />
              <span className="text-green-400">{stats.publishedThisWeek}</span>
              <span className="text-slate-500">published this week</span>
            </div>
          </CardContent>
        </Card>

        {/* Risk Stats */}
        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Avg Risk Score</p>
                <p
                  className="text-3xl font-bold mt-1"
                  style={{ color: getRiskColor(stats.averageRiskScore) }}
                >
                  {stats.averageRiskScore}
                </p>
              </div>
              <div
                className="w-12 h-12 rounded-lg flex items-center justify-center"
                style={{ backgroundColor: `${getRiskColor(stats.averageRiskScore)}20` }}
              >
                <ShieldAlert
                  className="w-6 h-6"
                  style={{ color: getRiskColor(stats.averageRiskScore) }}
                />
              </div>
            </div>
            <div className="flex items-center gap-1 mt-4 text-xs">
              <AlertCircle className="w-3 h-3 text-amber-400" />
              <span className="text-amber-400">{stats.pendingRiskAssessment}</span>
              <span className="text-slate-500">pending assessment</span>
            </div>
          </CardContent>
        </Card>

      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* ERI Trend Chart */}
        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-[#C7A84A]" />
              ERI Trend (Last 5 Weeks)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={eriHistoryData}>
                  <defs>
                    <linearGradient id="eriGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#C7A84A" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#C7A84A" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="week" stroke="#64748b" fontSize={12} />
                  <YAxis stroke="#64748b" fontSize={12} domain={[0, 100]} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0B1F3A',
                      border: '1px solid #1e293b',
                      borderRadius: '8px',
                    }}
                    labelStyle={{ color: '#94a3b8' }}
                  />
                  <Area
                    type="monotone"
                    dataKey="score"
                    stroke="#C7A84A"
                    strokeWidth={2}
                    fill="url(#eriGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Content Pipeline */}
        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg text-white flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-400" />
              Content Pipeline
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={contentPipelineData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                  <XAxis type="number" stroke="#64748b" fontSize={12} />
                  <YAxis
                    type="category"
                    dataKey="stage"
                    stroke="#64748b"
                    fontSize={12}
                    width={80}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0B1F3A',
                      border: '1px solid #1e293b',
                      borderRadius: '8px',
                    }}
                    labelStyle={{ color: '#94a3b8' }}
                  />
                  <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pending Approvals */}
        <Card className="bg-[#0B1F3A]/50 border-slate-700/50 lg:col-span-2">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg text-white flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-amber-400" />
              Pending Approvals
            </CardTitle>
          </CardHeader>
          <CardContent>
            {pendingApprovals.length > 0 ? (
              <div className="space-y-3">
                {pendingApprovals.map((content) => (
                  <div
                    key={content.id}
                    className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700/50"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-white truncate">
                        {content.headline}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="outline" className="text-[10px] border-slate-600 text-slate-400">
                          {content.currentStage.replace('_', ' ')}
                        </Badge>
                        <span className="text-xs text-slate-500">{content.region}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        className="border-slate-600 text-slate-300 hover:bg-slate-700"
                      >
                        Review
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-slate-500">
                <CheckCircle className="w-12 h-12 mx-auto mb-3 text-green-500/50" />
                <p>All content has been reviewed</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* System Status */}
        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg text-white">System Status</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-slate-400">Safe Mode</span>
                <Badge
                  variant={safeModeEnabled ? 'default' : 'outline'}
                  className={safeModeEnabled ? 'bg-green-500' : 'border-slate-600 text-slate-400'}
                >
                  {safeModeEnabled ? 'Active' : 'Inactive'}
                </Badge>
              </div>
              <Progress value={safeModeEnabled ? 100 : 0} className="h-2" />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-slate-400">Risk Threshold</span>
                <span className="text-sm text-white">{settings.riskThreshold}</span>
              </div>
              <Progress value={settings.riskThreshold} className="h-2" />
            </div>

            <div className="pt-4 border-t border-slate-700/50">
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-400">Data Sources</span>
                <span className="text-slate-300">Synchronized</span>
              </div>
              <div className="flex items-center justify-between text-sm mt-2">
                <span className="text-slate-400">Last Update</span>
                <span className="text-slate-300">Just now</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
