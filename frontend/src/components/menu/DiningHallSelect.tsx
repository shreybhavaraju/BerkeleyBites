import { useApp } from '../../context/AppContext';

export function DiningHallSelect() {
  const { menuSummary, selectedHall, setSelectedHall } = useApp();

  if (!menuSummary || menuSummary.dining_halls.length === 0) {
    return null;
  }

  return (
    <div className="flex items-center gap-3">
      <label htmlFor="dining-hall" className="text-sm font-semibold text-berkeley whitespace-nowrap">
        Dining Hall
      </label>
      <div className="relative">
        <select
          id="dining-hall"
          value={selectedHall}
          onChange={(e) => setSelectedHall(e.target.value)}
          className="appearance-none pl-4 pr-10 py-2.5 bg-slate-warm border border-slate-border rounded-lg text-sm font-medium text-gray-700 focus:outline-none focus:ring-2 focus:ring-berkeley-gold focus:border-transparent cursor-pointer hover:border-berkeley-gold/50 transition-colors"
        >
          {menuSummary.dining_halls.map((hall) => (
            <option key={hall} value={hall}>
              {hall}
            </option>
          ))}
        </select>
        <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
          <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>
    </div>
  );
}
