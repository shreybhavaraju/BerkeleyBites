import type { AgentStep } from '../../types';

interface AgentProgressProps {
  steps: AgentStep[];
}

export function AgentProgress({ steps }: AgentProgressProps) {
  return (
    <div className="bg-white border border-slate-border rounded-xl p-4 shadow-sm">
      <div className="flex items-center gap-3 mb-4 pb-3 border-b border-slate-border">
        <div className="w-8 h-8 bg-berkeley-gold/20 rounded-lg flex items-center justify-center">
          <span className="text-sm">🤖</span>
        </div>
        <div>
          <span className="text-sm font-semibold text-berkeley">Analyzing your request</span>
          <span className="text-xs text-gray-400 block">Multi-agent processing</span>
        </div>
      </div>
      <div className="space-y-2.5">
        {steps.map((step) => (
          <div key={step.id} className="flex items-center gap-3">
            {step.status === 'complete' && (
              <span className="w-6 h-6 flex items-center justify-center bg-success/10 rounded-full">
                <svg className="w-4 h-4 text-success" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </span>
            )}
            {step.status === 'loading' && (
              <span className="w-6 h-6 flex items-center justify-center">
                <span className="w-5 h-5 border-2 border-berkeley-gold border-t-transparent rounded-full animate-spin" />
              </span>
            )}
            {step.status === 'pending' && (
              <span className="w-6 h-6 flex items-center justify-center">
                <span className="w-2 h-2 bg-gray-300 rounded-full" />
              </span>
            )}
            <span
              className={`text-sm ${
                step.status === 'complete'
                  ? 'text-gray-600'
                  : step.status === 'loading'
                  ? 'text-berkeley font-semibold'
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
