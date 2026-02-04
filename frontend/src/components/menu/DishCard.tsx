import { useState, useEffect, useCallback } from 'react';
import type { Dish } from '../../types';
import { submitFeedback, getDishFeedback } from '../../api/client';
import { useApp } from '../../context/AppContext';

interface DishCardProps {
  dish: Dish;
}

export function DishCard({ dish }: DishCardProps) {
  const { refreshFeedbackStats } = useApp();
  const [feedback, setFeedback] = useState<boolean | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    getDishFeedback(dish.dish_id)
      .then((data) => setFeedback(data.feedback))
      .catch(() => {});
  }, [dish.dish_id]);

  const handleFeedback = useCallback(
    async (liked: boolean) => {
      if (isSubmitting) return;

      setIsSubmitting(true);
      setFeedback(liked);

      try {
        await submitFeedback(dish.dish_id, dish.dish_name, liked);
        refreshFeedbackStats();
      } catch {
        setFeedback(null);
      } finally {
        setIsSubmitting(false);
      }
    },
    [dish.dish_id, dish.dish_name, isSubmitting, refreshFeedbackStats]
  );

  // Build dietary tags
  const tags: { label: string; emoji: string; color: string }[] = [];

  if (dish.is_vegan) {
    tags.push({ label: 'Vegan', emoji: '🌱', color: 'bg-green-100 text-green-700 border-green-200' });
  } else if (dish.is_vegetarian) {
    tags.push({ label: 'Vegetarian', emoji: '🥗', color: 'bg-green-50 text-green-600 border-green-100' });
  }

  if (dish.is_halal) {
    tags.push({ label: 'Halal', emoji: '☪️', color: 'bg-blue-50 text-blue-700 border-blue-200' });
  }

  if (dish.is_kosher) {
    tags.push({ label: 'Kosher', emoji: '✡️', color: 'bg-blue-50 text-blue-700 border-blue-200' });
  }

  return (
    <div className="flex items-start justify-between py-4 group">
      <div className="flex-1 min-w-0">
        <h4 className="font-medium text-gray-800 group-hover:text-berkeley transition-colors">
          {dish.dish_name}
        </h4>
        {tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-2">
            {tags.map((tag) => (
              <span
                key={tag.label}
                className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium border ${tag.color}`}
              >
                {tag.emoji} {tag.label}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="flex items-center gap-2 ml-4">
        {feedback === null ? (
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={() => handleFeedback(true)}
              disabled={isSubmitting}
              className="p-2 text-gray-400 hover:text-success hover:bg-success/10 rounded-lg transition-all disabled:opacity-50 hover:scale-110"
              title="I'd eat this"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
              </svg>
            </button>
            <button
              onClick={() => handleFeedback(false)}
              disabled={isSubmitting}
              className="p-2 text-gray-400 hover:text-error hover:bg-error/10 rounded-lg transition-all disabled:opacity-50 hover:scale-110"
              title="Not for me"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76.94m-7 10v5a2 2 0 002 2h.096c.5 0 .905-.405.905-.904 0-.715.211-1.413.608-2.008L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5" />
              </svg>
            </button>
          </div>
        ) : feedback ? (
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-success/10 text-success border border-success/20">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            Liked
          </span>
        ) : (
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-gray-100 text-gray-500 border border-gray-200">
            Passed
          </span>
        )}
      </div>
    </div>
  );
}
