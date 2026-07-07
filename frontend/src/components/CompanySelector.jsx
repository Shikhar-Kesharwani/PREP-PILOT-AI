import { useState, useEffect } from 'react';
import { getCompanies } from '../api';
import { Loader2, Briefcase, Star, Target, CheckCircle2 } from 'lucide-react';

export default function CompanySelector({ onSelect }) {
  const [companies, setCompanies] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCompanies()
      .then(res => setCompanies(res.data))
      .catch(err => console.error("Failed to load companies:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <Loader2 className="w-8 h-8 text-brand-400 animate-spin mb-4" />
        <p className="text-gray-400">Loading company profiles...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-10">
        <h2 className="text-3xl font-bold text-white mb-3">Choose Your Target Company</h2>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Each company has a unique interview style and evaluation criteria.
          Select a company to start a tailored mock interview.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Object.values(companies).map((company) => (
          <button
            key={company.name}
            onClick={() => onSelect(company.name)}
            className="glass-card-hover p-6 text-left flex flex-col h-full group"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center text-2xl border border-white/20 group-hover:bg-brand-500/20 group-hover:border-brand-500/30 transition-all">
                {company.logo_emoji}
              </div>
              <span className={`badge ${
                company.difficulty === 'Very Hard' ? 'bg-red-500/20 text-red-300' :
                company.difficulty === 'Hard' ? 'bg-orange-500/20 text-orange-300' :
                'bg-yellow-500/20 text-yellow-300'
              }`}>
                {company.difficulty}
              </span>
            </div>

            <h3 className="text-xl font-bold text-white mb-2">{company.name}</h3>
            
            <p className="text-sm text-gray-400 mb-6 flex-grow">
              {company.known_for}
            </p>

            <div className="space-y-4 w-full mt-auto">
              <div>
                <div className="flex items-center gap-1.5 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                  <Target className="w-3.5 h-3.5" /> Focus Areas
                </div>
                <div className="flex flex-wrap gap-2">
                  {company.focus_areas.map(area => (
                    <span key={area} className="tag bg-white/5 text-gray-300 border border-white/10">
                      {area}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <div className="flex items-center gap-1.5 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                  <Star className="w-3.5 h-3.5" /> Style
                </div>
                <p className="text-xs text-gray-400 line-clamp-2">
                  {company.interview_style}
                </p>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-white/10 flex items-center justify-between text-sm font-medium text-brand-400 opacity-0 group-hover:opacity-100 transition-opacity">
              <span>Start Interview</span>
              <span>→</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
