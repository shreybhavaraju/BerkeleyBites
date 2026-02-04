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
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  }, [messages, agentSteps]);

  return (
    <div className="bg-white rounded-2xl overflow-hidden shadow-lg border border-slate-border">
      {/* Header */}
      <div className="relative bg-berkeley px-5 py-4">
        {/* Decorative pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 right-0 w-32 h-32 bg-berkeley-gold rounded-full -translate-y-1/2 translate-x-1/2" />
          <div className="absolute bottom-0 left-0 w-24 h-24 bg-berkeley-gold rounded-full translate-y-1/2 -translate-x-1/2" />
        </div>

        <div className="relative flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-berkeley-gold rounded-xl flex items-center justify-center shadow-md animate-pulse-gold">
              <span className="text-lg">🤖</span>
            </div>
            <div>
              <h3 className="font-bold text-white font-display text-lg">AI Food Assistant</h3>
              <p className="text-white/60 text-xs">Personalized recommendations just for you</p>
            </div>
          </div>
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 bg-white/10 rounded-full">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span className="text-white/80 text-xs font-medium">Online</span>
          </div>
        </div>
      </div>

      {/* Messages area */}
      <div
        ref={messagesContainerRef}
        className="h-80 overflow-y-auto p-5 space-y-4 bg-gradient-to-b from-slate-warm to-white"
      >
        {messages.length === 0 && !isRecommending ? (
          <div className="text-center py-10">
            <div className="w-16 h-16 bg-berkeley/5 rounded-2xl flex items-center justify-center mx-auto mb-4 border-2 border-dashed border-berkeley/20">
              <span className="text-3xl">💬</span>
            </div>
            <h4 className="font-semibold text-berkeley font-display text-lg mb-1">
              What are you craving?
            </h4>
            <p className="text-gray-500 text-sm mb-4">
              Ask me for personalized food recommendations!
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              <button
                onClick={() => sendMessage('/recommend')}
                className="px-4 py-2 bg-berkeley text-white text-sm font-medium rounded-lg hover:bg-berkeley-light transition-colors"
              >
                Get Recommendations
              </button>
              <button
                onClick={() => sendMessage('/help')}
                className="px-4 py-2 bg-berkeley-gold/20 text-berkeley text-sm font-medium rounded-lg hover:bg-berkeley-gold/30 transition-colors"
              >
                See Commands
              </button>
            </div>
          </div>
        ) : (
          messages.map((message, index) => {
            if (message.role === 'assistant' && message.isRecommendation && message.agentSummaries) {
              return (
                <div key={index} className="flex justify-start animate-fade-in">
                  <div className="max-w-[95%]">
                    <RecommendationMessage
                      agentSummaries={message.agentSummaries}
                      recommendation={message.content}
                    />
                  </div>
                </div>
              );
            }

            if (message.role === 'assistant' && message.isQuestion && message.questionId && message.options) {
              return (
                <div key={index} className="flex justify-start animate-fade-in">
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

            return <ChatMessage key={index} message={message} />;
          })
        )}

        {/* Agent progress */}
        {isRecommending && agentSteps.length > 0 && (
          <div className="flex justify-start animate-fade-in">
            <div className="max-w-[85%]">
              <AgentProgress steps={agentSteps} />
            </div>
          </div>
        )}

        {/* Simple loading */}
        {isLoading && !isRecommending && (
          <div className="flex justify-start">
            <div className="bg-white rounded-xl px-4 py-3 shadow-sm border border-slate-border">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 bg-berkeley-gold rounded-full animate-bounce" />
                <span
                  className="w-2.5 h-2.5 bg-berkeley-gold rounded-full animate-bounce"
                  style={{ animationDelay: '0.15s' }}
                />
                <span
                  className="w-2.5 h-2.5 bg-berkeley-gold rounded-full animate-bounce"
                  style={{ animationDelay: '0.3s' }}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input area */}
      <div className="p-4 border-t border-slate-border bg-white">
        <ChatInput onSend={sendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
}
