// User Profile Types
export interface UserProfile {
  is_vegetarian: boolean;
  is_vegan: boolean;
  is_pescatarian: boolean;
  is_halal: boolean;
  is_kosher: boolean;
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

// Question Types
export interface QuestionOption {
  value: string;
  label: string;
  emoji?: string;
}

export interface QuestionResponse {
  response_type: 'question';
  question_id: string;
  question_text: string;
  options: QuestionOption[];
  session_id: string;
}

// Chat Types
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  agentSummaries?: Record<string, AgentSummary>;
  isRecommendation?: boolean;
  // Question-related fields
  isQuestion?: boolean;
  questionId?: string;
  questionText?: string;
  options?: QuestionOption[];
  answeredValue?: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
}

export interface AgentSummary {
  icon: string;
  title: string;
  points: string[];
}

export interface RecommendationResponse {
  agent_summaries: Record<string, AgentSummary>;
  recommendation: string;
  session_id: string;
}

export type AgentStepStatus = 'pending' | 'loading' | 'complete';

export interface AgentStep {
  id: string;
  label: string;
  status: AgentStepStatus;
}

// API Response Types
export interface ApiError {
  detail: string;
}
