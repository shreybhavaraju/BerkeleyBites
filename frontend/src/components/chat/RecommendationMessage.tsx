import { useState } from 'react';
import type { AgentSummary } from '../../types';
import { AgentSummaryCard } from './AgentSummaryCard';

interface RecommendationMessageProps {
  agentSummaries: Record<string, AgentSummary>;
  recommendation: string;
}

export function RecommendationMessage({
  agentSummaries,
  recommendation,
}: RecommendationMessageProps) {
  const [showDetails, setShowDetails] = useState(true);
  const summaryOrder = ['mood', 'preferences', 'menu'];
  const orderedSummaries = summaryOrder
    .filter((key) => agentSummaries[key])
    .map((key) => ({ key, ...agentSummaries[key] }));

  return (
    <div className="bg-white border border-slate-border rounded-xl shadow-sm overflow-hidden">
      {/* Agent Summaries Section */}
      {orderedSummaries.length > 0 && (
        <div className="border-b border-slate-border">
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="w-full px-4 py-3 flex items-center gap-2 text-sm text-gray-600 hover:bg-slate-warm/50 transition-colors"
          >
            <svg
              className={`w-4 h-4 transition-transform ${showDetails ? 'rotate-0' : '-rotate-90'}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
            <span className="font-semibold text-berkeley">What I considered</span>
            <span className="text-xs bg-berkeley/10 text-berkeley px-2 py-0.5 rounded-full ml-auto">
              {orderedSummaries.length} agents
            </span>
          </button>

          {showDetails && (
            <div className="px-4 pb-4 grid grid-cols-2 gap-3">
              {orderedSummaries.map((summary) => (
                <AgentSummaryCard
                  key={summary.key}
                  icon={summary.icon}
                  title={summary.title}
                  points={summary.points}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Recommendation Section */}
      <div className="p-4 bg-gradient-to-br from-berkeley/5 to-berkeley-gold/5">
        <h4 className="font-semibold text-sm flex items-center gap-2 mb-3 text-berkeley">
          <span className="w-6 h-6 bg-berkeley-gold rounded-md flex items-center justify-center text-xs">🎯</span>
          <span>My Recommendations</span>
        </h4>
        <div className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed pl-8">
          {recommendation}
        </div>
      </div>
    </div>
  );
}
