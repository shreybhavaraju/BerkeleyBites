import { useState, useEffect, useCallback } from 'react';
import type { Dish } from '../types';
import { getMenu } from '../api/client';
import { useApp } from '../context/AppContext';

export function useMenu() {
  const { selectedHall, selectedMeal, profile } = useApp();
  const [dishes, setDishes] = useState<Dish[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDishes = useCallback(async () => {
    if (!selectedHall || !selectedMeal) return;

    setIsLoading(true);
    setError(null);

    try {
      const data = await getMenu(selectedHall, selectedMeal);
      setDishes(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dishes');
      setDishes([]);
    } finally {
      setIsLoading(false);
    }
  }, [selectedHall, selectedMeal]);

  useEffect(() => {
    fetchDishes();
  }, [fetchDishes, profile]);

  // Group dishes by category
  const dishesByCategory = dishes.reduce<Record<string, Dish[]>>((acc, dish) => {
    if (!acc[dish.category]) {
      acc[dish.category] = [];
    }
    acc[dish.category].push(dish);
    return acc;
  }, {});

  return {
    dishes,
    dishesByCategory,
    isLoading,
    error,
    refetch: fetchDishes,
  };
}
