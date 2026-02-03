import { useCallback } from 'react';
import { useApp } from '../context/AppContext';
import { sendChatMessage } from '../api/client';

export function useChat() {
  const {
    chatMessages,
    addChatMessage,
    clearChat,
    isChatLoading,
    setIsChatLoading,
  } = useApp();

  const sendMessage = useCallback(
    async (message: string) => {
      if (!message.trim() || isChatLoading) return;

      // Add user message
      addChatMessage({ role: 'user', content: message });
      setIsChatLoading(true);

      try {
        const response = await sendChatMessage(message);
        addChatMessage({ role: 'assistant', content: response.response });
      } catch (err) {
        addChatMessage({
          role: 'assistant',
          content: `Error: ${err instanceof Error ? err.message : 'Failed to get response'}`,
        });
      } finally {
        setIsChatLoading(false);
      }
    },
    [addChatMessage, isChatLoading, setIsChatLoading]
  );

  return {
    messages: chatMessages,
    sendMessage,
    clearChat,
    isLoading: isChatLoading,
  };
}
