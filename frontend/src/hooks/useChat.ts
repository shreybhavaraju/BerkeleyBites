import { useCallback, useState, useRef, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import {
  sendChatMessage,
  isRecommendationResponse,
  isQuestionResponse,
} from '../api/client';
import type { AgentStep } from '../types';

const INITIAL_AGENT_STEPS: AgentStep[] = [
  { id: 'mood', label: 'Checking your mood', status: 'pending' },
  { id: 'preferences', label: 'Reviewing your taste history', status: 'pending' },
  { id: 'menu', label: 'Finding matching dishes', status: 'pending' },
  { id: 'recommend', label: 'Generating recommendation', status: 'pending' },
];

export function useChat() {
  const {
    chatMessages,
    addChatMessage,
    updateChatMessage,
    clearChat,
    isChatLoading,
    setIsChatLoading,
  } = useApp();

  const [agentSteps, setAgentSteps] = useState<AgentStep[]>([]);
  const [isRecommending, setIsRecommending] = useState(false);
  const animationRef = useRef<ReturnType<typeof setTimeout> | null>(null);

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

      // Add user message
      addChatMessage({ role: 'user', content: message });
      setIsChatLoading(true);

      try {
        const response = await sendChatMessage(message);

        if (isQuestionResponse(response)) {
          // Add question message to chat
          addChatMessage({
            role: 'assistant',
            content: response.question_text,
            isQuestion: true,
            questionId: response.question_id,
            questionText: response.question_text,
            options: response.options,
          });
        } else if (isRecommendationResponse(response)) {
          if (isRecommending) {
            completeAllSteps();
            await new Promise((resolve) => setTimeout(resolve, 300));
          }
          addChatMessage({
            role: 'assistant',
            content: response.recommendation,
            agentSummaries: response.agent_summaries,
            isRecommendation: true,
          });
          setIsRecommending(false);
          setAgentSteps([]);
        } else {
          addChatMessage({ role: 'assistant', content: response.response });
        }
      } catch (err) {
        if (isRecommending) {
          completeAllSteps();
        }
        addChatMessage({
          role: 'assistant',
          content: `Error: ${err instanceof Error ? err.message : 'Failed to get response'}`,
        });
        setIsRecommending(false);
        setAgentSteps([]);
      } finally {
        setIsChatLoading(false);
      }
    },
    [addChatMessage, isChatLoading, setIsChatLoading, isRecommending, completeAllSteps]
  );

  const answerQuestion = useCallback(
    async (questionId: string, value: string) => {
      if (isChatLoading) return;

      // Find and mark the question as answered in chat messages
      const questionIndex = chatMessages.findIndex(
        (msg) => msg.isQuestion && msg.questionId === questionId && !msg.answeredValue
      );

      if (questionIndex !== -1) {
        updateChatMessage(questionIndex, { answeredValue: value });
      }

      // Find the option label for display
      const questionMsg = chatMessages.find(
        (msg) => msg.isQuestion && msg.questionId === questionId
      );
      const selectedOption = questionMsg?.options?.find((opt) => opt.value === value);
      const displayText = selectedOption
        ? `${selectedOption.emoji || ''} ${selectedOption.label}`.trim()
        : value;

      // Add user's answer as a message (visual feedback)
      addChatMessage({ role: 'user', content: displayText });
      setIsChatLoading(true);

      // Start the agent animation after the last question
      // We'll check if this triggers a recommendation
      setIsRecommending(true);
      animateProgress();

      try {
        // Send the answer to backend
        const response = await sendChatMessage(`answer:${questionId}:${value}`);

        if (isQuestionResponse(response)) {
          // Stop the animation - more questions coming
          setIsRecommending(false);
          setAgentSteps([]);

          // Add next question message
          addChatMessage({
            role: 'assistant',
            content: response.question_text,
            isQuestion: true,
            questionId: response.question_id,
            questionText: response.question_text,
            options: response.options,
          });
        } else if (isRecommendationResponse(response)) {
          // Complete animation and show recommendation
          completeAllSteps();
          await new Promise((resolve) => setTimeout(resolve, 300));

          addChatMessage({
            role: 'assistant',
            content: response.recommendation,
            agentSummaries: response.agent_summaries,
            isRecommendation: true,
          });
          setIsRecommending(false);
          setAgentSteps([]);
        } else {
          setIsRecommending(false);
          setAgentSteps([]);
          addChatMessage({ role: 'assistant', content: response.response });
        }
      } catch (err) {
        completeAllSteps();
        setIsRecommending(false);
        setAgentSteps([]);
        addChatMessage({
          role: 'assistant',
          content: `Error: ${err instanceof Error ? err.message : 'Failed to process answer'}`,
        });
      } finally {
        setIsChatLoading(false);
      }
    },
    [addChatMessage, updateChatMessage, chatMessages, isChatLoading, setIsChatLoading, animateProgress, completeAllSteps]
  );

  return {
    messages: chatMessages,
    sendMessage,
    answerQuestion,
    clearChat,
    isLoading: isChatLoading,
    isRecommending,
    agentSteps,
  };
}
