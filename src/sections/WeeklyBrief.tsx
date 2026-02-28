// ============================================
// WEEKLY BRIEF SECTION
// Intelligence Brief Generator & Manager
// ============================================

import { useState } from 'react';
import { useAppStore } from '@/store';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { generateWeeklyBrief, renderBriefToHTML } from '@/lib/briefGenerator';
import { getERIColor, classifyERI } from '@/lib/eriEngine';
import {
  Newspaper,
  Download,
  Eye,
  Plus,
  FileText,
  Calendar,
  TrendingUp,
  Users,
  Globe,
  Zap,
} from 'lucide-react';

export function WeeklyBriefSection() {
  const { weeklyBriefs, currentERI, addWeeklyBrief } = useAppStore();
  const [previewBriefId, setPreviewBriefId] = useState<string | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  const previewBrief = previewBriefId
    ? weeklyBriefs.find((b) => b.id === previewBriefId)
    : null;

  const handleCreateBrief = () => {
    if (!currentERI) return;

    const newBrief = generateWeeklyBrief({
      weekNumber: currentERI.weekNumber,
      year: currentERI.year,
      eriAssessment: currentERI,
    });

    addWeeklyBrief(newBrief);
    setIsCreateDialogOpen(false);
  };

  const handleDownloadPDF = (briefId: string) => {
    const brief = weeklyBriefs.find((b) => b.id === briefId);
    if (brief) {
      const html = renderBriefToHTML(brief);
      const printWindow = window.open('', '_blank');
      if (printWindow) {
        printWindow.document.write(html);
        printWindow.document.close();
        printWindow.print();
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Weekly Intelligence Briefs</h1>
          <p className="text-slate-400">Generate and manage premium intelligence reports</p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-[#C7A84A] hover:bg-[#d4b65c] text-[#0B1F3A] font-medium">
              <Plus className="w-4 h-4 mr-2" />
              Generate Brief
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-[#0B1F3A] border-slate-700">
            <DialogHeader>
              <DialogTitle className="text-white">Generate Weekly Brief</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              {currentERI ? (
                <>
                  <div className="p-4 bg-slate-800/50 rounded-lg">
                    <p className="text-sm text-slate-400">Current ERI</p>
                    <div className="flex items-center gap-3 mt-2">
                      <span
                        className="text-3xl font-bold"
                        style={{ color: getERIColor(currentERI.overallScore) }}
                      >
                        {currentERI.overallScore}
                      </span>
                      <Badge
                        variant="outline"
                        style={{
                          borderColor: getERIColor(currentERI.overallScore),
                          color: getERIColor(currentERI.overallScore),
                        }}
                      >
                        {classifyERI(currentERI.overallScore)}
                      </Badge>
                    </div>
                  </div>
                  <Button
                    onClick={handleCreateBrief}
                    className="w-full bg-[#C7A84A] hover:bg-[#d4b65c] text-[#0B1F3A]"
                  >
                    Generate Brief for Week {currentERI.weekNumber}
                  </Button>
                </>
              ) : (
                <div className="text-center py-8 text-slate-500">
                  <TrendingUp className="w-12 h-12 mx-auto mb-3 text-slate-600" />
                  <p>No ERI assessment available</p>
                  <p className="text-sm">Create an ERI assessment first</p>
                </div>
              )}
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Briefs List */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Brief Cards */}
        <div className="lg:col-span-2 space-y-4">
          {weeklyBriefs.length > 0 ? (
            weeklyBriefs.map((brief) => (
              <Card
                key={brief.id}
                className={`bg-[#0B1F3A]/50 border-slate-700/50 cursor-pointer transition-colors ${
                  previewBriefId === brief.id ? 'border-[#C7A84A]' : 'hover:border-slate-600'
                }`}
                onClick={() => setPreviewBriefId(brief.id)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <h3 className="text-lg font-medium text-white">{brief.title}</h3>
                        <Badge variant="outline" className="text-[10px] border-slate-600 text-slate-400">
                          v{brief.version}
                        </Badge>
                      </div>
                      <p className="text-sm text-slate-400 mt-1">{brief.subtitle}</p>
                      <div className="flex items-center gap-4 mt-3">
                        <div className="flex items-center gap-1 text-xs text-slate-500">
                          <Calendar className="w-3 h-3" />
                          Week {brief.weekNumber}, {brief.year}
                        </div>
                        <div className="flex items-center gap-1 text-xs text-slate-500">
                          <TrendingUp className="w-3 h-3" />
                          ERI: {brief.eriScore}
                        </div>
                        <div
                          className="px-2 py-0.5 text-xs rounded"
                          style={{
                            backgroundColor: `${getERIColor(brief.eriScore)}20`,
                            color: getERIColor(brief.eriScore),
                          }}
                        >
                          {classifyERI(brief.eriScore)}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDownloadPDF(brief.id);
                        }}
                        className="text-slate-400 hover:text-white"
                      >
                        <Download className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
              <CardContent className="p-12 text-center">
                <Newspaper className="w-16 h-16 mx-auto mb-4 text-slate-600" />
                <p className="text-lg text-slate-400">No briefs generated yet</p>
                <p className="text-sm text-slate-500 mt-1">
                  Generate your first weekly intelligence brief
                </p>
                <Button
                  onClick={() => setIsCreateDialogOpen(true)}
                  className="mt-4 bg-[#C7A84A] hover:bg-[#d4b65c] text-[#0B1F3A]"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Generate Brief
                </Button>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Preview Panel */}
        <div className="lg:col-span-1">
          <Card className="bg-[#0B1F3A]/50 border-slate-700/50 sticky top-6">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <Eye className="w-5 h-5 text-[#C7A84A]" />
                Brief Preview
              </CardTitle>
            </CardHeader>
            <CardContent>
              {previewBrief ? (
                <div className="space-y-4">
                  <div className="text-center p-4 bg-slate-800/50 rounded-lg">
                    <p className="text-xs text-slate-500">{previewBrief.title}</p>
                    <p className="text-2xl font-bold text-white mt-1">
                      Week {previewBrief.weekNumber}
                    </p>
                    <div
                      className="inline-flex items-center gap-2 px-3 py-1 rounded-full mt-2"
                      style={{
                        backgroundColor: `${getERIColor(previewBrief.eriScore)}20`,
                      }}
                    >
                      <span
                        className="text-lg font-bold"
                        style={{ color: getERIColor(previewBrief.eriScore) }}
                      >
                        ERI: {previewBrief.eriScore}
                      </span>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center gap-2 text-sm">
                      <FileText className="w-4 h-4 text-slate-400" />
                      <span className="text-slate-300">Executive Summary</span>
                    </div>
                    <p className="text-xs text-slate-400 line-clamp-3">
                      {previewBrief.executiveSummary.whatChanged}
                    </p>

                    <div className="flex items-center gap-2 text-sm">
                      <Globe className="w-4 h-4 text-slate-400" />
                      <span className="text-slate-300">
                        {previewBrief.keyDevelopments.length} Key Developments
                      </span>
                    </div>

                    <div className="flex items-center gap-2 text-sm">
                      <Users className="w-4 h-4 text-slate-400" />
                      <span className="text-slate-300">
                        {previewBrief.stakeholderPositions.length} Stakeholders
                      </span>
                    </div>

                    <div className="flex items-center gap-2 text-sm">
                      <Zap className="w-4 h-4 text-slate-400" />
                      <span className="text-slate-300">
                        {previewBrief.indicatorsToWatch.length} Indicators
                      </span>
                    </div>
                  </div>

                  <Button
                    onClick={() => handleDownloadPDF(previewBrief.id)}
                    className="w-full bg-[#C7A84A] hover:bg-[#d4b65c] text-[#0B1F3A]"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download PDF
                  </Button>
                </div>
              ) : (
                <div className="text-center py-8 text-slate-500">
                  <Eye className="w-12 h-12 mx-auto mb-3 text-slate-600" />
                  <p className="text-sm">Select a brief to preview</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
