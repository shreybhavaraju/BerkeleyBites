import { useApp } from '../../context/AppContext';

export function MealTabs() {
  const { menuSummary, selectedMeal, setSelectedMeal } = useApp();

  if (!menuSummary || menuSummary.meal_periods.length === 0) {
    return null;
  }

  return (
    <div className="flex gap-1 bg-slate-warm rounded-lg p-1 overflow-x-auto">
      {menuSummary.meal_periods.map((meal) => (
        <button
          key={meal}
          onClick={() => setSelectedMeal(meal)}
          className={`px-4 py-2 text-sm font-semibold rounded-md transition-all whitespace-nowrap ${
            selectedMeal === meal
              ? 'bg-berkeley text-white shadow-md'
              : 'text-gray-600 hover:text-berkeley hover:bg-white/50'
          }`}
        >
          {meal}
        </button>
      ))}
    </div>
  );
}
