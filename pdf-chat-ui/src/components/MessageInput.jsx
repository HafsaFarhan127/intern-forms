import React, { useState, useRef } from 'react';
import { Send, Mic, Paperclip } from 'lucide-react';

const MessageInput = ({ onSendMessage, disabled }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message);
      setMessage('');
      textareaRef.current?.focus();
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleTextareaChange = (e) => {
    setMessage(e.target.value);
    
    // Auto-resize textarea
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  };

  // Sample questions for quick access
  const sampleQuestions = [
    "What forms do I need to fill out?",
    "What is the deadline for submission?",
    "What documents are required?",
    "How do I contact support?",
    "What are the eligibility requirements?"
  ];

  return (
    <div className="space-y-3">
      {/* Sample Questions */}
      <div className="flex flex-wrap gap-2">
        {sampleQuestions.map((question, index) => (
          <button
            key={index}
            onClick={() => {
              setMessage(question);
              textareaRef.current?.focus();
            }}
            className="text-xs px-3 py-1 bg-blue-50 text-blue-700 rounded-full hover:bg-blue-100 transition-colors duration-200 border border-blue-200"
            disabled={disabled}
          >
            {question}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="flex items-end space-x-3">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleTextareaChange}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about your PDF documents..."
            className="w-full resize-none rounded-lg border border-gray-300 px-4 py-3 pr-12 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 disabled:opacity-50 disabled:cursor-not-allowed"
            rows="1"
            disabled={disabled}
            style={{ minHeight: '48px', maxHeight: '120px' }}
          />
          
          {/* Additional Actions */}
          <div className="absolute right-2 bottom-2 flex space-x-1">
            <button
              type="button"
              className="p-1 text-gray-400 hover:text-gray-600 transition-colors duration-200"
              disabled={disabled}
              title="Attach file (coming soon)"
            >
              <Paperclip className="h-4 w-4" />
            </button>
            <button
              type="button"
              className="p-1 text-gray-400 hover:text-gray-600 transition-colors duration-200"
              disabled={disabled}
              title="Voice input (coming soon)"
            >
              <Mic className="h-4 w-4" />
            </button>
          </div>
        </div>
        
        <button
          type="submit"
          disabled={!message.trim() || disabled}
          className="flex items-center justify-center w-12 h-12 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
        >
          <Send className="h-5 w-5" />
        </button>
      </form>

      {/* Status indicator */}
      {disabled && (
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
          <span>Processing your request...</span>
        </div>
      )}
    </div>
  );
};

export default MessageInput;