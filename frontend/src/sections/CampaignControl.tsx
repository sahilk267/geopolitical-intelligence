import { useAppStore } from '@/store';
import { Target, Play, Power, Plus, Calendar, Clock, BarChart3, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export function CampaignControl() {
  const { campaigns, profiles, triggerCampaign, deleteCampaign, updateCampaign } = useAppStore();

  const getProfileName = (profileId: string) => {
    return profiles.find(p => p.id === profileId)?.name || 'Unknown Profile';
  };

  const toggleCampaign = (id: string, currentStatus: boolean) => {
    updateCampaign(id, { is_active: !currentStatus });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Target className="w-6 h-6 text-[#C7A84A]" />
            Campaign Mission Control
          </h2>
          <p className="text-slate-400">Autonomous content blueprints and scheduling</p>
        </div>
        <Button className="bg-[#C7A84A] hover:bg-[#d4b65c] text-white gap-2">
          <Plus className="w-4 h-4" /> New Blueprint
        </Button>
      </div>

      <div className="space-y-4">
        {campaigns.map((campaign) => (
          <div key={campaign.id} className="bg-[#0B1F3A] border border-slate-700/50 rounded-xl overflow-hidden hover:border-[#C7A84A]/20 transition-all">
            <div className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-start gap-4">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${campaign.isActive ? 'bg-[#C7A84A]/20 text-[#C7A84A]' : 'bg-slate-700/30 text-slate-500'}`}>
                  <Target className="w-6 h-6" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-lg font-semibold text-white">{campaign.name}</h3>
                    <Badge variant={campaign.isActive ? "default" : "outline"} className={campaign.isActive ? "bg-green-500/10 text-green-400 border-green-500/20" : "text-slate-500 border-slate-700"}>
                      {campaign.isActive ? 'Active' : 'Paused'}
                    </Badge>
                  </div>
                  <p className="text-sm text-slate-400">{campaign.description || 'No description'}</p>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-3">
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="border-slate-700 text-slate-300 hover:bg-slate-800 gap-2"
                  onClick={() => triggerCampaign(campaign.id)}
                >
                  <Play className="w-4 h-4" /> Run Now
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className={`gap-2 ${campaign.isActive ? 'border-amber-500/30 text-amber-400 hover:bg-amber-500/10' : 'border-green-500/30 text-green-400 hover:bg-green-500/10'}`}
                  onClick={() => toggleCampaign(campaign.id, campaign.isActive)}
                >
                  <Power className="w-4 h-4" /> {campaign.isActive ? 'Pause' : 'Activate'}
                </Button>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="text-slate-500 hover:text-red-400 h-9 w-9"
                  onClick={() => deleteCampaign(campaign.id)}
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>

            <div className="bg-[#0a1628]/50 border-t border-slate-700/40 p-4 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="space-y-1">
                <div className="text-[10px] uppercase text-slate-500 font-bold flex items-center gap-1">
                  <Calendar className="w-3 h-3" /> Persona
                </div>
                <div className="text-sm text-slate-300 font-medium">
                  {getProfileName(campaign.profileId)}
                </div>
              </div>
              <div className="space-y-1">
                <div className="text-[10px] uppercase text-slate-500 font-bold flex items-center gap-1">
                  <BarChart3 className="w-3 h-3" /> Categories
                </div>
                <div className="flex flex-wrap gap-1">
                  {(campaign.categories || []).map((cat: string) => (
                    <span key={cat} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700/50">
                      {cat}
                    </span>
                  ))}
                </div>
              </div>
              <div className="space-y-1">
                <div className="text-[10px] uppercase text-slate-500 font-bold flex items-center gap-1">
                  <Clock className="w-3 h-3" /> Mission Schedule
                </div>
                <div className="text-sm text-slate-300 capitalize">
                  {campaign.scheduleType}
                </div>
              </div>
              <div className="space-y-1">
                <div className="text-[10px] uppercase text-slate-500 font-bold flex items-center gap-1">
                  <Calendar className="w-3 h-3" /> Last Successful
                </div>
                <div className="text-sm text-slate-300">
                  {campaign.lastRunAt ? new Date(campaign.lastRunAt).toLocaleString() : 'Never'}
                </div>
              </div>
            </div>
          </div>
        ))}

        {campaigns.length === 0 && (
          <div className="py-20 bg-[#0B1F3A]/30 border-2 border-dashed border-slate-700/50 rounded-2xl flex flex-col items-center justify-center text-center">
            <Target className="w-12 h-12 text-slate-600 mb-4" />
            <h3 className="text-lg font-medium text-slate-300">No Autonomous Missions</h3>
            <p className="text-slate-500 mt-1 max-w-xs">Create a mission blueprint to start your hands-free content generation.</p>
          </div>
        )}
      </div>
    </div>
  );
}
