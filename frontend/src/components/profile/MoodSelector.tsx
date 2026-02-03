import { useProfile } from '../../hooks/useProfile';
import type { Mood } from '../../types';

const MOOD_EMOJIS: Record<Mood, string> = {
  happy: '😊',
  grumpy: '😤',
  stressed: '😰',
  tired: '😴',
  adventurous: '🤩',
};

export function MoodSelector() {
  const { mood, moodOptions, setMood } = useProfile();

  if (moodOptions.length === 0) {
    return null;
  }

  const currentMoodOption = moodOptions.find((m) => m.value === mood);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-3">
      <select
        value={mood}
        onChange={(e) => setMood(e.target.value as Mood)}
        className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-berkeley focus:border-transparent"
      >
        {moodOptions.map((option) => (
          <option key={option.value} value={option.value}>
            {MOOD_EMOJIS[option.value as Mood] || ''} {option.label}
          </option>
        ))}
      </select>
      {currentMoodOption && (
        <p className="text-gray-500 text-xs mt-2">{currentMoodOption.description}</p>
      )}
    </div>
  );
}
