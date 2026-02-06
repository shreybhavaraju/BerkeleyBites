import type { QuestionOption } from '../../types';

interface QuestionMessageProps {
  questionId: string;
  questionText: string;
  options: QuestionOption[];
  onAnswer: (questionId: string, value: string) => void;
  disabled?: boolean;
  answeredValue?: string;
}

export function QuestionMessage({
  questionId,
  questionText,
  options,
  onAnswer,
  disabled,
  answeredValue,
}: QuestionMessageProps) {
  const isAnswered = !!answeredValue;

  return (
    <div className="bg-white border border-slate-border rounded-xl p-4 shadow-sm">
      <div className="flex items-start gap-3 mb-4">
        <div className="w-8 h-8 bg-berkeley-gold/20 rounded-lg flex items-center justify-center flex-shrink-0">
          <span className="text-sm">❓</span>
        </div>
        <p className="text-sm text-gray-700 leading-relaxed pt-1">{questionText}</p>
      </div>
      <div className="flex flex-wrap gap-2 pl-11">
        {options.map((option) => {
          const isSelected = answeredValue === option.value;
          return (
            <button
              key={option.value}
              onClick={() => !isAnswered && onAnswer(questionId, option.value)}
              disabled={disabled || isAnswered}
              className={`
                px-4 py-2 rounded-lg text-sm font-medium transition-all
                ${
                  isSelected
                    ? 'bg-berkeley text-white shadow-md'
                    : isAnswered
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-slate-warm hover:bg-berkeley/10 text-gray-700 hover:text-berkeley border border-slate-border hover:border-berkeley/30'
                }
                disabled:opacity-50
              `}
            >
              {option.emoji && <span className="mr-1.5">{option.emoji}</span>}
              {option.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
