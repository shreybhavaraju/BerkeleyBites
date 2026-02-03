import { useState, useEffect } from 'react';
import { getWeather } from '../../api/client';
import type { Weather } from '../../types';

export function Header() {
  const [weather, setWeather] = useState<Weather | null>(null);
  const today = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  });

  useEffect(() => {
    getWeather()
      .then(setWeather)
      .catch(() => {});
  }, []);

  return (
    <header className="bg-berkeley text-white px-6 py-4 shadow-md">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🍽️</span>
          <h1 className="text-xl font-semibold">BerkeleyBites</h1>
        </div>

        <div className="flex items-center gap-6 text-sm">
          {weather && (
            <div className="hidden sm:flex items-center gap-2 text-white/90">
              <span>{Math.round(weather.temperature_f)}°F</span>
              <span className="text-white/60">|</span>
              <span>{weather.conditions}</span>
            </div>
          )}
          <time className="text-white/80">{today}</time>
        </div>
      </div>
    </header>
  );
}
