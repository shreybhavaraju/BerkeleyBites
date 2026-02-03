import type {
  UserProfile,
  Dish,
  MenuSummary,
  FeedbackStats,
  DishFeedback,
  ChatResponse,
  Weather,
  MoodOption,
} from '../types';

const API_BASE = '/api';

// Helper function for API calls
async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `API error: ${response.status}`);
  }

  return response.json();
}

// Get user ID from localStorage
export function getUserId(): string {
  let userId = localStorage.getItem('berkeleyBitesUserId');
  if (!userId) {
    userId = `user_${Math.random().toString(36).substring(2, 10)}`;
    localStorage.setItem('berkeleyBitesUserId', userId);
  }
  return userId;
}

// Menu API
export async function getMenu(
  hall?: string,
  meal?: string,
  category?: string
): Promise<Dish[]> {
  const params = new URLSearchParams({ user_id: getUserId() });
  if (hall) params.set('hall', hall);
  if (meal) params.set('meal', meal);
  if (category) params.set('category', category);

  return fetchApi<Dish[]>(`/menu?${params}`);
}

export async function getMenuSummary(): Promise<MenuSummary> {
  return fetchApi<MenuSummary>(`/menu/summary?user_id=${getUserId()}`);
}

export async function refreshMenu(): Promise<{ success: boolean; message: string }> {
  return fetchApi<{ success: boolean; message: string }>('/menu/refresh', {
    method: 'POST',
  });
}

// Profile API
export async function getProfile(): Promise<UserProfile> {
  return fetchApi<UserProfile>(`/profile?user_id=${getUserId()}`);
}

export async function updateProfile(profile: UserProfile): Promise<UserProfile> {
  return fetchApi<UserProfile>(`/profile?user_id=${getUserId()}`, {
    method: 'PUT',
    body: JSON.stringify(profile),
  });
}

export async function getMood(): Promise<{
  current_mood: string;
  available_moods: MoodOption[];
}> {
  return fetchApi(`/profile/mood?user_id=${getUserId()}`);
}

export async function updateMood(mood: string): Promise<{
  mood: string;
  description: string;
  food_suggestion: string;
}> {
  return fetchApi(`/profile/mood?user_id=${getUserId()}`, {
    method: 'PUT',
    body: JSON.stringify({ mood }),
  });
}

// Feedback API
export async function submitFeedback(
  dishId: number,
  dishName: string,
  liked: boolean
): Promise<{ success: boolean }> {
  return fetchApi<{ success: boolean }>(`/feedback?user_id=${getUserId()}`, {
    method: 'POST',
    body: JSON.stringify({
      dish_id: dishId,
      dish_name: dishName,
      liked,
    }),
  });
}

export async function getFeedbackStats(): Promise<FeedbackStats> {
  return fetchApi<FeedbackStats>(`/feedback/stats?user_id=${getUserId()}`);
}

export async function getDishFeedback(dishId: number): Promise<DishFeedback> {
  return fetchApi<DishFeedback>(`/feedback/${dishId}?user_id=${getUserId()}`);
}

// Chat API
export async function sendChatMessage(message: string): Promise<ChatResponse> {
  return fetchApi<ChatResponse>(`/chat?user_id=${getUserId()}`, {
    method: 'POST',
    body: JSON.stringify({
      message,
      session_id: getUserId(),
    }),
  });
}

// Weather API
export async function getWeather(): Promise<Weather> {
  return fetchApi<Weather>('/weather');
}

// Health Check
export async function healthCheck(): Promise<{
  status: string;
  date: string;
  menu_loaded: boolean;
  dish_count: number;
}> {
  return fetchApi('/health');
}
