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
  const summaryOrder = ['mood', 'weather', 'preferences', 'menu'];
  const orderedSummaries = summaryOrder
    .filter((key) => agentSummaries[key])
    .map((key) => ({ key, ...agentSummaries[key] }));

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      {/* Agent Summaries Section */}
      {orderedSummaries.length > 0 && (
        <div className="border-b border-gray-100">
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="w-full px-4 py-2 flex items-center gap-2 text-sm text-gray-600 hover:bg-gray-50 transition-colors"
          >
            <span
              className={`transition-transform ${showDetails ? 'rotate-0' : '-rotate-90'}`}
            >
              ▼
            </span>
            <span className="font-medium">What I considered</span>
            <span className="text-xs text-gray-400 ml-auto">
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
      <div className="p-4">
        <h4 className="font-medium text-sm flex items-center gap-2 mb-3 text-berkeley">
          <span>🎯</span>
          <span>My Recommendations</span>
        </h4>
        <div className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
          {recommendation}
        </div>
      </div>
    </div>
  );
}
