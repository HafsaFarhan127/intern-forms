import React from 'react';

const TypingIndicator = () => {
  return (
    <div className="flex items-center space-x-1">
      <span className="text-sm text-gray-500">Thinking</span>
      <div className="typing-indicator">
        <div className="typing-dot"></div>
        <div className="typing-dot"></div>
        <div className="typing-dot"></div>
      </div>
    </div>
  );
};

export default TypingIndicator;