import type { AgentStep } from '../../types';

interface AgentProgressProps {
  steps: AgentStep[];
}

export function AgentProgress({ steps }: AgentProgressProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg px-4 py-3 shadow-sm">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-lg">🤖</span>
        <span className="text-sm font-medium text-gray-700">Analyzing your request...</span>
      </div>
      <div className="space-y-2">
        {steps.map((step) => (
          <div key={step.id} className="flex items-center gap-2.5">
            {step.status === 'complete' && (
              <span className="w-5 h-5 flex items-center justify-center text-green-600 font-bold">
                ✓
              </span>
            )}
            {step.status === 'loading' && (
              <span className="w-5 h-5 flex items-center justify-center">
                <span className="w-4 h-4 border-2 border-berkeley-gold border-t-transparent rounded-full animate-spin" />
              </span>
            )}
            {step.status === 'pending' && (
              <span className="w-5 h-5 flex items-center justify-center text-gray-300">
                ○
              </span>
            )}
            <span
              className={`text-sm ${
                step.status === 'complete'
                  ? 'text-gray-700'
                  : step.status === 'loading'
                  ? 'text-berkeley font-medium'
                  : 'text-gray-400'
              }`}
            >
              {step.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
