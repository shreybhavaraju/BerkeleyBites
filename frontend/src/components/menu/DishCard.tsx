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
      // Optimistic update
      setFeedback(liked);

      try {
        await submitFeedback(dish.dish_id, dish.dish_name, liked);
        refreshFeedbackStats();
      } catch {
        // Revert on error
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
    tags.push({ label: 'Vegan', emoji: '🌱', color: 'bg-green-100 text-green-800' });
  } else if (dish.is_vegetarian) {
    tags.push({ label: 'Vegetarian', emoji: '🥗', color: 'bg-green-50 text-green-700' });
  }

  if (dish.is_halal) {
    tags.push({ label: 'Halal', emoji: '☪️', color: 'bg-blue-100 text-blue-800' });
  }

  if (dish.is_kosher) {
    tags.push({ label: 'Kosher', emoji: '✡️', color: 'bg-blue-100 text-blue-800' });
  }

  return (
    <div className="flex items-start justify-between py-3 border-b border-gray-100 last:border-0">
      <div className="flex-1 min-w-0">
        <h4 className="font-medium text-gray-900">{dish.dish_name}</h4>
        {tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-1.5">
            {tags.map((tag) => (
              <span
                key={tag.label}
                className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${tag.color}`}
              >
                {tag.emoji} {tag.label}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="flex items-center gap-2 ml-4">
        {feedback === null ? (
          <>
            <button
              onClick={() => handleFeedback(true)}
              disabled={isSubmitting}
              className="p-2 text-gray-400 hover:text-success hover:bg-green-50 rounded-lg transition-colors disabled:opacity-50"
              title="I'd eat this"
            >
              👍
            </button>
            <button
              onClick={() => handleFeedback(false)}
              disabled={isSubmitting}
              className="p-2 text-gray-400 hover:text-error hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
              title="Not for me"
            >
              👎
            </button>
          </>
        ) : feedback ? (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
            👍 Liked
          </span>
        ) : (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
            👎 Passed
          </span>
        )}
      </div>
    </div>
  );
}
