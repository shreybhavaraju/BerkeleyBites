import { useCallback } from 'react';
import type { UserProfile } from '../types';
import { useApp } from '../context/AppContext';

export function useProfile() {
  const { profile, setProfile, isProfileLoading } = useApp();

  const updateProfileField = useCallback(
    async <K extends keyof UserProfile>(field: K, value: UserProfile[K]) => {
      const newProfile = { ...profile, [field]: value };
      await setProfile(newProfile);
    },
    [profile, setProfile]
  );

  // Generate profile summary text
  const getProfileSummary = useCallback((): string[] => {
    const summary: string[] = [];

    if (profile.is_vegan) {
      summary.push('Vegan');
    } else if (profile.is_vegetarian) {
      summary.push('Vegetarian');
    } else if (profile.is_pescatarian) {
      summary.push('Pescatarian');
    }

    if (profile.is_halal) summary.push('Halal');
    if (profile.is_kosher) summary.push('Kosher');

    const allergens: string[] = [];
    if (profile.avoid_milk) allergens.push('dairy');
    if (profile.avoid_eggs) allergens.push('eggs');
    if (profile.avoid_gluten) allergens.push('gluten');
    if (profile.avoid_nuts) allergens.push('nuts');
    if (profile.avoid_soy) allergens.push('soy');

    if (allergens.length > 0) {
      summary.push(`Avoids: ${allergens.join(', ')}`);
    }

    return summary;
  }, [profile]);

  return {
    profile,
    setProfile,
    updateProfileField,
    isLoading: isProfileLoading,
    getProfileSummary,
  };
}
