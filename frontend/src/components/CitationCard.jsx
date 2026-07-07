import { BookOpen, ExternalLink } from 'lucide-react';

export default function CitationCard({ citations = [] }) {
  if (!citations || citations.length === 0) return null;

  return (
    <div className="glass-card p-4 space-y-3 animate-fade-in">
      <div className="flex items-center gap-2 text-sm font-semibold text-gray-300">
        <BookOpen className="w-4 h-4 text-brand-400" />
        <span>📚 Sources Used</span>
        <span className="badge bg-brand-600/20 text-brand-300 border border-brand-500/20 ml-auto">
          {citations.length} source{citations.length !== 1 ? 's' : ''}
        </span>
      </div>

      <div className="space-y-2">
        {citations.map((cite, i) => {
          const score = cite.relevance_score || 0;
          const pct   = Math.round(score * 100);
          const color =
            pct >= 80 ? 'bg-green-500' :
            pct >= 60 ? 'bg-yellow-500' :
            'bg-orange-500';

          return (
            <div
              key={i}
              className="flex items-center justify-between gap-3 p-3 rounded-xl bg-white/5 border border-white/8 hover:bg-white/8 transition-colors"
            >
              <div className="flex items-center gap-3 min-w-0">
                <div className={`w-2 h-2 rounded-full flex-shrink-0 ${color}`} />
                <div className="min-w-0">
                  <p className="text-sm text-white font-medium truncate">
                    {cite.file_name || 'Unknown Source'}
                  </p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-xs text-gray-500">
                      Page {cite.page_number || '?'}
                    </span>
                    {cite.topic && (
                      <>
                        <span className="text-gray-600">·</span>
                        <span className="text-xs text-brand-400">{cite.topic}</span>
                      </>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 flex-shrink-0">
                <div className="flex items-center gap-1.5">
                  <div className="w-16 h-1.5 bg-white/10 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${color}`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <span className={`text-xs font-semibold ${
                    pct >= 80 ? 'text-green-400' :
                    pct >= 60 ? 'text-yellow-400' :
                    'text-orange-400'
                  }`}>
                    {pct}%
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
