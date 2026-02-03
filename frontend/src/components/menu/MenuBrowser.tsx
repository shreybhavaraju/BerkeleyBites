import { useMenu } from '../../hooks/useMenu';
import { useApp } from '../../context/AppContext';
import { DiningHallSelect } from './DiningHallSelect';
import { MealTabs } from './MealTabs';
import { CategorySection } from './CategorySection';

function LoadingSkeleton() {
  return (
    <div className="space-y-4 animate-pulse">
      {[1, 2, 3].map((i) => (
        <div key={i} className="border border-gray-200 rounded-lg p-4">
          <div className="h-5 bg-gray-200 rounded w-1/3 mb-4" />
          <div className="space-y-3">
            {[1, 2, 3].map((j) => (
              <div key={j} className="h-4 bg-gray-100 rounded w-full" />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

export function MenuBrowser() {
  const { menuSummary, selectedHall, selectedMeal } = useApp();
  const { dishes, dishesByCategory, isLoading, error } = useMenu();

  const categories = Object.keys(dishesByCategory).sort();

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
        <DiningHallSelect />
        <MealTabs />
      </div>

      {/* Dish count */}
      {menuSummary && dishes.length > 0 && (
        <p className="text-sm text-gray-600">
          ✓ <span className="font-medium">{dishes.length}</span> dishes matching your
          profile
        </p>
      )}

      {/* Menu content */}
      <div className="space-y-4">
        {isLoading ? (
          <LoadingSkeleton />
        ) : error ? (
          <div className="text-center py-8">
            <p className="text-error">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 text-berkeley hover:underline"
            >
              Try again
            </button>
          </div>
        ) : dishes.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <p className="text-lg">No dishes match your profile</p>
            <p className="text-sm mt-2">Try adjusting your dietary preferences</p>
          </div>
        ) : (
          <>
            <h2 className="text-lg font-semibold text-gray-900">
              {selectedHall} - {selectedMeal}
            </h2>
            {categories.map((category) => (
              <CategorySection
                key={category}
                category={category}
                dishes={dishesByCategory[category]}
              />
            ))}
          </>
        )}
      </div>
    </div>
  );
}
