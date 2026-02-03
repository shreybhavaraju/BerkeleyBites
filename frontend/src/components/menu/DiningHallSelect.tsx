import { useApp } from '../../context/AppContext';

export function DiningHallSelect() {
  const { menuSummary, selectedHall, setSelectedHall } = useApp();

  if (!menuSummary || menuSummary.dining_halls.length === 0) {
    return null;
  }

  return (
    <div className="flex items-center gap-2">
      <label htmlFor="dining-hall" className="text-sm font-medium text-gray-700">
        🏛️ Dining Hall:
      </label>
      <select
        id="dining-hall"
        value={selectedHall}
        onChange={(e) => setSelectedHall(e.target.value)}
        className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-berkeley focus:border-transparent bg-white"
      >
        {menuSummary.dining_halls.map((hall) => (
          <option key={hall} value={hall}>
            {hall}
          </option>
        ))}
      </select>
    </div>
  );
}
