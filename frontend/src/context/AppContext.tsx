import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from 'react';
import type {
  UserProfile,
  MenuSummary,
  FeedbackStats,
  Mood,
  MoodOption,
  ChatMessage,
} from '../types';
import { DEFAULT_PROFILE } from '../types';
import * as api from '../api/client';

interface AppState {
  // Profile
  profile: UserProfile;
  setProfile: (profile: UserProfile) => Promise<void>;
  isProfileLoading: boolean;

  // Mood
  mood: Mood;
  moodOptions: MoodOption[];
  setMood: (mood: Mood) => Promise<void>;

  // Menu
  menuSummary: MenuSummary | null;
  selectedHall: string;
  selectedMeal: string;
  setSelectedHall: (hall: string) => void;
  setSelectedMeal: (meal: string) => void;
  refreshMenuSummary: () => Promise<void>;

  // Feedback
  feedbackStats: FeedbackStats | null;
  refreshFeedbackStats: () => Promise<void>;

  // Chat
  chatMessages: ChatMessage[];
  addChatMessage: (message: ChatMessage) => void;
  clearChat: () => void;
  isChatLoading: boolean;
  setIsChatLoading: (loading: boolean) => void;

  // General
  isLoading: boolean;
  error: string | null;
}

const AppContext = createContext<AppState | undefined>(undefined);

const PROFILE_STORAGE_KEY = 'berkeleyBitesProfile';
const MOOD_STORAGE_KEY = 'berkeleyBitesMood';

export function AppProvider({ children }: { children: ReactNode }) {
  // Profile state
  const [profile, setProfileState] = useState<UserProfile>(() => {
    const stored = localStorage.getItem(PROFILE_STORAGE_KEY);
    return stored ? JSON.parse(stored) : DEFAULT_PROFILE;
  });
  const [isProfileLoading, setIsProfileLoading] = useState(false);

  // Mood state
  const [mood, setMoodState] = useState<Mood>(() => {
    return (localStorage.getItem(MOOD_STORAGE_KEY) as Mood) || 'happy';
  });
  const [moodOptions, setMoodOptions] = useState<MoodOption[]>([]);

  // Menu state
  const [menuSummary, setMenuSummary] = useState<MenuSummary | null>(null);
  const [selectedHall, setSelectedHall] = useState<string>('');
  const [selectedMeal, setSelectedMeal] = useState<string>('');

  // Feedback state
  const [feedbackStats, setFeedbackStats] = useState<FeedbackStats | null>(null);

  // Chat state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [isChatLoading, setIsChatLoading] = useState(false);

  // General state
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load initial data
  useEffect(() => {
    async function loadInitialData() {
      setIsLoading(true);
      try {
        // Load menu summary
        const summary = await api.getMenuSummary();
        setMenuSummary(summary);

        // Set defaults for hall/meal if available
        if (summary.dining_halls.length > 0 && !selectedHall) {
          setSelectedHall(summary.dining_halls[0]);
        }
        if (summary.meal_periods.length > 0 && !selectedMeal) {
          setSelectedMeal(summary.meal_periods[0]);
        }

        // Load mood options
        const moodData = await api.getMood();
        setMoodOptions(moodData.available_moods);

        // Load feedback stats
        const stats = await api.getFeedbackStats();
        setFeedbackStats(stats);

        // Sync profile to backend
        await api.updateProfile(profile);
        await api.updateMood(mood);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setIsLoading(false);
      }
    }

    loadInitialData();
  }, []);

  // Profile methods
  const setProfile = useCallback(async (newProfile: UserProfile) => {
    setIsProfileLoading(true);
    try {
      await api.updateProfile(newProfile);
      setProfileState(newProfile);
      localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(newProfile));

      // Refresh menu summary since it depends on profile
      const summary = await api.getMenuSummary();
      setMenuSummary(summary);
    } finally {
      setIsProfileLoading(false);
    }
  }, []);

  // Mood methods
  const setMood = useCallback(async (newMood: Mood) => {
    await api.updateMood(newMood);
    setMoodState(newMood);
    localStorage.setItem(MOOD_STORAGE_KEY, newMood);
  }, []);

  // Menu methods
  const refreshMenuSummary = useCallback(async () => {
    const summary = await api.getMenuSummary();
    setMenuSummary(summary);
  }, []);

  // Feedback methods
  const refreshFeedbackStats = useCallback(async () => {
    const stats = await api.getFeedbackStats();
    setFeedbackStats(stats);
  }, []);

  // Chat methods
  const addChatMessage = useCallback((message: ChatMessage) => {
    setChatMessages((prev) => [...prev, message]);
  }, []);

  const clearChat = useCallback(() => {
    setChatMessages([]);
  }, []);

  const value: AppState = {
    profile,
    setProfile,
    isProfileLoading,
    mood,
    moodOptions,
    setMood,
    menuSummary,
    selectedHall,
    selectedMeal,
    setSelectedHall,
    setSelectedMeal,
    refreshMenuSummary,
    feedbackStats,
    refreshFeedbackStats,
    chatMessages,
    addChatMessage,
    clearChat,
    isChatLoading,
    setIsChatLoading,
    isLoading,
    error,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}
