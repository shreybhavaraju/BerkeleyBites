import { useApp } from '../../context/AppContext';

export function MealTabs() {
  const { menuSummary, selectedMeal, setSelectedMeal } = useApp();

  if (!menuSummary || menuSummary.meal_periods.length === 0) {
    return null;
  }

  return (
    <div className="flex gap-1 bg-gray-100 rounded-lg p-1 overflow-x-auto">
      {menuSummary.meal_periods.map((meal) => (
        <button
          key={meal}
          onClick={() => setSelectedMeal(meal)}
          className={`px-3 sm:px-4 py-2 text-sm font-medium rounded-md transition-colors whitespace-nowrap ${
            selectedMeal === meal
              ? 'bg-white text-berkeley shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          {meal}
        </button>
      ))}
    </div>
  );
}
