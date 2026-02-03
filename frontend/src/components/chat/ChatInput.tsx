import { useState, type FormEvent, type KeyboardEvent } from 'react';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
}

const COMMAND_HINTS = [
  { cmd: '/recommend', desc: 'Get personalized recommendations' },
  { cmd: '/recommend lunch', desc: 'Recommendations for specific meal' },
  { cmd: '/why [dish]', desc: 'Explain why a dish fits you' },
  { cmd: '/similar [dish]', desc: 'Find similar dishes on menu' },
  { cmd: '/help', desc: 'Show all commands' },
];

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [input, setInput] = useState('');
  const [showHints, setShowHints] = useState(false);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSend(input.trim());
      setInput('');
      setShowHints(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Escape') {
      setShowHints(false);
    }
  };

  const handleHintClick = (cmd: string) => {
    setInput(cmd + ' ');
    setShowHints(false);
  };

  return (
    <div className="relative">
      {/* Command hints */}
      {showHints && (
        <div className="absolute bottom-full left-0 right-0 mb-2 bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden">
          <div className="px-3 py-2 bg-gray-50 border-b border-gray-200">
            <span className="text-xs font-medium text-gray-600">Available Commands</span>
          </div>
          <div className="max-h-48 overflow-y-auto">
            {COMMAND_HINTS.map((hint) => (
              <button
                key={hint.cmd}
                onClick={() => handleHintClick(hint.cmd)}
                className="w-full text-left px-3 py-2 hover:bg-gray-50 transition-colors"
              >
                <span className="font-mono text-sm text-berkeley">{hint.cmd}</span>
                <span className="text-xs text-gray-500 ml-2">{hint.desc}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="relative flex-1">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onFocus={() => setShowHints(true)}
            onBlur={() => setTimeout(() => setShowHints(false), 200)}
            onKeyDown={handleKeyDown}
            placeholder="Try: /recommend lunch"
            disabled={isLoading}
            className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-berkeley focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
          />
        </div>
        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="px-5 py-2.5 bg-berkeley text-white rounded-lg text-sm font-medium hover:bg-berkeley-light transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <span className="inline-flex items-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            </span>
          ) : (
            'Ask'
          )}
        </button>
      </form>
    </div>
  );
}
