import React from 'react';
import { Bot, User, FileText, Table, Type, AlertCircle } from 'lucide-react';

const Message = ({ message }) => {
  const isUser = message.type === 'user';
  
  const formatContent = (content) => {
    // Convert markdown-style formatting to HTML
    const formatted = content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1 py-0.5 rounded text-sm">$1</code>')
      .replace(/\n/g, '<br>');
    
    return formatted;
  };

  const getSourceIcon = (type) => {
    switch (type) {
      case 'field':
        return <Type className="h-4 w-4 text-green-600" />;
      case 'table':
        return <Table className="h-4 w-4 text-blue-600" />;
      case 'text':
        return <FileText className="h-4 w-4 text-purple-600" />;
      default:
        return <FileText className="h-4 w-4 text-gray-600" />;
    }
  };

  return (
    <div className={`flex items-start space-x-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className={`p-2 rounded-full ${message.isError ? 'bg-red-100' : 'bg-gray-100'}`}>
          {message.isError ? (
            <AlertCircle className="h-5 w-5 text-red-600" />
          ) : (
            <Bot className="h-5 w-5 text-gray-600" />
          )}
        </div>
      )}
      
      <div className={`max-w-2xl ${isUser ? 'order-first' : ''}`}>
        <div
          className={`rounded-lg px-4 py-3 shadow-sm ${
            isUser
              ? 'bg-blue-600 text-white'
              : message.isError
              ? 'bg-red-50 border border-red-200'
              : 'bg-white border'
          }`}
        >
          <div
            className={`${
              isUser ? 'text-white' : message.isError ? 'text-red-800' : 'text-gray-800'
            }`}
            dangerouslySetInnerHTML={{
              __html: formatContent(message.content)
            }}
          />
        </div>
        
        {/* Show metadata for bot messages */}
        {!isUser && message.metadata && message.metadata.sources && (
          <div className="mt-2 space-y-1">
            {message.metadata.sources.map((source, index) => (
              <div
                key={index}
                className="flex items-center space-x-2 text-xs text-gray-500 bg-gray-50 rounded px-2 py-1"
              >
                {getSourceIcon(source.type)}
                <span className="font-medium">{source.source}</span>
                <span className="text-gray-400">•</span>
                <span className="capitalize">{source.type}</span>
                {source.page !== 'N/A' && (
                  <>
                    <span className="text-gray-400">•</span>
                    <span>Page {source.page}</span>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
        
        <div className={`text-xs mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
          <span className="text-gray-500">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
        </div>
      </div>
      
      {isUser && (
        <div className="p-2 bg-blue-100 rounded-full">
          <User className="h-5 w-5 text-blue-600" />
        </div>
      )}
    </div>
  );
};

export default Message;