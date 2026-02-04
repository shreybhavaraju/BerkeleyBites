import { useMenu } from '../../hooks/useMenu';
import { useApp } from '../../context/AppContext';
import { DiningHallSelect } from './DiningHallSelect';
import { MealTabs } from './MealTabs';
import { CategorySection } from './CategorySection';

function LoadingSkeleton() {
  return (
    <div className="space-y-4 animate-pulse">
      {[1, 2, 3].map((i) => (
        <div key={i} className="bg-white rounded-xl p-5 border border-slate-border">
          <div className="h-5 bg-gray-200 rounded-lg w-1/3 mb-4" />
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
      {/* Section header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-berkeley-gold rounded-xl flex items-center justify-center">
          <span className="text-lg">📋</span>
        </div>
        <div>
          <h2 className="text-xl font-bold text-berkeley font-display">Today's Menu</h2>
          <p className="text-gray-500 text-sm">Browse dishes and give feedback</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl p-4 border border-slate-border shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center gap-4">
          <DiningHallSelect />
          <div className="h-8 w-px bg-slate-border hidden sm:block" />
          <MealTabs />
        </div>
      </div>

      {/* Dish count */}
      {menuSummary && dishes.length > 0 && (
        <div className="flex items-center gap-2 px-1">
          <span className="w-2 h-2 bg-success rounded-full" />
          <p className="text-sm text-gray-600">
            <span className="font-semibold text-berkeley">{dishes.length}</span> dishes match your dietary profile
          </p>
        </div>
      )}

      {/* Menu content */}
      <div className="space-y-4">
        {isLoading ? (
          <LoadingSkeleton />
        ) : error ? (
          <div className="text-center py-12 bg-white rounded-2xl border border-slate-border">
            <div className="w-16 h-16 bg-error/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">😕</span>
            </div>
            <p className="text-error font-medium mb-2">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="text-berkeley hover:text-berkeley-light font-medium text-sm"
            >
              Try again →
            </button>
          </div>
        ) : dishes.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-2xl border border-slate-border">
            <div className="w-16 h-16 bg-berkeley-gold/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">🍽️</span>
            </div>
            <h3 className="text-lg font-semibold text-berkeley mb-1">No matches found</h3>
            <p className="text-gray-500 text-sm">Try adjusting your dietary preferences in the profile menu</p>
          </div>
        ) : (
          <>
            {/* Current selection header */}
            <div className="flex items-center gap-2 bg-berkeley/5 px-4 py-3 rounded-xl">
              <span className="text-berkeley-gold">🏛️</span>
              <h2 className="text-lg font-bold text-berkeley font-display">
                {selectedHall}
              </h2>
              <span className="text-gray-400">•</span>
              <span className="text-gray-600 font-medium">{selectedMeal}</span>
            </div>

            {/* Categories */}
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
