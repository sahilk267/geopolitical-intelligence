// ============================================
// AUDIENCE INTELLIGENCE SECTION
// Viewer Analytics & Feedback Management
// ============================================

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  Users,
  TrendingUp,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  Minus,
  Eye,
  Clock,
  Target,
  BarChart3,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

// Sample data
const subscriberGrowth = [
  { month: 'Jan', subscribers: 1200 },
  { month: 'Feb', subscribers: 1850 },
  { month: 'Mar', subscribers: 2800 },
  { month: 'Apr', subscribers: 4200 },
  { month: 'May', subscribers: 5800 },
  { month: 'Jun', subscribers: 7500 },
];

const engagementData = [
  { day: 'Mon', views: 12000, comments: 145 },
  { day: 'Tue', views: 8500, comments: 98 },
  { day: 'Wed', views: 18000, comments: 234 },
  { day: 'Thu', views: 6000, comments: 67 },
  { day: 'Fri', views: 15000, comments: 189 },
  { day: 'Sat', views: 9000, comments: 112 },
  { day: 'Sun', views: 7500, comments: 89 },
];

const sentimentData = [
  { name: 'Positive', value: 65, color: '#22c55e' },
  { name: 'Neutral', value: 25, color: '#64748b' },
  { name: 'Negative', value: 10, color: '#ef4444' },
];

const topicDemand = [
  { topic: 'Israel-Iran', demand: 92 },
  { topic: 'Energy Security', demand: 85 },
  { topic: 'Proxy Warfare', demand: 78 },
  { topic: 'Sanctions', demand: 72 },
  { topic: 'Diplomacy', demand: 65 },
  { topic: 'Military Balance', demand: 58 },
];

const recentComments = [
  {
    id: 1,
    user: 'StrategicThinker',
    comment: 'Excellent analysis on the Hormuz chokepoint. Would love to see more on India\'s energy security angle.',
    sentiment: 'positive',
    sentimentScore: 0.85,
    platform: 'YouTube',
    timestamp: '2 hours ago',
  },
  {
    id: 2,
    user: 'PolicyWonk',
    comment: 'The ERI framework is brilliant. Can you explain more about the weighting methodology?',
    sentiment: 'positive',
    sentimentScore: 0.78,
    platform: 'Twitter',
    timestamp: '4 hours ago',
  },
  {
    id: 3,
    user: 'NeutralObserver',
    comment: 'Good content but could use more historical context in the Israel-Iran piece.',
    sentiment: 'neutral',
    sentimentScore: 0.52,
    platform: 'YouTube',
    timestamp: '6 hours ago',
  },
  {
    id: 4,
    user: 'GeoPoliticsFan',
    comment: 'This is exactly the kind of structured analysis we need. Subscribed!',
    sentiment: 'positive',
    sentimentScore: 0.92,
    platform: 'LinkedIn',
    timestamp: '8 hours ago',
  },
];

export function AudienceIntelligence() {

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Audience Intelligence</h1>
        <p className="text-slate-400">Viewer analytics, sentiment tracking, and feedback management</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-400">Total Subscribers</p>
                <p className="text-2xl font-bold text-white">7,500</p>
              </div>
              <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                <Users className="w-5 h-5 text-blue-400" />
              </div>
            </div>
            <div className="flex items-center gap-1 mt-2 text-xs">
              <TrendingUp className="w-3 h-3 text-green-400" />
              <span className="text-green-400">+12%</span>
              <span className="text-slate-500">this month</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-400">Weekly Views</p>
                <p className="text-2xl font-bold text-white">76K</p>
              </div>
              <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                <Eye className="w-5 h-5 text-green-400" />
              </div>
            </div>
            <div className="flex items-center gap-1 mt-2 text-xs">
              <TrendingUp className="w-3 h-3 text-green-400" />
              <span className="text-green-400">+8%</span>
              <span className="text-slate-500">vs last week</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-400">Avg Watch Time</p>
                <p className="text-2xl font-bold text-white">14:32</p>
              </div>
              <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center">
                <Clock className="w-5 h-5 text-amber-400" />
              </div>
            </div>
            <div className="flex items-center gap-1 mt-2 text-xs">
              <TrendingUp className="w-3 h-3 text-green-400" />
              <span className="text-green-400">+3%</span>
              <span className="text-slate-500">improvement</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-400">Engagement Rate</p>
                <p className="text-2xl font-bold text-white">8.4%</p>
              </div>
              <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                <Target className="w-5 h-5 text-purple-400" />
              </div>
            </div>
            <div className="flex items-center gap-1 mt-2 text-xs">
              <TrendingUp className="w-3 h-3 text-green-400" />
              <span className="text-green-400">+1.2%</span>
              <span className="text-slate-500">vs industry avg</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Subscriber Growth */}
        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-[#C7A84A]" />
              Subscriber Growth
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={subscriberGrowth}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
                  <YAxis stroke="#64748b" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0B1F3A',
                      border: '1px solid #1e293b',
                      borderRadius: '8px',
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="subscribers"
                    stroke="#C7A84A"
                    strokeWidth={2}
                    dot={{ fill: '#C7A84A' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Sentiment Distribution */}
        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg text-white flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-[#C7A84A]" />
              Sentiment Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={sentimentData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {sentimentData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0B1F3A',
                      border: '1px solid #1e293b',
                      borderRadius: '8px',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-4 mt-4">
              {sentimentData.map((item) => (
                <div key={item.name} className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-xs text-slate-400">
                    {item.name} ({item.value}%)
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Topic Demand & Recent Comments */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Topic Demand */}
        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg text-white flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-[#C7A84A]" />
              Topic Demand Heatmap
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topicDemand.map((topic) => (
                <div key={topic.topic}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-slate-300">{topic.topic}</span>
                    <span className="text-sm text-slate-400">{topic.demand}%</span>
                  </div>
                  <Progress value={topic.demand} className="h-2" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Comments */}
        <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg text-white flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-[#C7A84A]" />
              Recent Feedback
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 max-h-80 overflow-y-auto">
              {recentComments.map((comment) => (
                <div
                  key={comment.id}
                  className="p-3 bg-slate-800/50 rounded-lg border border-slate-700/50"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-white">
                        {comment.user}
                      </span>
                      <Badge variant="outline" className="text-[10px] border-slate-600 text-slate-400">
                        {comment.platform}
                      </Badge>
                    </div>
                    {comment.sentiment === 'positive' && (
                      <ThumbsUp className="w-4 h-4 text-green-400" />
                    )}
                    {comment.sentiment === 'negative' && (
                      <ThumbsDown className="w-4 h-4 text-red-400" />
                    )}
                    {comment.sentiment === 'neutral' && (
                      <Minus className="w-4 h-4 text-slate-400" />
                    )}
                  </div>
                  <p className="text-sm text-slate-400 mt-2 line-clamp-2">
                    {comment.comment}
                  </p>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-xs text-slate-500">{comment.timestamp}</span>
                    <span className="text-xs text-slate-500">
                      Score: {(comment.sentimentScore * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Engagement Chart */}
      <Card className="bg-[#0B1F3A]/50 border-slate-700/50">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg text-white flex items-center gap-2">
            <Eye className="w-5 h-5 text-[#C7A84A]" />
            Weekly Engagement
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={engagementData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="day" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0B1F3A',
                    border: '1px solid #1e293b',
                    borderRadius: '8px',
                  }}
                />
                <Bar dataKey="views" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="comments" fill="#C7A84A" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
