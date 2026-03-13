import { useState, useEffect } from 'react';
import { useAppStore } from '@/store';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Target, UserSquare, Globe, Mail, MessageSquare, Youtube } from 'lucide-react';
import type { Profile } from '@/types';

interface ProfileDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  profile?: Profile;
}

export function ProfileDialog({ open, onOpenChange, profile }: ProfileDialogProps) {
  const { createProfile, updateProfile } = useAppStore();
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    voiceEngine: 'edge-tts',
    voiceId: '',
    platformConfigs: {
      telegram: { bot_token: '', chat_id: '' },
      youtube: { oauth_token: '' }
    }
  });

  useEffect(() => {
    if (profile) {
      setFormData({
        name: profile.name,
        description: profile.description || '',
        voiceEngine: profile.voiceEngine || 'edge-tts',
        voiceId: profile.voiceId || '',
        platformConfigs: {
          telegram: { 
            bot_token: profile.platformConfigs?.telegram?.bot_token || '', 
            chat_id: profile.platformConfigs?.telegram?.chat_id || '' 
          },
          youtube: { 
            oauth_token: profile.platformConfigs?.youtube?.oauth_token || '' 
          }
        }
      });
    } else {
      setFormData({
        name: '',
        description: '',
        voiceEngine: 'edge-tts',
        voiceId: '',
        platformConfigs: {
          telegram: { bot_token: '', chat_id: '' },
          youtube: { oauth_token: '' }
        }
      });
    }
  }, [profile, open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      if (profile) {
        await updateProfile(profile.id, formData);
      } else {
        await createProfile(formData as any);
      }
      onOpenChange(false);
    } catch (error) {
      console.error('Failed to save profile:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-[#0B1F3A] border-slate-700 text-white max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <UserSquare className="w-5 h-5 text-[#C7A84A]" />
            {profile ? 'Edit Persona' : 'Create New Persona'}
          </DialogTitle>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-6 py-4">
          <Tabs defaultValue="basic" className="w-full">
            <TabsList className="bg-slate-900 border-slate-800 mb-4">
              <TabsTrigger value="basic">Basic Identity</TabsTrigger>
              <TabsTrigger value="voice">Voice & Style</TabsTrigger>
              <TabsTrigger value="platforms">Distribution Creds</TabsTrigger>
            </TabsList>

            <TabsContent value="basic" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Persona Name</Label>
                <Input 
                  id="name" 
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g. Global Strategic Analyst"
                  className="bg-slate-800 border-slate-700"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Mission Description</Label>
                <Textarea 
                  id="description" 
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Describe this persona's voice and objectives..."
                  className="bg-slate-800 border-slate-700 h-24"
                />
              </div>
            </TabsContent>

            <TabsContent value="voice" className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Voice Engine</Label>
                  <Select 
                    value={formData.voiceEngine}
                    onValueChange={(val) => setFormData({ ...formData, voiceEngine: val })}
                  >
                    <SelectTrigger className="bg-slate-800 border-slate-700 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-800 border-slate-700">
                      <SelectItem value="edge-tts">Edge-TTS (Free)</SelectItem>
                      <SelectItem value="elevenlabs">ElevenLabs (Premium)</SelectItem>
                      <SelectItem value="gtts">Google TTS (Fallback)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Voice ID / Model</Label>
                  <Input 
                    value={formData.voiceId}
                    onChange={(e) => setFormData({ ...formData, voiceId: e.target.value })}
                    placeholder="e.g. en-US-ChristopherNeural"
                    className="bg-slate-800 border-slate-700"
                  />
                </div>
              </div>
            </TabsContent>

            <TabsContent value="platforms" className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center gap-2 pb-2 border-b border-slate-800">
                  <MessageSquare className="w-4 h-4 text-blue-400" />
                  <span className="text-sm font-semibold">Telegram Configuration</span>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-xs">Bot Token</Label>
                    <Input 
                      type="password"
                      value={formData.platformConfigs.telegram.bot_token}
                      onChange={(e) => setFormData({ 
                        ...formData, 
                        platformConfigs: { 
                          ...formData.platformConfigs, 
                          telegram: { ...formData.platformConfigs.telegram, bot_token: e.target.value } 
                        } 
                      })}
                      className="bg-slate-800 border-slate-700 h-8"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs">Chat ID</Label>
                    <Input 
                      value={formData.platformConfigs.telegram.chat_id}
                      onChange={(e) => setFormData({ 
                        ...formData, 
                        platformConfigs: { 
                          ...formData.platformConfigs, 
                          telegram: { ...formData.platformConfigs.telegram, chat_id: e.target.value } 
                        } 
                      })}
                      className="bg-slate-800 border-slate-700 h-8"
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center gap-2 pb-2 border-b border-slate-800">
                  <Youtube className="w-4 h-4 text-red-500" />
                  <span className="text-sm font-semibold">YouTube Configuration</span>
                </div>
                <div className="space-y-2">
                  <Label className="text-xs">OAuth Token (JSON)</Label>
                  <Textarea 
                    value={formData.platformConfigs.youtube.oauth_token}
                    onChange={(e) => setFormData({ 
                      ...formData, 
                      platformConfigs: { 
                        ...formData.platformConfigs, 
                        youtube: { ...formData.platformConfigs.youtube, oauth_token: e.target.value } 
                      } 
                    })}
                    placeholder='{"token": "...", "refresh_token": "..."}'
                    className="bg-slate-800 border-slate-700 text-xs font-mono h-20"
                  />
                </div>
              </div>
            </TabsContent>
          </Tabs>

          <DialogFooter className="mt-8">
            <Button 
              type="button" 
              variant="ghost" 
              onClick={() => onOpenChange(false)}
              className="text-slate-400 hover:text-white"
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={isSubmitting}
              className="bg-[#C7A84A] hover:bg-[#d4b65c] text-slate-900 font-bold px-8"
            >
              {isSubmitting ? 'Saving...' : (profile ? 'Update Persona' : 'Create Persona')}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
