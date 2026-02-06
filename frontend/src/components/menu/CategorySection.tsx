import { useState } from 'react';
import type { Dish } from '../../types';
import { DishCard } from './DishCard';

interface CategorySectionProps {
  category: string;
  dishes: Dish[];
  defaultExpanded?: boolean;
}

export function CategorySection({
  category,
  dishes,
  defaultExpanded = true,
}: CategorySectionProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  return (
    <div className="bg-white rounded-xl border border-slate-border overflow-hidden shadow-sm">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-5 py-4 hover:bg-slate-warm/50 transition-colors group"
      >
        <div className="flex items-center gap-3">
          <span className="w-8 h-8 bg-berkeley-gold/20 rounded-lg flex items-center justify-center text-sm group-hover:bg-berkeley-gold/30 transition-colors">
            🍴
          </span>
          <span className="font-semibold text-berkeley font-display text-lg">
            {category}
          </span>
          <span className="px-2 py-0.5 bg-berkeley/10 rounded-full text-xs font-semibold text-berkeley">
            {dishes.length}
          </span>
        </div>
        <svg
          className={`w-5 h-5 text-gray-400 transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isExpanded && (
        <div className="px-5 pb-3 divide-y divide-slate-border">
          {dishes.map((dish) => (
            <DishCard key={dish.dish_id} dish={dish} />
          ))}
        </div>
      )}
    </div>
  );
}
