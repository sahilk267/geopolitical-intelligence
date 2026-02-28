// ============================================
// SETTINGS SECTION
// System Configuration & Preferences
// ============================================

import { useAppStore } from '@/store';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Shield,
  Bell,
  Globe,
  Users,
  Save,
  RefreshCw,
  Database,
  Lock,
} from 'lucide-react';

export function Settings() {
  const { settings, updateSettings, safeModeEnabled, toggleSafeMode, riskThreshold, setRiskThreshold } = useAppStore();

  const handleSaveSettings = () => {
    // Settings are automatically saved via Zustand persist
    alert('Settings saved successfully!');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-slate-400">Configure system preferences and governance parameters</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Brand Settings */}
        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg text-white flex items-center gap-2">
              <Globe className="w-5 h-5 text-[#C7A84A]" />
              Brand Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="brandName" className="text-slate-300">Brand Name</Label>
              <Input
                id="brandName"
                value={settings.brandName}
                onChange={(e) => updateSettings({ brandName: e.target.value })}
                className="bg-slate-800 border-slate-600 text-white mt-1"
              />
            </div>
            <div>
              <Label htmlFor="tagline" className="text-slate-300">Tagline</Label>
              <Input
                id="tagline"
                value={settings.tagline}
                onChange={(e) => updateSettings({ tagline: e.target.value })}
                className="bg-slate-800 border-slate-600 text-white mt-1"
              />
            </div>
          </CardContent>
        </Card>

        {/* Risk Governance */}
        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg text-white flex items-center gap-2">
              <Shield className="w-5 h-5 text-[#C7A84A]" />
              Risk Governance
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label className="text-slate-300">Safe Mode</Label>
                <p className="text-xs text-slate-500">
                  Restrict high-risk content publication
                </p>
              </div>
              <Switch checked={safeModeEnabled} onCheckedChange={toggleSafeMode} />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <Label className="text-slate-300">Risk Threshold</Label>
                <span className="text-sm text-white">{riskThreshold}</span>
              </div>
              <Slider
                value={[riskThreshold]}
                onValueChange={([value]) => setRiskThreshold(value)}
                max={100}
                step={5}
              />
              <p className="text-xs text-slate-500 mt-1">
                Content above this score requires senior review
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Notifications */}
        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg text-white flex items-center gap-2">
              <Bell className="w-5 h-5 text-[#C7A84A]" />
              Notifications
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label className="text-slate-300">Email Notifications</Label>
                <p className="text-xs text-slate-500">
                  Receive email alerts for important events
                </p>
              </div>
              <Switch
                checked={settings.emailNotifications}
                onCheckedChange={(checked) =>
                  updateSettings({ emailNotifications: checked })
                }
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label className="text-slate-300">Slack Notifications</Label>
                <p className="text-xs text-slate-500">
                  Send alerts to Slack channel
                </p>
              </div>
              <Switch
                checked={settings.slackNotifications}
                onCheckedChange={(checked) =>
                  updateSettings({ slackNotifications: checked })
                }
              />
            </div>
          </CardContent>
        </Card>

        {/* Weekly Brief Settings */}
        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg text-white flex items-center gap-2">
              <RefreshCw className="w-5 h-5 text-[#C7A84A]" />
              Weekly Brief Schedule
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label className="text-slate-300">Release Day</Label>
              <Select
                value={settings.weeklyBriefDay}
                onValueChange={(value) =>
                  updateSettings({ weeklyBriefDay: value })
                }
              >
                <SelectTrigger className="bg-slate-800 border-slate-600 text-white mt-1">
                  <SelectValue placeholder="Select day" />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-slate-700">
                  <SelectItem value="Monday">Monday</SelectItem>
                  <SelectItem value="Tuesday">Tuesday</SelectItem>
                  <SelectItem value="Wednesday">Wednesday</SelectItem>
                  <SelectItem value="Thursday">Thursday</SelectItem>
                  <SelectItem value="Friday">Friday</SelectItem>
                  <SelectItem value="Saturday">Saturday</SelectItem>
                  <SelectItem value="Sunday">Sunday</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Content Defaults */}
        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg text-white flex items-center gap-2">
              <Database className="w-5 h-5 text-[#C7A84A]" />
              Content Defaults
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label className="text-slate-300">Default Priority</Label>
              <Select
                value={settings.defaultPriority.toString()}
                onValueChange={(value) =>
                  updateSettings({ defaultPriority: parseInt(value) as 0 | 1 | 2 | 3 })
                }
              >
                <SelectTrigger className="bg-slate-800 border-slate-600 text-white mt-1">
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

            <div className="flex items-center justify-between">
              <div>
                <Label className="text-slate-300">Auto-Publish</Label>
                <p className="text-xs text-slate-500">
                  Automatically publish approved content
                </p>
              </div>
              <Switch
                checked={settings.autoPublishEnabled}
                onCheckedChange={(checked) =>
                  updateSettings({ autoPublishEnabled: checked })
                }
              />
            </div>
          </CardContent>
        </Card>

        {/* Security */}
        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg text-white flex items-center gap-2">
              <Lock className="w-5 h-5 text-[#C7A84A]" />
              Security
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
              <div className="flex items-center gap-3">
                <Database className="w-5 h-5 text-slate-400" />
                <div>
                  <p className="text-sm text-white">Last Backup</p>
                  <p className="text-xs text-slate-500">2 hours ago</p>
                </div>
              </div>
              <Button
                variant="outline"
                size="sm"
                className="border-slate-600 text-slate-300"
              >
                <RefreshCw className="w-3 h-3 mr-1" />
                Backup Now
              </Button>
            </div>

            <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
              <div className="flex items-center gap-3">
                <Users className="w-5 h-5 text-slate-400" />
                <div>
                  <p className="text-sm text-white">Active Sessions</p>
                  <p className="text-xs text-slate-500">1 active session</p>
                </div>
              </div>
              <Button
                variant="outline"
                size="sm"
                className="border-slate-600 text-slate-300"
              >
                Manage
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button
          onClick={handleSaveSettings}
          className="bg-[#C7A84A] hover:bg-[#d4b65c] text-[#0B1F3A] font-medium"
        >
          <Save className="w-4 h-4 mr-2" />
          Save Settings
        </Button>
      </div>
    </div>
  );
}
