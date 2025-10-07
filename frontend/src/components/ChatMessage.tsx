import React from 'react';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  tokensUsed?: number;
  model?: string;
}

const ChatMessage: React.FC<ChatMessageProps> = ({
  role,
  content,
  timestamp,
  tokensUsed,
  model
}) => {
  const isUser = role === 'user';

  const formatTime = (isoString: string | undefined) => {
    if (!isoString) return '';
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString('es-AR', {
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return '';
    }
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[75%] ${isUser ? 'order-2' : 'order-1'}`}>
        <div
          className={`rounded-lg px-4 py-3 ${
            isUser
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-900 border border-gray-200'
          }`}
        >
          {!isUser && (
            <div className="flex items-center mb-2">
              <span className="text-xl mr-2">🤖</span>
              <span className="text-xs font-semibold text-gray-600">
                CaféBot IA
              </span>
            </div>
          )}
          
          <p className="text-sm whitespace-pre-wrap break-words">{content}</p>
          
          <div className="flex items-center justify-between mt-2 text-xs opacity-75">
            <span>{formatTime(timestamp)}</span>
            
            {!isUser && tokensUsed && tokensUsed > 0 && (
              <span className="ml-2">
                {tokensUsed} tokens
              </span>
            )}
            
            {!isUser && model && (
              <span className="ml-2 italic">
                {model}
              </span>
            )}
          </div>
        </div>
      </div>
      
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-sm font-bold ml-2 order-3">
          U
        </div>
      )}
      
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white text-sm font-bold mr-2 order-0">
          AI
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
