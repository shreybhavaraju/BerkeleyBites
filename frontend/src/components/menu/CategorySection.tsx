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
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors"
      >
        <span className="font-medium text-gray-900">
          {category}
          <span className="ml-2 text-sm text-gray-500 font-normal">
            ({dishes.length} items)
          </span>
        </span>
        <span className="text-gray-400">{isExpanded ? '▼' : '▶'}</span>
      </button>

      {isExpanded && (
        <div className="px-4 divide-y divide-gray-100">
          {dishes.map((dish) => (
            <DishCard key={dish.dish_id} dish={dish} />
          ))}
        </div>
      )}
    </div>
  );
}
