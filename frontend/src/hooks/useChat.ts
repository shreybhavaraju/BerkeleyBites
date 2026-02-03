import { useCallback, useState, useRef, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { sendChatMessage, isRecommendationResponse } from '../api/client';
import type { AgentStep } from '../types';

const INITIAL_AGENT_STEPS: AgentStep[] = [
  { id: 'mood', label: 'Checking your mood', status: 'pending' },
  { id: 'weather', label: 'Getting Berkeley weather', status: 'pending' },
  { id: 'preferences', label: 'Reviewing your taste history', status: 'pending' },
  { id: 'menu', label: 'Finding matching dishes', status: 'pending' },
  { id: 'recommend', label: 'Generating recommendation', status: 'pending' },
];

export function useChat() {
  const {
    chatMessages,
    addChatMessage,
    clearChat,
    isChatLoading,
    setIsChatLoading,
  } = useApp();

  const [agentSteps, setAgentSteps] = useState<AgentStep[]>([]);
  const [isRecommending, setIsRecommending] = useState(false);
  const animationRef = useRef<NodeJS.Timeout | null>(null);

  // Cleanup animation on unmount
  useEffect(() => {
    return () => {
      if (animationRef.current) {
        clearTimeout(animationRef.current);
      }
    };
  }, []);

  const animateProgress = useCallback(() => {
    const steps = [...INITIAL_AGENT_STEPS];
    setAgentSteps(steps);

    let currentIndex = 0;

    const advanceStep = () => {
      if (currentIndex < steps.length) {
        setAgentSteps((prev) =>
          prev.map((step, i) => {
            if (i < currentIndex) return { ...step, status: 'complete' as const };
            if (i === currentIndex) return { ...step, status: 'loading' as const };
            return step;
          })
        );
        currentIndex++;
        animationRef.current = setTimeout(advanceStep, 400 + Math.random() * 300);
      }
    };

    advanceStep();
  }, []);

  const completeAllSteps = useCallback(() => {
    if (animationRef.current) {
      clearTimeout(animationRef.current);
    }
    setAgentSteps((prev) =>
      prev.map((step) => ({ ...step, status: 'complete' as const }))
    );
  }, []);

  const sendMessage = useCallback(
    async (message: string) => {
      if (!message.trim() || isChatLoading) return;

      const isRecommendCommand = message.trim().toLowerCase().startsWith('/recommend');

      // Add user message
      addChatMessage({ role: 'user', content: message });
      setIsChatLoading(true);

      if (isRecommendCommand) {
        setIsRecommending(true);
        animateProgress();
      }

      try {
        const response = await sendChatMessage(message);

        if (isRecommendCommand) {
          completeAllSteps();
          // Small delay to show completed state
          await new Promise((resolve) => setTimeout(resolve, 300));
        }

        if (isRecommendationResponse(response)) {
          addChatMessage({
            role: 'assistant',
            content: response.recommendation,
            agentSummaries: response.agent_summaries,
            isRecommendation: true,
          });
        } else {
          addChatMessage({ role: 'assistant', content: response.response });
        }
      } catch (err) {
        if (isRecommendCommand) {
          completeAllSteps();
        }
        addChatMessage({
          role: 'assistant',
          content: `Error: ${err instanceof Error ? err.message : 'Failed to get response'}`,
        });
      } finally {
        setIsChatLoading(false);
        setIsRecommending(false);
        setAgentSteps([]);
      }
    },
    [addChatMessage, isChatLoading, setIsChatLoading, animateProgress, completeAllSteps]
  );

  return {
    messages: chatMessages,
    sendMessage,
    clearChat,
    isLoading: isChatLoading,
    isRecommending,
    agentSteps,
  };
}
