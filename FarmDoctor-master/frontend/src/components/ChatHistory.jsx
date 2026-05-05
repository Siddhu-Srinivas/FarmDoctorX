import React from 'react';
import ChatMessage from './ChatMessage';

const ChatHistory = ({ history }) => {
  return (
    <div>
      {(!history || history.length === 0) && (
        <div className="text-center text-white py-8">
          <p className="text-lg">👋 Welcome to FarmDoctor</p>
          <p className="text-sm">Ask your first question to start diagnosing your crop.</p>
        </div>
      )}
      {history && history.length > 0 && history.map((msg, idx) => (
        <ChatMessage key={idx} message={msg} />
      ))}
    </div>
  );
};

export default ChatHistory;
