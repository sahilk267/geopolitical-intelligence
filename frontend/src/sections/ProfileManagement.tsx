import { useState } from 'react';
import { useAppStore } from '@/store';
import { UserSquare, Plus, Edit2, Trash2, Globe } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ProfileDialog } from './ProfileDialog';
import type { Profile } from '@/types';

export function ProfileManagement() {
  const { profiles, deleteProfile } = useAppStore();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingProfile, setEditingProfile] = useState<Profile | undefined>();

  const handleCreate = () => {
    setEditingProfile(undefined);
    setDialogOpen(true);
  };

  const handleEdit = (profile: Profile) => {
    setEditingProfile(profile);
    setDialogOpen(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <UserSquare className="w-6 h-6 text-[#C7A84A]" />
            Persona Management
          </h2>
          <p className="text-slate-400">Configure distinct identities for your autonomous content network</p>
        </div>
        <Button 
          className="bg-[#C7A84A] hover:bg-[#d4b65c] text-white gap-2"
          onClick={handleCreate}
        >
          <Plus className="w-4 h-4" /> New Persona
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {profiles.map((profile) => (
          <div key={profile.id} className="bg-[#0B1F3A] border border-slate-700/50 rounded-xl p-5 hover:border-[#C7A84A]/30 transition-all group">
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 rounded-lg bg-[#0B1F3A] border border-slate-700 flex items-center justify-center text-[#C7A84A]">
                <Globe className="w-6 h-6" />
              </div>
              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="h-8 w-8 text-slate-400 hover:text-white"
                  onClick={() => handleEdit(profile)}
                >
                  <Edit2 className="w-4 h-4" />
                </Button>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="h-8 w-8 text-slate-400 hover:text-red-400"
                  onClick={() => deleteProfile(profile.id)}
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
            
            <h3 className="text-lg font-semibold text-white mb-1">{profile.name}</h3>
            <p className="text-sm text-slate-400 mb-4 line-clamp-2">{profile.description || 'No description provided.'}</p>
            
            <div className="space-y-2 pt-4 border-t border-slate-700/50">
              <div className="flex justify-between text-xs">
                <span className="text-slate-500">Voice Engine:</span>
                <span className="text-slate-300 uppercase">{profile.voiceEngine || 'Edge-TTS'}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-slate-500">Video Style:</span>
                <span className="text-slate-300">{Object.keys(profile.videoStyle || {}).length > 0 ? 'Custom' : 'Standard'}</span>
              </div>
            </div>
          </div>
        ))}

        {profiles.length === 0 && (
          <div className="col-span-full py-20 bg-[#0B1F3A]/30 border-2 border-dashed border-slate-700/50 rounded-2xl flex flex-col items-center justify-center text-center">
            <UserSquare className="w-12 h-12 text-slate-600 mb-4" />
            <h3 className="text-lg font-medium text-slate-300">No Personas Found</h3>
            <p className="text-slate-500 mt-1 max-w-xs">Create your first persona to start generating branded autonomous content.</p>
          </div>
        )}
      </div>

      <ProfileDialog 
        open={dialogOpen} 
        onOpenChange={setDialogOpen} 
        profile={editingProfile} 
      />
    </div>
  );
}
