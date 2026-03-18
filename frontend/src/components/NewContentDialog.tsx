import React, { useState } from 'react';
import { useAppStore } from '@/store';
import { api } from '@/lib/api';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import type { ContentItem } from '@/types';

export function NewContentDialog() {
    const { createDialogOpen, setCreateDialogOpen, addContent } = useAppStore();
    const [isGenerating, setIsGenerating] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Form State
    const [formData, setFormData] = useState({
        url: '',
        headline: '',
        summary: '',
        region: 'Middle East',
        topic: 'Strategic Analysis',
        priority: '1',
        tags: '',
    });

    const handleCreateContent = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setIsSubmitting(true);

        try {
            const newContent: ContentItem = {
                id: `content-${Date.now()}`,
                headline: formData.headline,
                summary: formData.summary,
                currentStage: 'ingestion',
                layers: ['factual_reporting'],
                sources: formData.url ? [{
                    id: `source-${Date.now()}`,
                    title: 'Source',
                    url: formData.url,
                    tier: 1,
                    timestamp: new Date().toISOString(),
                    credibilityScore: 100
                }] : [],
                priority: parseInt(formData.priority) as 0 | 1 | 2 | 3,
                assignedTo: undefined,
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString(),
                status: 'draft',
                tags: formData.tags.split(',').map((t: string) => t.trim()).filter(Boolean),
                region: formData.region,
                topic: formData.topic,
            };

            await addContent(newContent);
            setCreateDialogOpen(false);
            setFormData({
                url: '',
                headline: '',
                summary: '',
                region: 'Middle East',
                topic: 'Strategic Analysis',
                priority: '1',
                tags: '',
            });
        } catch (error) {
            console.error('Failed to create content:', error);
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleAiGenerate = async () => {
        if (!formData.url) return;

        setIsGenerating(true);
        try {
            const data = await api.generateFromUrl(
                formData.url,
                formData.topic,
                formData.region
            ) as { headline: string; summary: string };

            setFormData((prev: any) => ({
                ...prev,
                headline: data.headline || prev.headline,
                summary: data.summary || prev.summary,
            }));
        } catch (error) {
            console.error('AI generation error:', error);
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogContent className="bg-[#0B1F3A] border-slate-700 max-w-2xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle className="text-white">Create New Content</DialogTitle>
                    <DialogDescription className="text-slate-400">
                        Draft a briefing by summarizing a source URL or generating content directly with AI assistance.
                    </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleCreateContent} className="space-y-4">
                    <div>
                        <Label htmlFor="url" className="text-slate-300">Source URL (Optional for AI)</Label>
                        <div className="flex gap-2">
                            <Input
                                id="url"
                                name="url"
                                value={formData.url}
                                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, url: e.target.value })}
                                placeholder="https://news-source.com/article"
                                className="bg-slate-800 border-slate-600 text-white flex-1"
                            />
                            <Button
                                type="button"
                                variant="secondary"
                                className="bg-indigo-600 hover:bg-indigo-700 text-white shrink-0"
                                onClick={handleAiGenerate}
                                disabled={isGenerating || !formData.url}
                            >
                                {isGenerating ? 'Analyzing...' : 'AI Generate'}
                            </Button>
                        </div>
                    </div>
                    <div>
                        <Label htmlFor="headline" className="text-slate-300">Headline</Label>
                        <Input
                            id="headline"
                            name="headline"
                            value={formData.headline}
                            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, headline: e.target.value })}
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
                            value={formData.summary}
                            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setFormData({ ...formData, summary: e.target.value })}
                            placeholder="Brief summary of the content"
                            className="bg-slate-800 border-slate-600 text-white"
                            rows={3}
                            required
                        />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <Label htmlFor="region" className="text-slate-300">Region</Label>
                            <Select
                                value={formData.region}
                                onValueChange={(val: string) => setFormData({ ...formData, region: val })}
                            >
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
                                    <SelectItem value="Global">Global</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <div>
                            <Label htmlFor="topic" className="text-slate-300">Topic</Label>
                            <Select
                                value={formData.topic}
                                onValueChange={(val: string) => setFormData({ ...formData, topic: val })}
                            >
                                <SelectTrigger className="bg-slate-800 border-slate-600 text-white">
                                    <SelectValue placeholder="Select topic" />
                                </SelectTrigger>
                                <SelectContent className="bg-slate-800 border-slate-700">
                                    <SelectItem value="Strategic Analysis">Strategic Analysis</SelectItem>
                                    <SelectItem value="Energy Security">Energy Security</SelectItem>
                                    <SelectItem value="Cyber Warfare">Cyber Warfare</SelectItem>
                                    <SelectItem value="Border Disputes">Border Disputes</SelectItem>
                                    <SelectItem value="Conflict Analysis">Conflict Analysis</SelectItem>
                                    <SelectItem value="Diplomatic Relations">Diplomatic Relations</SelectItem>
                                    <SelectItem value="Economic Policy">Economic Policy</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <Label htmlFor="priority" className="text-slate-300">Priority (0-3)</Label>
                            <Select
                                value={formData.priority}
                                onValueChange={(val: string) => setFormData({ ...formData, priority: val })}
                            >
                                <SelectTrigger className="bg-slate-800 border-slate-600 text-white">
                                    <SelectValue placeholder="Select priority" />
                                </SelectTrigger>
                                <SelectContent className="bg-slate-800 border-slate-700">
                                    <SelectItem value="0">0 - Routine</SelectItem>
                                    <SelectItem value="1">1 - Standard</SelectItem>
                                    <SelectItem value="2">2 - High</SelectItem>
                                    <SelectItem value="3">3 - Critical</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <div>
                            <Label htmlFor="tags" className="text-slate-300">Tags (Comma separated)</Label>
                            <Input
                                id="tags"
                                name="tags"
                                value={formData.tags}
                                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, tags: e.target.value })}
                                placeholder="russia, energy, sanctions"
                                className="bg-slate-800 border-slate-600 text-white"
                            />
                        </div>
                    </div>
                    <Button
                        type="submit"
                        className="w-full bg-[#C7A84A] hover:bg-[#d4b65c] text-[#0B1F3A]"
                        disabled={isSubmitting}
                    >
                        {isSubmitting ? 'Creating...' : 'Create Content'}
                    </Button>
                </form>
            </DialogContent>
        </Dialog>
    );
}
