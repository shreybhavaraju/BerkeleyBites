import { useRef, useEffect } from 'react';
import { useChat } from '../../hooks/useChat';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { AgentProgress } from './AgentProgress';
import { RecommendationMessage } from './RecommendationMessage';
import { QuestionMessage } from './QuestionMessage';

export function ChatPanel() {
  const { messages, sendMessage, answerQuestion, isLoading, isRecommending, agentSteps } = useChat();
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Scroll within the chat container only, not the entire page
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  }, [messages, agentSteps]);

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden shadow-sm">
      <div className="px-4 py-3 bg-berkeley border-b border-berkeley-light">
        <h3 className="font-medium text-white flex items-center gap-2">
          <span className="w-6 h-6 bg-berkeley-gold rounded-full flex items-center justify-center text-sm">
            🤖
          </span>
          <span>AI Assistant</span>
          <span className="text-xs text-white/60 font-normal ml-auto">Powered by Perplexity</span>
        </h3>
      </div>

      {/* Messages area */}
      <div ref={messagesContainerRef} className="h-80 overflow-y-auto p-4 space-y-3 bg-gray-50/50">
        {messages.length === 0 && !isRecommending ? (
          <div className="text-center py-8">
            <div className="w-12 h-12 bg-berkeley/10 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-2xl">💬</span>
            </div>
            <p className="text-sm text-gray-600">Ask me for personalized food recommendations!</p>
            <p className="text-xs mt-2 text-gray-400">
              Try: <span className="font-mono bg-berkeley/10 px-1.5 py-0.5 rounded text-berkeley">/recommend lunch</span>
            </p>
          </div>
        ) : (
          messages.map((message, index) => {
            // Render recommendation messages
            if (message.role === 'assistant' && message.isRecommendation && message.agentSummaries) {
              return (
                <div key={index} className="flex justify-start">
                  <div className="max-w-[95%]">
                    <RecommendationMessage
                      agentSummaries={message.agentSummaries}
                      recommendation={message.content}
                    />
                  </div>
                </div>
              );
            }

            // Render question messages
            if (message.role === 'assistant' && message.isQuestion && message.questionId && message.options) {
              return (
                <div key={index} className="flex justify-start">
                  <div className="max-w-[85%]">
                    <QuestionMessage
                      questionId={message.questionId}
                      questionText={message.questionText || message.content}
                      options={message.options}
                      onAnswer={answerQuestion}
                      disabled={isLoading}
                      answeredValue={message.answeredValue}
                    />
                  </div>
                </div>
              );
            }

            // Render regular chat messages
            return <ChatMessage key={index} message={message} />;
          })
        )}

        {/* Show agent progress animation during /recommend */}
        {isRecommending && agentSteps.length > 0 && (
          <div className="flex justify-start">
            <div className="max-w-[85%]">
              <AgentProgress steps={agentSteps} />
            </div>
          </div>
        )}

        {/* Show simple loading for non-recommend commands */}
        {isLoading && !isRecommending && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-lg px-4 py-2 shadow-sm">
              <div className="flex items-center gap-1">
                <span className="w-2 h-2 bg-berkeley-gold rounded-full animate-bounce" />
                <span
                  className="w-2 h-2 bg-berkeley-gold rounded-full animate-bounce"
                  style={{ animationDelay: '0.1s' }}
                />
                <span
                  className="w-2 h-2 bg-berkeley-gold rounded-full animate-bounce"
                  style={{ animationDelay: '0.2s' }}
                />
              </div>
            </div>
          </div>
        )}

      </div>

      {/* Input area */}
      <div className="p-4 border-t border-gray-200 bg-white">
        <ChatInput onSend={sendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
}
