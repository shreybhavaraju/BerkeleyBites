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
    <label className={`flex items-center gap-2 cursor-pointer ${disabled ? 'opacity-50' : ''}`}>
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        disabled={disabled}
        className="w-4 h-4 text-berkeley rounded border-gray-300 focus:ring-berkeley"
      />
      <span className="text-sm">
        {emoji} {label}
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

  const isVegetarianLike = profile.is_vegetarian || profile.is_vegan;

  return (
    <div className="mt-3">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 text-sm text-berkeley hover:text-berkeley-light transition-colors"
      >
        <span className="text-lg">{isOpen ? '▼' : '▶'}</span>
        <span>Edit Profile</span>
      </button>

      {isOpen && (
        <div className={`mt-3 space-y-4 ${isLoading ? 'opacity-50 pointer-events-none' : ''}`}>
          {/* Dietary Identity */}
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">
              Dietary Identity
            </h4>
            <div className="space-y-2">
              <CheckboxItem
                label="Vegan (no animal products)"
                emoji="🌱"
                checked={profile.is_vegan}
                onChange={(v) => handleChange('is_vegan', v)}
              />
              <CheckboxItem
                label="Vegetarian (no meat/fish)"
                emoji="🥗"
                checked={profile.is_vegetarian}
                onChange={(v) => handleChange('is_vegetarian', v)}
              />
              <CheckboxItem
                label="Pescatarian (fish OK)"
                emoji="🐟"
                checked={profile.is_pescatarian}
                onChange={(v) => handleChange('is_pescatarian', v)}
              />
              <CheckboxItem
                label="Halal only"
                emoji="☪️"
                checked={profile.is_halal}
                onChange={(v) => handleChange('is_halal', v)}
              />
              <CheckboxItem
                label="Kosher only"
                emoji="✡️"
                checked={profile.is_kosher}
                onChange={(v) => handleChange('is_kosher', v)}
              />
            </div>
          </div>

          {/* Specific Meats */}
          {!isVegetarianLike && (
            <div>
              <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">
                Meats You Eat
              </h4>
              <div className="space-y-2">
                <CheckboxItem
                  label="Chicken"
                  emoji="🍗"
                  checked={profile.eats_chicken}
                  onChange={(v) => handleChange('eats_chicken', v)}
                />
                <CheckboxItem
                  label="Beef"
                  emoji="🥩"
                  checked={profile.eats_beef}
                  onChange={(v) => handleChange('eats_beef', v)}
                />
                <CheckboxItem
                  label="Pork"
                  emoji="🥓"
                  checked={profile.eats_pork}
                  onChange={(v) => handleChange('eats_pork', v)}
                />
                <CheckboxItem
                  label="Fish"
                  emoji="🐟"
                  checked={profile.eats_fish}
                  onChange={(v) => handleChange('eats_fish', v)}
                />
                <CheckboxItem
                  label="Shellfish"
                  emoji="🦐"
                  checked={profile.eats_shellfish}
                  onChange={(v) => handleChange('eats_shellfish', v)}
                />
              </div>
            </div>
          )}

          {/* Allergens */}
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">
              Allergens to Avoid
            </h4>
            <div className="space-y-2">
              <CheckboxItem
                label="Dairy/milk"
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
