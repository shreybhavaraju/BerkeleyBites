import type { ChatMessage as ChatMessageType } from '../../types';

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-berkeley text-white'
            : 'bg-gray-100 text-gray-900'
        }`}
      >
        <div className="text-sm whitespace-pre-wrap break-words">{message.content}</div>
      </div>
    </div>
  );
}
