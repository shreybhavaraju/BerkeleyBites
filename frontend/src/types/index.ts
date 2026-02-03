// User Profile Types
export interface UserProfile {
  is_vegetarian: boolean;
  is_vegan: boolean;
  is_pescatarian: boolean;
  is_halal: boolean;
  is_kosher: boolean;
  eats_chicken: boolean;
  eats_beef: boolean;
  eats_pork: boolean;
  eats_fish: boolean;
  eats_shellfish: boolean;
  avoid_milk: boolean;
  avoid_eggs: boolean;
  avoid_gluten: boolean;
  avoid_nuts: boolean;
  avoid_soy: boolean;
  prefer_low_carbon: boolean;
}

export const DEFAULT_PROFILE: UserProfile = {
  is_vegetarian: false,
  is_vegan: false,
  is_pescatarian: false,
  is_halal: false,
  is_kosher: false,
  eats_chicken: true,
  eats_beef: true,
  eats_pork: true,
  eats_fish: true,
  eats_shellfish: true,
  avoid_milk: false,
  avoid_eggs: false,
  avoid_gluten: false,
  avoid_nuts: false,
  avoid_soy: false,
  prefer_low_carbon: false,
};

// Mood Types
export type Mood = 'happy' | 'grumpy' | 'stressed' | 'tired' | 'adventurous';

export interface MoodOption {
  value: Mood;
  label: string;
  description: string;
}

// Menu Types
export interface Dish {
  dish_id: number;
  dish_name: string;
  dining_hall: string;
  dining_hall_status: string;
  meal_period: string;
  category: string;
  has_milk: boolean;
  has_egg: boolean;
  has_fish: boolean;
  has_shellfish: boolean;
  has_tree_nuts: boolean;
  has_wheat: boolean;
  has_peanuts: boolean;
  has_soybeans: boolean;
  has_sesame: boolean;
  has_gluten: boolean;
  is_vegan: boolean;
  is_vegetarian: boolean;
  is_halal: boolean;
  is_kosher: boolean;
  has_pork: boolean;
  has_alcohol: boolean;
  scrape_date: string;
}

export interface MenuSummary {
  total_dishes: number;
  dining_halls: string[];
  meal_periods: string[];
  categories: string[];
  vegan_count: number;
  vegetarian_count: number;
  halal_count: number;
}

// Feedback Types
export interface FeedbackStats {
  total_ratings: number;
  liked_count: number;
  disliked_count: number;
  today_ratings: number;
}

export interface DishFeedback {
  feedback: boolean | null;
}

// Chat Types
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
}

// Weather Types
export interface Weather {
  temperature_f: number;
  conditions: string;
  food_suggestion: string;
}

// API Response Types
export interface ApiError {
  detail: string;
}
