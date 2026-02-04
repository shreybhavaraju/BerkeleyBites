import { useState } from 'react';
import { useProfile } from '../../hooks/useProfile';
import type { UserProfile } from '../../types';

interface CheckboxItemProps {
  label: string;
  emoji: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
}

function CheckboxItem({ label, emoji, checked, onChange, disabled }: CheckboxItemProps) {
  return (
    <label className={`flex items-center gap-3 cursor-pointer p-2 rounded-lg hover:bg-slate-warm transition-colors ${disabled ? 'opacity-50' : ''}`}>
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        disabled={disabled}
        className="w-4 h-4 text-berkeley rounded border-slate-border focus:ring-berkeley-gold focus:ring-2 cursor-pointer"
      />
      <span className="text-sm flex items-center gap-2">
        <span>{emoji}</span>
        <span className="text-gray-700">{label}</span>
      </span>
    </label>
  );
}

export function ProfileEditor() {
  const { profile, setProfile, isLoading } = useProfile();
  const [isOpen, setIsOpen] = useState(false);

  const handleChange = async <K extends keyof UserProfile>(
    field: K,
    value: UserProfile[K]
  ) => {
    await setProfile({ ...profile, [field]: value });
  };

  return (
    <div className="mt-3">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 text-sm font-semibold text-berkeley hover:text-berkeley-light transition-colors"
      >
        <svg className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-90' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
        <span>Edit Preferences</span>
      </button>

      {isOpen && (
        <div className={`mt-3 space-y-4 animate-fade-in ${isLoading ? 'opacity-50 pointer-events-none' : ''}`}>
          {/* Dietary Identity */}
          <div>
            <h4 className="text-xs font-bold text-berkeley uppercase tracking-wider mb-2 flex items-center gap-2">
              <span className="w-1 h-3 bg-berkeley-gold rounded-full" />
              Dietary Identity
            </h4>
            <div className="space-y-1 bg-white rounded-lg border border-slate-border p-1">
              <CheckboxItem
                label="Vegan"
                emoji="🌱"
                checked={profile.is_vegan}
                onChange={(v) => handleChange('is_vegan', v)}
              />
              <CheckboxItem
                label="Vegetarian"
                emoji="🥗"
                checked={profile.is_vegetarian}
                onChange={(v) => handleChange('is_vegetarian', v)}
              />
              <CheckboxItem
                label="Pescatarian"
                emoji="🐟"
                checked={profile.is_pescatarian}
                onChange={(v) => handleChange('is_pescatarian', v)}
              />
              <CheckboxItem
                label="Halal"
                emoji="☪️"
                checked={profile.is_halal}
                onChange={(v) => handleChange('is_halal', v)}
              />
              <CheckboxItem
                label="Kosher"
                emoji="✡️"
                checked={profile.is_kosher}
                onChange={(v) => handleChange('is_kosher', v)}
              />
            </div>
          </div>

          {/* Allergens */}
          <div>
            <h4 className="text-xs font-bold text-berkeley uppercase tracking-wider mb-2 flex items-center gap-2">
              <span className="w-1 h-3 bg-error rounded-full" />
              Allergens to Avoid
            </h4>
            <div className="space-y-1 bg-white rounded-lg border border-slate-border p-1">
              <CheckboxItem
                label="Dairy/Milk"
                emoji="🥛"
                checked={profile.avoid_milk}
                onChange={(v) => handleChange('avoid_milk', v)}
              />
              <CheckboxItem
                label="Eggs"
                emoji="🥚"
                checked={profile.avoid_eggs}
                onChange={(v) => handleChange('avoid_eggs', v)}
              />
              <CheckboxItem
                label="Gluten"
                emoji="🌾"
                checked={profile.avoid_gluten}
                onChange={(v) => handleChange('avoid_gluten', v)}
              />
              <CheckboxItem
                label="Nuts"
                emoji="🥜"
                checked={profile.avoid_nuts}
                onChange={(v) => handleChange('avoid_nuts', v)}
              />
              <CheckboxItem
                label="Soy"
                emoji="🫘"
                checked={profile.avoid_soy}
                onChange={(v) => handleChange('avoid_soy', v)}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
