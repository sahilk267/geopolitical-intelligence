// ============================================
// CONTENT WORKFLOW SECTION
// Editorial Pipeline Management
// ============================================

import { useState } from 'react';
import { useAppStore } from '@/store';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  FileText,
  ArrowRight,
  Clock,
  User,
  Plus,
  Search,
  Filter,
  MoreVertical,
} from 'lucide-react';
import type { ContentItem, WorkflowStage } from '@/types';

const workflowStages: { id: WorkflowStage; label: string; color: string }[] = [
  { id: 'ingestion', label: 'Ingestion', color: 'bg-slate-500' },
  { id: 'preliminary_screening', label: 'Screening', color: 'bg-blue-500' },
  { id: 'research_layering', label: 'Research', color: 'bg-indigo-500' },
  { id: 'risk_scoring', label: 'Risk Scoring', color: 'bg-amber-500' },
  { id: 'script_drafting', label: 'Script Draft', color: 'bg-purple-500' },
  { id: 'editorial_review', label: 'Editorial Review', color: 'bg-pink-500' },
  { id: 'final_approval', label: 'Final Approval', color: 'bg-orange-500' },
  { id: 'archive_publish', label: 'Published', color: 'bg-green-500' },
];

const priorityColors = ['bg-slate-500', 'bg-blue-500', 'bg-amber-500', 'bg-red-500'];

export function ContentWorkflow() {
  const { contents, addContent, moveToStage } = useAppStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStage, setSelectedStage] = useState<WorkflowStage | 'all'>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  const filteredContents = contents.filter((content) => {
    const matchesSearch =
      content.headline.toLowerCase().includes(searchQuery.toLowerCase()) ||
      content.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
      content.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesStage = selectedStage === 'all' || content.currentStage === selectedStage;
    return matchesSearch && matchesStage;
  });

  const getStageCount = (stage: WorkflowStage) =>
    contents.filter((c) => c.currentStage === stage).length;

  const handleCreateContent = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    
    const newContent: ContentItem = {
      id: `content-${Date.now()}`,
      headline: formData.get('headline') as string,
      summary: formData.get('summary') as string,
      currentStage: 'ingestion',
      layers: ['factual_reporting'],
      sources: [],
      priority: parseInt(formData.get('priority') as string) as 0 | 1 | 2 | 3,
      assignedTo: undefined,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      status: 'draft',
      tags: (formData.get('tags') as string).split(',').map((t) => t.trim()).filter(Boolean),
      region: formData.get('region') as string,
      topic: formData.get('topic') as string,
    };

    addContent(newContent);
    setIsCreateDialogOpen(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Content Workflow</h1>
          <p className="text-slate-400">Manage editorial pipeline from ingestion to publication</p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-[#C7A84A] hover:bg-[#d4b65c] text-[#0B1F3A] font-medium">
              <Plus className="w-4 h-4 mr-2" />
              New Content
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-[#0B1F3A] border-slate-700 max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="text-white">Create New Content</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreateContent} className="space-y-4">
              <div>
                <Label htmlFor="headline" className="text-slate-300">Headline</Label>
                <Input
                  id="headline"
                  name="headline"
                  placeholder="Enter content headline"
                  className="bg-slate-800 border-slate-600 text-white"
                  required
                />
              </div>
              <div>
                <Label htmlFor="summary" className="text-slate-300">Summary</Label>
                <Textarea
                  id="summary"
                  name="summary"
                  placeholder="Brief summary of the content"
                  className="bg-slate-800 border-slate-600 text-white"
                  rows={3}
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="region" className="text-slate-300">Region</Label>
                  <Select name="region" defaultValue="Middle East">
                    <SelectTrigger className="bg-slate-800 border-slate-600 text-white">
                      <SelectValue placeholder="Select region" />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-800 border-slate-700">
                      <SelectItem value="Middle East">Middle East</SelectItem>
                      <SelectItem value="South Asia">South Asia</SelectItem>
                      <SelectItem value="Europe">Europe</SelectItem>
                      <SelectItem value="Asia-Pacific">Asia-Pacific</SelectItem>
                      <SelectItem value="Africa">Africa</SelectItem>
                      <SelectItem value="Americas">Americas</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="topic" className="text-slate-300">Topic</Label>
                  <Select name="topic" defaultValue="Strategic Analysis">
                    <SelectTrigger className="bg-slate-800 border-slate-600 text-white">
                      <SelectValue placeholder="Select topic" />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-800 border-slate-700">
                      <SelectItem value="Strategic Analysis">Strategic Analysis</SelectItem>
                      <SelectItem value="Energy Security">Energy Security</SelectItem>
                      <SelectItem value="Conflict Analysis">Conflict Analysis</SelectItem>
                      <SelectItem value="Diplomatic Relations">Diplomatic Relations</SelectItem>
                      <SelectItem value="Economic Policy">Economic Policy</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="priority" className="text-slate-300">Priority</Label>
                  <Select name="priority" defaultValue="1">
                    <SelectTrigger className="bg-slate-800 border-slate-600 text-white">
                      <SelectValue placeholder="Select priority" />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-800 border-slate-700">
                      <SelectItem value="0">Normal</SelectItem>
                      <SelectItem value="1">Important</SelectItem>
                      <SelectItem value="2">Breaking</SelectItem>
                      <SelectItem value="3">Emergency</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="tags" className="text-slate-300">Tags (comma-separated)</Label>
                  <Input
                    id="tags"
                    name="tags"
                    placeholder="iran, israel, oil"
                    className="bg-slate-800 border-slate-600 text-white"
                  />
                </div>
              </div>
              <Button type="submit" className="w-full bg-[#C7A84A] hover:bg-[#d4b65c] text-[#0B1F3A]">
                Create Content
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Pipeline Overview */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        <button
          onClick={() => setSelectedStage('all')}
          className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
            selectedStage === 'all'
              ? 'bg-[#C7A84A] text-[#0B1F3A]'
              : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
          }`}
        >
          All ({contents.length})
        </button>
        {workflowStages.map((stage) => (
          <button
            key={stage.id}
            onClick={() => setSelectedStage(stage.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors flex items-center gap-2 ${
              selectedStage === stage.id
                ? 'bg-[#C7A84A] text-[#0B1F3A]'
                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
            }`}
          >
            <span className={`w-2 h-2 rounded-full ${stage.color}`} />
            {stage.label} ({getStageCount(stage.id)})
          </button>
        ))}
      </div>

      {/* Search and Filter */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input
            type="text"
            placeholder="Search content..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-slate-800 border-slate-700 text-white"
          />
        </div>
        <Button variant="outline" className="border-slate-600 text-slate-300">
          <Filter className="w-4 h-4 mr-2" />
          Filter
        </Button>
      </div>

      {/* Content List */}
      <div className="space-y-3">
        {filteredContents.length > 0 ? (
          filteredContents.map((content) => (
            <ContentCard
              key={content.id}
              content={content}
              onMoveStage={(stage) => moveToStage(content.id, stage)}
            />
          ))
        ) : (
          <div className="text-center py-12 text-slate-500">
            <FileText className="w-16 h-16 mx-auto mb-4 text-slate-600" />
            <p className="text-lg">No content found</p>
            <p className="text-sm">Create new content or adjust your filters</p>
          </div>
        )}
      </div>
    </div>
  );
}

