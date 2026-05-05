import React, { useState } from 'react';
import AnswerCard from './AnswerCard';
import parseResponse from '../utils/parseResponse';

const HistoryModal = ({ conversation, onClose, onReRun }) => {
  const [isReRunning, setIsReRunning] = useState(false);
  
  if (!conversation) return null;

  const answer = parseResponse({
    raw_answer: conversation.answer
  });

  const handleReRun = async () => {
    setIsReRunning(true);
    try {
      await onReRun(conversation.question, conversation.solution_type);
      onClose();
    } catch (error) {
      console.error('Error re-running query:', error);
      setIsReRunning(false);
      alert('Failed to re-run query. Please try again.');
    }
  };

  const formatDate = (timestamp) => {
    if (!timestamp) return 'Unknown date';
    try {
      const date = new Date(timestamp);
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e) {
      return 'Unknown date';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-96 overflow-y-auto">
        <div className="sticky top-0 bg-green-600 text-white p-4 flex justify-between items-center">
          <h2 className="text-xl font-bold">Conversation Details</h2>
          <button
            onClick={onClose}
            className="text-white hover:bg-green-700 w-8 h-8 flex items-center justify-center rounded"
          >
            ✕
          </button>
        </div>

        <div className="p-4 space-y-4">
          {/* Question */}
          <div className="bg-blue-50 p-3 rounded border-l-4 border-blue-400">
            <p className="text-xs text-gray-600">Question</p>
            <p className="text-sm font-medium text-gray-800">{conversation.question}</p>
          </div>

          {/* Meta Info */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="bg-gray-50 p-2 rounded">
              <p className="text-gray-600">Solution Type</p>
              <p className="font-medium text-gray-800">{conversation.solution_type}</p>
            </div>
            <div className="bg-gray-50 p-2 rounded">
              <p className="text-gray-600">Date</p>
              <p className="font-medium text-gray-800">{formatDate(conversation.timestamp)}</p>
            </div>
          </div>

          {/* Answer */}
          <div>
            <p className="text-xs text-gray-600 mb-2">Answer</p>
            <AnswerCard answer={answer} />
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-4 border-t border-gray-200">
            <button
              onClick={handleReRun}
              disabled={isReRunning}
              className="flex-1 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {isReRunning ? '⏳ Re-running...' : '🔄 Re-run Query'}
            </button>
            <button
              onClick={onClose}
              disabled={isReRunning}
              className="flex-1 bg-gray-300 text-gray-800 px-4 py-2 rounded hover:bg-gray-400 transition disabled:bg-gray-200 disabled:cursor-not-allowed"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HistoryModal;
