// ============================================
// AUDIENCE INTELLIGENCE SECTION
// Under Development - Coming Soon
// ============================================

import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Users,
  TrendingUp,
  MessageSquare,
  Eye,
  Clock,
  Target,
  BarChart3,
  Sparkles,
} from 'lucide-react';

const plannedFeatures = [
  { icon: Eye, title: 'Cross-Platform View Analytics', description: 'Track views, impressions, and reach across YouTube, Telegram, and other platforms.' },
  { icon: MessageSquare, title: 'Sentiment Analysis', description: 'AI-powered sentiment scoring of audience comments and reactions.' },
  { icon: TrendingUp, title: 'Subscriber Growth Tracking', description: 'Monitor subscriber and follower growth with trend projections.' },
  { icon: Target, title: 'Content Topic Demand', description: 'Identify which geopolitical topics generate the most engagement.' },
  { icon: BarChart3, title: 'Engagement Rate Benchmarks', description: 'Compare your engagement rates against industry averages.' },
  { icon: Clock, title: 'Optimal Posting Times', description: 'Discover the best times to publish for maximum audience reach.' },
];

export function AudienceIntelligence() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Audience Intelligence</h1>
        <p className="text-slate-400">Viewer analytics, sentiment tracking, and feedback management</p>
      </div>

      {/* Status Banner */}
      <Card className="bg-gradient-to-r from-[#0B1F3A] to-[#162d4f] border-[#C7A84A]/30">
        <CardContent className="p-8 text-center">
          <div className="w-16 h-16 bg-[#C7A84A]/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <Sparkles className="w-8 h-8 text-[#C7A84A]" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Under Development</h2>
          <p className="text-slate-400 max-w-lg mx-auto mb-4">
            This module is being built to provide real-time audience analytics powered by the platform APIs
            connected via the Distribution tab. Once social accounts are fully linked, data will flow automatically.
          </p>
          <Badge variant="outline" className="border-[#C7A84A]/50 text-[#C7A84A]">
            Phase 3 — Expected in Next Sprint
          </Badge>
        </CardContent>
      </Card>

      {/* Planned Features Grid */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4">Planned Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {plannedFeatures.map((feature) => {
            const Icon = feature.icon;
            return (
              <Card key={feature.title} className="bg-[#0B1F3A]/50 border-slate-700/50">
                <CardContent className="p-5">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center shrink-0">
                      <Icon className="w-5 h-5 text-[#C7A84A]" />
                    </div>
                    <div>
                      <h3 className="font-medium text-white text-sm">{feature.title}</h3>
                      <p className="text-xs text-slate-400 mt-1">{feature.description}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}
