import React, { useState, useRef, useEffect, forwardRef } from 'react';
import ChatHistory from './ChatHistory';
import ChatInput from './ChatInput';
import SolutionTypeSelector from './SolutionTypeSelector';
import LoadingSpinner from './LoadingSpinner';
import { useChatState } from '../context/ChatContext';

const ChatContainer = forwardRef(({ sendMessage, clearHistory }, ref) => {
  const { history } = useChatState();
  const [loading, setLoading] = useState(false);
  const [solutionType, setSolutionType] = useState('Both');
  const [language, setLanguage] = useState('English');
  const [error, setError] = useState(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [history]);

  useEffect(() => {
    if (ref && typeof ref !== 'function') {
      ref.current = { scrollToBottom: () => {
        if (scrollRef.current) {
          scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
      } };
    }
  }, [ref]);

  const handleSend = async (text) => {
    if (!text.trim()) {
      setError('Please enter a question');
      return;
    }
    setError(null);
    setLoading(true);
    try {
      await sendMessage(text, solutionType, language);
    } catch (err) {
      setError(err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    clearHistory();
    setError(null);
  };

  return (
    <div className="w-full h-full flex flex-col bg-transparent">
      <div className="flex-none bg-white/80 shadow-sm border-b border-white/20 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center mb-3">
            <h1 className="text-3xl font-bold text-green-700">🌾 FarmDoctor</h1>
            <button
              onClick={handleClear}
              className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200 transition"
            >
              Clear Chat
            </button>
          </div>
          <div className="flex flex-col md:flex-row gap-4 items-start md:items-center">
            <SolutionTypeSelector
              value={solutionType}
              onChange={setSolutionType}
            />
            
            <div className="flex items-center gap-2 bg-white/60 p-1 rounded-lg">
              <span className="text-xs font-bold text-gray-500 ml-2 uppercase">Language:</span>
              <select 
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="bg-white border border-gray-200 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="English">English</option>
                <option value="Hindi">Hindi</option>
                <option value="Telugu">Telugu</option>
                <option value="Marathi">Marathi</option>
                <option value="Tamil">Tamil</option>
                <option value="Kannada">Kannada</option>
              </select>
            </div>
          </div>
          {error && (
            <div className="mt-2 p-2 bg-red-100 text-red-700 text-sm rounded">
              ⚠️ {error}
            </div>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto bg-white/10">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <ChatHistory history={history} />
          {loading && <LoadingSpinner />}
        </div>
      </div>

      <div className="flex-none bg-white/30 shadow-lg border-t border-white/20">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <ChatInput onSend={handleSend} disabled={loading} language={language} />
        </div>
      </div>
    </div>
  );
});

export default ChatContainer;
