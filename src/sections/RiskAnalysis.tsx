// ============================================
// RISK ANALYSIS SECTION
// 4-Dimensional Risk Scoring Dashboard
// ============================================

import { useState } from 'react';
import { useAppStore } from '@/store';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import {
  ShieldAlert,
  AlertTriangle,
  CheckCircle,
  XCircle,
  RefreshCw,
  Info,
  FileText,
  Gavel,
  Globe,
  Scale,
} from 'lucide-react';
import {
  classifyRisk,
  getRiskColor,
  getRiskBgColor,
  getRequiredApprovalLevel,
  getRiskMitigationSuggestions,
  checkSafeModeViolation,
  generateRiskAssessmentReport,
} from '@/lib/riskEngine';

export function RiskAnalysis() {
  const {
    contents,
    riskAssessments,
    safeModeEnabled,
    riskThreshold,
    toggleSafeMode,
    setRiskThreshold,
    addRiskAssessment,
  } = useAppStore();

  const [selectedContentId, setSelectedContentId] = useState<string | null>(null);

  const pendingRiskContent = contents.filter(
    (c) => c.currentStage === 'risk_scoring' && !riskAssessments.find((ra) => ra.contentId === c.id)
  );

  const assessedContent = contents.filter((c) =>
    riskAssessments.find((ra) => ra.contentId === c.id)
  );

  const selectedContent = selectedContentId
    ? contents.find((c) => c.id === selectedContentId)
    : null;

  const selectedRisk = selectedContentId
    ? riskAssessments.find((ra) => ra.contentId === selectedContentId)
    : null;

  const handleAssessRisk = (contentId: string) => {
    const content = contents.find((c) => c.id === contentId);
    if (!content) return;

    const assessment = generateRiskAssessmentReport(content, 'system');
    const safeModeCheck = checkSafeModeViolation(assessment.factors, safeModeEnabled);

    if (safeModeCheck.violated) {
      assessment.safeModeBlocked = true;
      assessment.notes += ` | Safe Mode Violations: ${safeModeCheck.reasons.join(', ')}`;
    }

    addRiskAssessment(assessment);
    setSelectedContentId(contentId);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Risk Analysis</h1>
          <p className="text-slate-400">4-dimensional risk scoring for content governance</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Switch
              id="safe-mode"
              checked={safeModeEnabled}
              onCheckedChange={toggleSafeMode}
            />
            <Label htmlFor="safe-mode" className="text-slate-300">
              Safe Mode
            </Label>
          </div>
        </div>
      </div>

      {/* Risk Threshold Setting */}
      <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-white">Risk Threshold</h3>
              <p className="text-xs text-slate-400">
                Content above this score requires senior review
              </p>
            </div>
            <div className="flex items-center gap-4 w-64">
              <Slider
                value={[riskThreshold]}
                onValueChange={([value]) => setRiskThreshold(value)}
                max={100}
                step={5}
                className="flex-1"
              />
              <span className="text-sm font-medium text-white w-10">{riskThreshold}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pending Assessment List */}
        <div className="lg:col-span-1 space-y-4">
          <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-amber-400" />
                Pending Assessment
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {pendingRiskContent.length > 0 ? (
                pendingRiskContent.map((content) => (
                  <div
                    key={content.id}
                    onClick={() => setSelectedContentId(content.id)}
                    className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                      selectedContentId === content.id
                        ? 'border-[#C7A84A] bg-[#C7A84A]/10'
                        : 'border-slate-700 bg-slate-800/50 hover:bg-slate-800'
                    }`}
                  >
                    <p className="text-sm font-medium text-white line-clamp-2">
                      {content.headline}
                    </p>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant="outline" className="text-[10px] border-slate-600 text-slate-400">
                        {content.region}
                      </Badge>
                      <span className="text-[10px] text-slate-500">
                        {content.tags.slice(0, 2).join(', ')}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-slate-500">
                  <CheckCircle className="w-12 h-12 mx-auto mb-3 text-green-500/50" />
                  <p className="text-sm">All content assessed</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recently Assessed */}
          <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-400" />
                Recently Assessed
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {assessedContent.slice(0, 5).map((content) => {
                const risk = riskAssessments.find((ra) => ra.contentId === content.id);
                return (
                  <div
                    key={content.id}
                    onClick={() => setSelectedContentId(content.id)}
                    className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                      selectedContentId === content.id
                        ? 'border-[#C7A84A] bg-[#C7A84A]/10'
                        : 'border-slate-700 bg-slate-800/50 hover:bg-slate-800'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-white line-clamp-1 flex-1">
                        {content.headline}
                      </p>
                      {risk && (
                        <span
                          className="text-sm font-bold ml-2"
                          style={{ color: getRiskColor(risk.scores.overallScore) }}
                        >
                          {risk.scores.overallScore}
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        </div>

        {/* Risk Assessment Detail */}
        <div className="lg:col-span-2">
          {selectedContent ? (
            <Card className="bg-[#0B1F3A]/50 border-slate-700/50 h-full">
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg text-white">Risk Assessment</CardTitle>
                    <p className="text-sm text-slate-400 mt-1">{selectedContent.headline}</p>
                  </div>
                  {!selectedRisk && (
                    <Button
                      onClick={() => handleAssessRisk(selectedContent.id)}
                      className="bg-[#C7A84A] hover:bg-[#d4b65c] text-[#0B1F3A]"
                    >
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Assess Risk
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {selectedRisk ? (
                  <div className="space-y-6">
                    {/* Overall Score */}
                    <div className="flex items-center justify-center p-6 bg-slate-800/50 rounded-lg">
                      <div className="text-center">
                        <p className="text-sm text-slate-400 mb-2">Overall Risk Score</p>
                        <div
                          className="text-6xl font-bold"
                          style={{ color: getRiskColor(selectedRisk.scores.overallScore) }}
                        >
                          {selectedRisk.scores.overallScore}
                        </div>
                        <Badge
                          className={`mt-2 ${getRiskBgColor(selectedRisk.scores.overallScore)}`}
                        >
                          {classifyRisk(selectedRisk.scores.overallScore)}
                        </Badge>
                        <p className="text-xs text-slate-500 mt-2">
                          {getRequiredApprovalLevel(selectedRisk.scores.overallScore)} approval required
                        </p>
                      </div>
                    </div>

                    {/* 4D Scores */}
                    <div className="grid grid-cols-2 gap-4">
                      <RiskDimensionCard
                        title="Legal Risk"
                        icon={Gavel}
                        score={selectedRisk.scores.legalRisk}
                        description="Risk of legal action or regulatory issues"
                      />
                      <RiskDimensionCard
                        title="Defamation Risk"
                        icon={Scale}
                        score={selectedRisk.scores.defamationRisk}
                        description="Risk of defamation or reputational harm"
                      />
                      <RiskDimensionCard
                        title="Platform Risk"
                        icon={Globe}
                        score={selectedRisk.scores.platformRisk}
                        description="Risk of platform policy violations"
                      />
                      <RiskDimensionCard
                        title="Political Sensitivity"
                        icon={ShieldAlert}
                        score={selectedRisk.scores.politicalSensitivity}
                        description="Political and geopolitical sensitivity"
                      />
                    </div>

                    {/* Risk Factors */}
                    <div>
                      <h4 className="text-sm font-medium text-white mb-3">Detected Risk Factors</h4>
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(selectedRisk.factors)
                          .filter(([_, value]) => value)
                          .map(([key]) => (
                            <Badge
                              key={key}
                              variant="outline"
                              className="text-xs border-amber-500/50 text-amber-400 capitalize"
                            >
                              {key.replace(/([A-Z])/g, ' $1').trim()}
                            </Badge>
                          ))}
                      </div>
                    </div>

                    {/* Mitigation Suggestions */}
                    <div>
                      <h4 className="text-sm font-medium text-white mb-3">Mitigation Suggestions</h4>
                      <ul className="space-y-2">
                        {getRiskMitigationSuggestions(selectedRisk.factors).map((suggestion, i) => (
                          <li
                            key={i}
                            className="flex items-start gap-2 text-sm text-slate-300"
                          >
                            <Info className="w-4 h-4 text-[#C7A84A] flex-shrink-0 mt-0.5" />
                            {suggestion}
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Safe Mode Status */}
                    {selectedRisk.safeModeBlocked && (
                      <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                        <div className="flex items-center gap-2 text-red-400">
                          <XCircle className="w-5 h-5" />
                          <span className="font-medium">Safe Mode Blocked</span>
                        </div>
                        <p className="text-sm text-red-400/80 mt-1">
                          This content cannot be published while Safe Mode is enabled.
                        </p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-12 text-slate-500">
                    <ShieldAlert className="w-16 h-16 mx-auto mb-4 text-slate-600" />
                    <p className="text-lg">No risk assessment yet</p>
                    <p className="text-sm">Click "Assess Risk" to analyze this content</p>
                  </div>
                )}
              </CardContent>
            </Card>
          ) : (
            <Card className="bg-[#0B1F3A]/50 border-slate-700/50 h-full flex items-center justify-center">
              <div className="text-center py-12 text-slate-500">
                <FileText className="w-16 h-16 mx-auto mb-4 text-slate-600" />
                <p className="text-lg">Select content to assess</p>
                <p className="text-sm">Choose from pending or recently assessed content</p>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

// Risk Dimension Card Component
function RiskDimensionCard({
  title,
  icon: Icon,
  score,
  description,
}: {
  title: string;
  icon: React.ElementType;
  score: number;
  description: string;
}) {
  return (
    <div className="p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Icon className="w-4 h-4 text-slate-400" />
          <span className="text-sm font-medium text-white">{title}</span>
        </div>
        <span
          className="text-lg font-bold"
          style={{ color: getRiskColor(score) }}
        >
          {score}
        </span>
      </div>
      <Progress value={score} className="h-2 mb-2" />
      <p className="text-xs text-slate-500">{description}</p>
    </div>
  );
}
