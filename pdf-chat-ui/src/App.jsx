import React, { useState, useRef, useEffect } from 'react';
import { Send, FileText, Bot, User, AlertCircle } from 'lucide-react';
import Message from './components/Message';
import MessageInput from './components/MessageInput';
import TypingIndicator from './components/TypingIndicator';
import { queryPDFSystem } from './services/pdfApi';

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: "Hello! I'm your PDF Document Assistant. I can help you find information from your uploaded PDF documents. What would you like to know?",
      timestamp: new Date().toISOString(),
      metadata: null
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSendMessage = async (message) => {
    if (!message.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date().toISOString(),
      metadata: null
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);
    setError(null);

    try {
      const response = await queryPDFSystem(message);
      
      // Format the response as a bot message
      let botContent = '';
      let sources = [];

      if (response.results && response.results.length > 0) {
        botContent = "Here's what I found in your documents:\n\n";
        
        response.results.forEach((result, index) => {
          botContent += `**Result ${index + 1}:**\n`;
          botContent += `${result.content}\n\n`;
          
          if (result.metadata) {
            sources.push({
              source: result.metadata.source,
              type: result.metadata.type,
              page: result.metadata.page || 'N/A'
            });
          }
        });

        if (sources.length > 0) {
          botContent += "**Sources:**\n";
          sources.forEach((source, index) => {
            botContent += `${index + 1}. ${source.source} (${source.type}, Page: ${source.page})\n`;
          });
        }
      } else {
        botContent = "I couldn't find any relevant information in your documents for that query. Try rephrasing your question or asking about different topics.";
      }

      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: botContent,
        timestamp: new Date().toISOString(),
        metadata: {
          results: response.results,
          query: message,
          sources: sources
        }
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      console.error('Error querying PDF system:', err);
      setError('Failed to process your query. Please try again.');
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: "I'm sorry, but I encountered an error while processing your request. Please try again later.",
        timestamp: new Date().toISOString(),
        metadata: null,
        isError: true
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: 1,
        type: 'bot',
        content: "Hello! I'm your PDF Document Assistant. I can help you find information from your uploaded PDF documents. What would you like to know?",
        timestamp: new Date().toISOString(),
        metadata: null
      }
    ]);
    setError(null);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b px-4 py-3">
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <FileText className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">PDF Document Assistant</h1>
              <p className="text-sm text-gray-500">Ask questions about your PDF documents</p>
            </div>
          </div>
          <button
            onClick={clearChat}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Clear Chat
          </button>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4 max-w-4xl mx-auto w-full">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((message) => (
            <Message key={message.id} message={message} />
          ))}
          {isTyping && (
            <div className="flex items-start space-x-3">
              <div className="p-2 bg-gray-100 rounded-full">
                <Bot className="h-5 w-5 text-gray-600" />
              </div>
              <div className="bg-white rounded-lg px-4 py-3 shadow-sm border max-w-xs">
                <TypingIndicator />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Message Input */}
      <div className="bg-white border-t px-4 py-4">
        <div className="max-w-4xl mx-auto">
          <MessageInput onSendMessage={handleSendMessage} disabled={isTyping} />
        </div>
      </div>
    </div>
  );
}

export default App;
