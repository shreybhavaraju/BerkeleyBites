import { useState, type FormEvent, type KeyboardEvent } from 'react';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
}

const COMMAND_HINTS = [
  { cmd: '/recommend', desc: 'Get personalized recommendations', icon: '✨' },
  { cmd: '/recommend lunch', desc: 'Recommendations for specific meal', icon: '🍽️' },
  { cmd: '/why [dish]', desc: 'Explain why a dish fits you', icon: '🤔' },
  { cmd: '/similar [dish]', desc: 'Find similar dishes on menu', icon: '🔍' },
  { cmd: '/help', desc: 'Show all commands', icon: '📖' },
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
        <div className="absolute bottom-full left-0 right-0 mb-2 bg-white rounded-xl shadow-xl border border-slate-border overflow-hidden animate-slide-down">
          <div className="px-4 py-2.5 bg-berkeley/5 border-b border-slate-border">
            <span className="text-xs font-bold text-berkeley uppercase tracking-wider">Available Commands</span>
          </div>
          <div className="max-h-52 overflow-y-auto">
            {COMMAND_HINTS.map((hint) => (
              <button
                key={hint.cmd}
                onClick={() => handleHintClick(hint.cmd)}
                className="w-full text-left px-4 py-2.5 hover:bg-berkeley-gold/10 transition-colors flex items-center gap-3 group"
              >
                <span className="text-lg opacity-60 group-hover:opacity-100 transition-opacity">{hint.icon}</span>
                <div className="flex-1 min-w-0">
                  <span className="font-mono text-sm font-semibold text-berkeley">{hint.cmd}</span>
                  <span className="text-xs text-gray-500 block mt-0.5">{hint.desc}</span>
                </div>
                <svg className="w-4 h-4 text-gray-300 group-hover:text-berkeley-gold transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            ))}
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex gap-3">
        <div className="relative flex-1">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onFocus={() => setShowHints(true)}
            onBlur={() => setTimeout(() => setShowHints(false), 200)}
            onKeyDown={handleKeyDown}
            placeholder="Try /recommend or ask anything..."
            disabled={isLoading}
            className="w-full px-4 py-3 bg-slate-warm border border-slate-border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-berkeley-gold focus:border-transparent disabled:bg-gray-100 disabled:text-gray-400 placeholder:text-gray-400"
          />
          {!isLoading && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400">
              Press Enter ↵
            </div>
          )}
        </div>
        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="px-6 py-3 bg-berkeley text-white rounded-xl text-sm font-semibold hover:bg-berkeley-light disabled:opacity-40 disabled:cursor-not-allowed transition-all hover:shadow-lg hover:-translate-y-0.5 active:translate-y-0"
        >
          {isLoading ? (
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
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
          ) : (
            <span className="flex items-center gap-2">
              Send
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </span>
          )}
        </button>
      </form>
    </div>
  );
}
