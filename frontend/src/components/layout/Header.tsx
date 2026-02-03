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
          <div className="w-10 h-10 bg-berkeley-gold rounded-full flex items-center justify-center">
            <span className="text-xl">🍽️</span>
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">
              Berkeley<span className="text-berkeley-gold">Bites</span>
            </h1>
            <p className="text-xs text-white/60 -mt-0.5">UC Berkeley Dining</p>
          </div>
        </div>

        <div className="flex items-center gap-6 text-sm">
          {weather && (
            <div className="hidden sm:flex items-center gap-2 bg-white/10 px-3 py-1.5 rounded-full">
              <span className="text-berkeley-gold font-medium">{Math.round(weather.temperature_f)}°F</span>
              <span className="text-white/40">•</span>
              <span className="text-white/90">{weather.conditions}</span>
            </div>
          )}
          <time className="text-white/70 hidden md:block">{today}</time>
        </div>
      </div>
    </header>
  );
}
