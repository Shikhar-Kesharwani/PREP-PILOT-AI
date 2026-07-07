import { useState, useEffect } from 'react';
import { getDashboard } from '../api';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  BarChart, Bar
} from 'recharts';
import { Loader2, TrendingUp, Target, Brain, Activity, ArrowRight } from 'lucide-react';

export default function ProgressDashboard({ userId = 1 }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboard(userId)
      .then(res => setData(res.data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [userId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <Loader2 className="w-8 h-8 text-brand-400 animate-spin mb-4" />
        <p className="text-gray-400">Loading your performance data...</p>
      </div>
    );
  }

  if (!data || data.overview.total_questions === 0) {
    return (
      <div className="text-center py-20 animate-fade-in">
        <div className="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-6">
          <Activity className="w-10 h-10 text-gray-500" />
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">No Data Yet</h2>
        <p className="text-gray-400 max-w-md mx-auto">
          Start practicing in the Interview Simulator to see your analytics, performance trends, and AI recommendations here.
        </p>
      </div>
    );
  }

  const { overview, topic_performance, score_trend, company_stats, recommendations } = data;
  const companyData = Object.entries(company_stats).map(([name, score]) => ({ name, score }));

  return (
    <div className="max-w-6xl mx-auto space-y-6 pb-12 animate-fade-in">
      {/* Top Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="stat-card border-t-2 border-t-brand-500">
          <div className="text-gray-400 text-sm font-medium flex items-center gap-2">
            <Target className="w-4 h-4 text-brand-400" /> Overall Score
          </div>
          <div className="text-3xl font-black text-white">{overview.overall_score}<span className="text-lg text-gray-500 font-medium">/100</span></div>
        </div>
        <div className="stat-card border-t-2 border-t-purple-500">
          <div className="text-gray-400 text-sm font-medium flex items-center gap-2">
            <Brain className="w-4 h-4 text-purple-400" /> Questions Attempted
          </div>
          <div className="text-3xl font-black text-white">{overview.total_questions}</div>
        </div>
        <div className="stat-card border-t-2 border-t-blue-500">
          <div className="text-gray-400 text-sm font-medium flex items-center gap-2">
            <Activity className="w-4 h-4 text-blue-400" /> Mock Sessions
          </div>
          <div className="text-3xl font-black text-white">{overview.total_sessions}</div>
        </div>
        <div className="stat-card border-t-2 border-t-orange-500">
          <div className="text-gray-400 text-sm font-medium flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-orange-400" /> Day Streak
          </div>
          <div className="text-3xl font-black text-white">{overview.streak_days} <span className="text-lg text-orange-400">🔥</span></div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Chart */}
        <div className="lg:col-span-2 glass-card p-6">
          <h3 className="text-lg font-bold text-white mb-6">Performance Trend</h3>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={score_trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis domain={[0, 100]} stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc' }}
                  itemStyle={{ color: '#818cf8' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="score" 
                  stroke="#6366f1" 
                  strokeWidth={3}
                  dot={{ r: 4, fill: '#6366f1', strokeWidth: 2, stroke: '#1e293b' }}
                  activeDot={{ r: 6, fill: '#8b5cf6' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recommendations */}
        <div className="glass-card p-6 flex flex-col">
          <h3 className="text-lg font-bold text-white mb-4">Focus Areas</h3>
          <p className="text-sm text-gray-400 mb-6">Based on your recent mock interviews, focus on these topics:</p>
          
          <div className="space-y-4 flex-1">
            {recommendations.length > 0 ? recommendations.map((rec, i) => (
              <div key={i} className="bg-white/5 border border-white/10 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-white">{rec.topic}</span>
                  <span className="text-xs font-bold text-red-400">{rec.current_score}/100</span>
                </div>
                <p className="text-xs text-gray-400 leading-relaxed">{rec.suggestion}</p>
              </div>
            )) : (
              <div className="text-center text-sm text-gray-500 py-10">
                Keep practicing to generate targeted recommendations.
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Topic Mastery */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-bold text-white mb-6">Topic Mastery</h3>
          <div className="space-y-5">
            {Object.entries(topic_performance.all).map(([topic, score]) => (
              <div key={topic}>
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="text-gray-300 font-medium">{topic}</span>
                  <span className="text-gray-400">{score}%</span>
                </div>
                <div className="w-full h-2.5 bg-white/5 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full ${
                      score >= 80 ? 'bg-green-500' :
                      score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${score}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Company Performance */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-bold text-white mb-6">Company Match Scores</h3>
          <div className="h-[280px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={companyData} layout="vertical" margin={{ left: 30 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={true} vertical={false} />
                <XAxis type="number" domain={[0, 100]} stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis dataKey="name" type="category" stroke="#e2e8f0" fontSize={12} tickLine={false} axisLine={false} width={80} />
                <RechartsTooltip 
                  cursor={{ fill: '#ffffff0a' }}
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                />
                <Bar dataKey="score" fill="#8b5cf6" radius={[0, 4, 4, 0]} barSize={24} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
