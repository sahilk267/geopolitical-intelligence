// ============================================
// EVIDENCE ARCHIVE SECTION
// Source Documentation & Evidence Management
// ============================================

import { useState } from 'react';
import { useAppStore } from '@/store';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Archive,
  Plus,
  Search,
  ExternalLink,
  Image,
  FileText,
  Video,
  Mic,
  Link2,
  Trash2,
  Calendar,
} from 'lucide-react';
import type { EvidenceItem, SourceTier } from '@/types';

const tierColors: Record<SourceTier, string> = {
  1: 'bg-green-500/20 text-green-400 border-green-500/30',
  2: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  3: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  4: 'bg-red-500/20 text-red-400 border-red-500/30',
};

const tierLabels: Record<SourceTier, string> = {
  1: 'Official',
  2: 'Established Media',
  3: 'Expert Analysis',
  4: 'Unverified',
};

const typeIcons = {
  screenshot: Image,
  document: FileText,
  video: Video,
  audio: Mic,
  link: Link2,
};

export function EvidenceArchive() {
  const { evidenceArchive, addEvidence, deleteEvidence, contents } = useAppStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);

  const filteredEvidence = evidenceArchive.filter((evidence) => {
    const matchesSearch =
      evidence.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      evidence.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesType = selectedType === 'all' || evidence.type === selectedType;
    return matchesSearch && matchesType;
  });

  const handleAddEvidence = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);

    const newEvidence: EvidenceItem = {
      id: `evidence-${Date.now()}`,
      contentId: (formData.get('contentId') as string) || '',
      type: formData.get('type') as EvidenceItem['type'],
      url: formData.get('url') as string,
      timestamp: formData.get('timestamp') as string,
      sourceTier: parseInt(formData.get('sourceTier') as string) as SourceTier,
      description: formData.get('description') as string,
      tags: (formData.get('tags') as string).split(',').map((t) => t.trim()).filter(Boolean),
      uploadedBy: 'Editor-in-Chief',
      uploadedAt: new Date().toISOString(),
    };

    addEvidence(newEvidence);
    setIsAddDialogOpen(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Evidence Archive</h1>
          <p className="text-slate-400">Source documentation and evidence management</p>
        </div>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-[#C7A84A] hover:bg-[#d4b65c] text-[#0B1F3A] font-medium">
              <Plus className="w-4 h-4 mr-2" />
              Add Evidence
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-[#0B1F3A] border-slate-700 max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="text-white">Add Evidence</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleAddEvidence} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="type" className="text-slate-300">Evidence Type</Label>
                  <select
                    id="type"
                    name="type"
                    className="w-full mt-1 px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white"
                    required
                  >
                    <option value="screenshot">Screenshot</option>
                    <option value="document">Document</option>
                    <option value="video">Video</option>
                    <option value="audio">Audio</option>
                    <option value="link">Link</option>
                  </select>
                </div>
                <div>
                  <Label htmlFor="sourceTier" className="text-slate-300">Source Tier</Label>
                  <select
                    id="sourceTier"
                    name="sourceTier"
                    className="w-full mt-1 px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white"
                    required
                  >
                    <option value="1">Tier 1 - Official</option>
                    <option value="2">Tier 2 - Established Media</option>
                    <option value="3">Tier 3 - Expert Analysis</option>
                    <option value="4">Tier 4 - Unverified</option>
                  </select>
                </div>
              </div>

              <div>
                <Label htmlFor="url" className="text-slate-300">URL / Source</Label>
                <Input
                  id="url"
                  name="url"
                  placeholder="https://example.com/source"
                  className="bg-slate-800 border-slate-600 text-white"
                  required
                />
              </div>

              <div>
                <Label htmlFor="contentId" className="text-slate-300">Related Content (Optional)</Label>
                <select
                  id="contentId"
                  name="contentId"
                  className="w-full mt-1 px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white"
                >
                  <option value="">None</option>
                  {contents.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.headline.slice(0, 60)}...
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <Label htmlFor="timestamp" className="text-slate-300">Original Timestamp</Label>
                <Input
                  id="timestamp"
                  name="timestamp"
                  type="datetime-local"
                  className="bg-slate-800 border-slate-600 text-white"
                  required
                />
              </div>

              <div>
                <Label htmlFor="description" className="text-slate-300">Description</Label>
                <textarea
                  id="description"
                  name="description"
                  rows={3}
                  className="w-full mt-1 px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white"
                  placeholder="Describe this evidence..."
                  required
                />
              </div>

              <div>
                <Label htmlFor="tags" className="text-slate-300">Tags (comma-separated)</Label>
                <Input
                  id="tags"
                  name="tags"
                  placeholder="iran, sanctions, treaty"
                  className="bg-slate-800 border-slate-600 text-white"
                />
              </div>

              <Button type="submit" className="w-full bg-[#C7A84A] hover:bg-[#d4b65c] text-[#0B1F3A]">
                Add Evidence
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {(['all', 'screenshot', 'document', 'video', 'link'] as const).map((type) => {
          const count =
            type === 'all'
              ? evidenceArchive.length
              : evidenceArchive.filter((e) => e.type === type).length;
          const Icon = type === 'all' ? Archive : typeIcons[type as keyof typeof typeIcons] || FileText;

          return (
            <button
              key={type}
              onClick={() => setSelectedType(type)}
              className={`p-4 rounded-lg border transition-colors ${
                selectedType === type
                  ? 'border-[#C7A84A] bg-[#C7A84A]/10'
                  : 'border-slate-700 bg-slate-800/50 hover:bg-slate-800'
              }`}
            >
              <Icon className="w-5 h-5 text-slate-400 mb-2" />
              <p className="text-2xl font-bold text-white">{count}</p>
              <p className="text-xs text-slate-400 capitalize">{type === 'all' ? 'Total' : type}</p>
            </button>
          );
        })}
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
        <Input
          type="text"
          placeholder="Search evidence by description or tags..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10 bg-slate-800 border-slate-700 text-white"
        />
      </div>

      {/* Evidence Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredEvidence.length > 0 ? (
          filteredEvidence.map((evidence) => {
            const Icon = typeIcons[evidence.type];
            return (
              <Card
                key={evidence.id}
                className="bg-[#0B1F3A]/50 border-slate-700/50 hover:border-slate-600 transition-colors"
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center">
                        <Icon className="w-5 h-5 text-slate-400" />
                      </div>
                      <div>
                        <Badge
                          variant="outline"
                          className={`text-[10px] ${tierColors[evidence.sourceTier]}`}
                        >
                          {tierLabels[evidence.sourceTier]}
                        </Badge>
                        <p className="text-xs text-slate-500 capitalize mt-1">{evidence.type}</p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => deleteEvidence(evidence.id)}
                      className="text-slate-400 hover:text-red-400"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>

                  <p className="text-sm text-slate-300 mt-3 line-clamp-2">{evidence.description}</p>

                  <div className="flex items-center gap-2 mt-3">
                    {evidence.tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-0.5 text-[10px] bg-slate-800 text-slate-400 rounded"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>

                  <div className="flex items-center justify-between mt-4 pt-3 border-t border-slate-700/50">
                    <div className="flex items-center gap-1 text-xs text-slate-500">
                      <Calendar className="w-3 h-3" />
                      {new Date(evidence.timestamp).toLocaleDateString()}
                    </div>
                    <a
                      href={evidence.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-xs text-[#C7A84A] hover:underline"
                    >
                      <ExternalLink className="w-3 h-3" />
                      View Source
                    </a>
                  </div>
                </CardContent>
              </Card>
            );
          })
        ) : (
          <div className="col-span-full text-center py-12 text-slate-500">
            <Archive className="w-16 h-16 mx-auto mb-4 text-slate-600" />
            <p className="text-lg">No evidence found</p>
            <p className="text-sm">Add evidence or adjust your search</p>
          </div>
        )}
      </div>
    </div>
  );
}
