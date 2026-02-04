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
    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
      <p className="text-sm text-gray-700 mb-3">{questionText}</p>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => {
          const isSelected = answeredValue === option.value;
          return (
            <button
              key={option.value}
              onClick={() => !isAnswered && onAnswer(questionId, option.value)}
              disabled={disabled || isAnswered}
              className={`
                px-3 py-2 rounded-lg text-sm transition-all
                ${
                  isSelected
                    ? 'bg-berkeley text-white border-berkeley'
                    : isAnswered
                    ? 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed'
                    : 'bg-gray-50 hover:bg-berkeley/10 border-gray-200 hover:border-berkeley/30'
                }
                border disabled:opacity-50
              `}
            >
              {option.emoji && <span className="mr-1">{option.emoji}</span>}
              {option.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
