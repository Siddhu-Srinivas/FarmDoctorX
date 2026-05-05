import React from 'react';
import AnswerCard from './AnswerCard';

const ChatMessage = ({ message }) => {
  const { user, ai } = message;
  return (
    <div className="mb-6">
      <div className="flex justify-end mb-2">
        <div className="bg-green-600 text-white px-4 py-2 rounded-lg max-w-sm">
          <p className="text-sm">{user}</p>
        </div>
      </div>
      {ai && (
        <div className="flex justify-start">
          {ai.error ? (
            <div className="bg-red-100 border border-red-300 text-red-700 px-4 py-2 rounded-lg">
              ❌ {ai.error}
            </div>
          ) : (
            <div className="w-full">
              <AnswerCard answer={ai} />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
