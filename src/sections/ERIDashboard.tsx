// ============================================
// ERI DASHBOARD SECTION
// Escalation Risk Index Management
// ============================================

import { useState } from 'react';
import { useAppStore } from '@/store';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import {
  TrendingUp,
  TrendingDown,
  Minus,
  Plus,
  History,
  BarChart3,
  Globe,
  Target,
  Zap,
} from 'lucide-react';
import {
  getERIColor,
  classifyERI,
  calculateERI,
  generateERIAssessment,
  type ERICalculationInput,
} from '@/lib/eriEngine';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';

export function ERIDashboard() {
  const { currentERI, eriHistory, addERIAssessment } = useAppStore();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [dimensionScores, setDimensionScores] = useState<ERICalculationInput>({
    military: 50,
    political: 50,
    proxy: 50,
    economic: 50,
    diplomatic: 50,
  });

  const handleCreateERI = () => {
    const newERI = generateERIAssessment({
      weekNumber: 13,
      year: 2026,
      dimensionScores,
      keyDevelopments: [
        {
          headline: 'New Regional Development',
          whatHappened: 'Significant geopolitical shift observed',
          whyItMatters: 'Potential escalation trigger',
          whoBenefits: 'Regional power brokers',
          whoLoses: 'Stability seekers',
          escalationImpact: 6,
        },
      ],
    });

    addERIAssessment(newERI);
    setIsCreateDialogOpen(false);
  };

  const radarData = currentERI
    ? currentERI.dimensions.map((d) => ({
        dimension: d.name,
        score: d.score,
        fullMark: 100,
      }))
    : [];

  const historyData = eriHistory
    .slice()
    .reverse()
    .map((eri) => ({
      week: `W${eri.weekNumber}`,
      score: eri.overallScore,
    }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">ERI Dashboard</h1>
          <p className="text-slate-400">Escalation Risk Index tracking and analysis</p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-[#C7A84A] hover:bg-[#d4b65c] text-[#0B1F3A] font-medium">
              <Plus className="w-4 h-4 mr-2" />
              New ERI Assessment
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-[#0B1F3A] border-slate-700 max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="text-white">Create New ERI Assessment</DialogTitle>
            </DialogHeader>
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(dimensionScores).map(([dimension, score]) => (
                  <div key={dimension}>
                    <Label className="text-slate-300 capitalize">{dimension} Score</Label>
                    <div className="flex items-center gap-3 mt-2">
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={score}
                        onChange={(e) =>
                          setDimensionScores((prev) => ({
                            ...prev,
                            [dimension]: parseInt(e.target.value),
                          }))
                        }
                        className="flex-1"
                      />
                      <span className="text-white w-10 text-right">{score}</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="p-4 bg-slate-800/50 rounded-lg">
                <p className="text-sm text-slate-400">Calculated ERI</p>
                <p
                  className="text-3xl font-bold"
                  style={{ color: getERIColor(calculateERI(dimensionScores)) }}
                >
                  {calculateERI(dimensionScores)}
                </p>
                <Badge
                  variant="outline"
                  className="mt-2"
                  style={{
                    borderColor: getERIColor(calculateERI(dimensionScores)),
                    color: getERIColor(calculateERI(dimensionScores)),
                  }}
                >
                  {classifyERI(calculateERI(dimensionScores))}
                </Badge>
              </div>

              <Button
                onClick={handleCreateERI}
                className="w-full bg-[#C7A84A] hover:bg-[#d4b65c] text-[#0B1F3A]"
              >
                Create Assessment
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Current ERI Overview */}
      {currentERI && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Score Card */}
          <Card className="bg-[#0B1F3A]/50 border-slate-700/50 lg:col-span-1">
            <CardContent className="p-6">
              <div className="text-center">
                <p className="text-sm text-slate-400 mb-2">Current ERI Score</p>
                <div
                  className="text-7xl font-bold"
                  style={{ color: getERIColor(currentERI.overallScore) }}
                >
                  {currentERI.overallScore}
                </div>
                <Badge
                  className="mt-3 px-4 py-1"
                  style={{
                    backgroundColor: `${getERIColor(currentERI.overallScore)}20`,
                    color: getERIColor(currentERI.overallScore),
                    borderColor: getERIColor(currentERI.overallScore),
                  }}
                  variant="outline"
                >
                  {currentERI.classification}
                </Badge>
                <div className="mt-4 pt-4 border-t border-slate-700/50">
                  <p className="text-xs text-slate-500">
                    Week {currentERI.weekNumber}, {currentERI.year}
                  </p>
                  <p className="text-xs text-slate-500">
                    Last updated: {new Date(currentERI.updatedAt).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Radar Chart */}
          <Card className="bg-[#0B1F3A]/50 border-slate-700/50 lg:col-span-1">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <Target className="w-5 h-5 text-[#C7A84A]" />
                Dimension Breakdown
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={radarData}>
                    <PolarGrid stroke="#1e293b" />
                    <PolarAngleAxis dataKey="dimension" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <PolarRadiusAxis
                      angle={90}
                      domain={[0, 100]}
                      tick={{ fill: '#64748b', fontSize: 10 }}
                    />
                    <Radar
                      name="ERI"
                      dataKey="score"
                      stroke="#C7A84A"
                      strokeWidth={2}
                      fill="#C7A84A"
                      fillOpacity={0.3}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Dimension Scores */}
          <Card className="bg-[#0B1F3A]/50 border-slate-700/50 lg:col-span-1">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-[#C7A84A]" />
                Dimension Scores
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {currentERI.dimensions.map((dim) => (
                <div key={dim.name}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-slate-300">{dim.name}</span>
                    <div className="flex items-center gap-2">
                      <span
                        className="text-sm font-bold"
                        style={{ color: getERIColor(dim.score) }}
                      >
                        {dim.score}
                      </span>
                      {dim.indicators[0]?.trend === 'up' && (
                        <TrendingUp className="w-3 h-3 text-red-400" />
                      )}
                      {dim.indicators[0]?.trend === 'down' && (
                        <TrendingDown className="w-3 h-3 text-green-400" />
                      )}
                      {dim.indicators[0]?.trend === 'stable' && (
                        <Minus className="w-3 h-3 text-slate-400" />
                      )}
                    </div>
                  </div>
                  <Progress value={dim.score} className="h-2" />
                  <p className="text-xs text-slate-500 mt-1">
                    Weight: {(dim.weight * 100).toFixed(0)}%
                  </p>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Trend Chart */}
      <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg text-white flex items-center gap-2">
            <History className="w-5 h-5 text-[#C7A84A]" />
            ERI History
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={historyData}>
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
                <Line
                  type="monotone"
                  dataKey="score"
                  stroke="#C7A84A"
                  strokeWidth={3}
                  dot={{ fill: '#C7A84A', strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, fill: '#C7A84A' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Scenarios & Indicators */}
      {currentERI && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Scenario Outlook */}
          <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <Globe className="w-5 h-5 text-[#C7A84A]" />
                Scenario Outlook
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {currentERI.scenarioOutlook.map((scenario) => (
                <div
                  key={scenario.id}
                  className={`p-4 rounded-lg border ${
                    scenario.probability === 'high'
                      ? 'border-red-500/30 bg-red-500/10'
                      : scenario.probability === 'moderate'
                      ? 'border-amber-500/30 bg-amber-500/10'
                      : 'border-green-500/30 bg-green-500/10'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-white">{scenario.name}</h4>
                    <Badge
                      variant="outline"
                      className={`text-xs capitalize ${
                        scenario.probability === 'high'
                          ? 'border-red-500 text-red-400'
                          : scenario.probability === 'moderate'
                          ? 'border-amber-500 text-amber-400'
                          : 'border-green-500 text-green-400'
                      }`}
                    >
                      {scenario.probability} probability
                    </Badge>
                  </div>
                  <p className="text-sm text-slate-400">{scenario.description}</p>
                  <div className="mt-2">
                    <span className="text-xs text-slate-500">Triggers: </span>
                    <span className="text-xs text-slate-400">
                      {scenario.triggers.join(', ')}
                    </span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Indicators to Watch */}
          <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <Zap className="w-5 h-5 text-[#C7A84A]" />
                Indicators to Watch
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {currentERI.indicatorsToWatch.map((indicator, i) => (
                  <li
                    key={i}
                    className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg"
                  >
                    <div className="w-6 h-6 rounded-full bg-[#C7A84A]/20 flex items-center justify-center">
                      <span className="text-xs text-[#C7A84A]">{i + 1}</span>
                    </div>
                    <span className="text-sm text-slate-300">{indicator}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