// Content Card Component
function ContentCard({
  content,
  onMoveStage,
}: {
  content: ContentItem;
  onMoveStage: (stage: WorkflowStage) => void;
}) {
  const currentStageIndex = workflowStages.findIndex((s) => s.id === content.currentStage);
  const nextStage = workflowStages[currentStageIndex + 1];

  return (
    <Card className="bg-[#0B1F3A]/50 border-slate-700/50 hover:border-slate-600 transition-colors">
      <CardContent className="p-4">
        <div className="flex items-start gap-4">
          {/* Priority Indicator */}
          <div
            className={`w-1 h-full min-h-[60px] rounded-full ${priorityColors[content.priority]}`}
          />

          <div className="flex-1 min-w-0">
            {/* Header */}
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3 className="text-lg font-medium text-white">{content.headline}</h3>
                <p className="text-sm text-slate-400 mt-1 line-clamp-2">{content.summary}</p>
              </div>
              <Button variant="ghost" size="icon" className="text-slate-400">
                <MoreVertical className="w-4 h-4" />
              </Button>
            </div>

            {/* Meta Info */}
            <div className="flex items-center gap-4 mt-3 flex-wrap">
              <Badge
                variant="outline"
                className="text-xs border-slate-600 text-slate-400"
              >
                {workflowStages.find((s) => s.id === content.currentStage)?.label}
              </Badge>
              <Badge variant="outline" className="text-xs border-slate-600 text-slate-400">
                {content.region}
              </Badge>
              <div className="flex items-center gap-1 text-xs text-slate-500">
                <Clock className="w-3 h-3" />
                {new Date(content.createdAt).toLocaleDateString()}
              </div>
              {content.assignedTo && (
                <div className="flex items-center gap-1 text-xs text-slate-500">
                  <User className="w-3 h-3" />
                  Assigned
                </div>
              )}
            </div>

            {/* Tags */}
            <div className="flex items-center gap-2 mt-3">
              {content.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-2 py-0.5 text-[10px] bg-slate-800 text-slate-400 rounded"
                >
                  {tag}
                </span>
              ))}
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between mt-4 pt-3 border-t border-slate-700/50">
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500">Layers:</span>
                {content.layers.map((layer) => (
                  <span
                    key={layer}
                    className="px-2 py-0.5 text-[10px] bg-slate-800 text-slate-400 rounded capitalize"
                  >
                    {layer.replace('_', ' ')}
                  </span>
                ))}
              </div>
              <div className="flex items-center gap-2">
                {nextStage && content.currentStage !== 'archive_publish' && (
                  <Button
                    size="sm"
                    onClick={() => onMoveStage(nextStage.id)}
                    className="bg-[#C7A84A] hover:bg-[#d4b65c] text-[#0B1F3A]"
                  >
                    Move to {nextStage.label}
                    <ArrowRight className="w-3 h-3 ml-1" />
                  </Button>
                )}
                <Button
                  size="sm"
                  variant="outline"
                  className="border-slate-600 text-slate-300"
                >
                  View Details
                </Button>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
