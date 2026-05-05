import React, { useState, useEffect } from 'react';
import HistoryItem from './HistoryItem';
import HistoryModal from './HistoryModal';
import { useHistory } from '../hooks/useHistory';

const HistoryPanel = ({ onSelectItem, isExpanded = true, onClose }) => {
  const { conversations, loading, error, loadHistory, deleteItem, clearHistory, search, filter } = useHistory();
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('All');

  useEffect(() => {
    if (isExpanded) {
      loadHistory();
    }
  }, [isExpanded, loadHistory]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      search(searchQuery);
    }
  };

  const handleFilter = (type) => {
    setFilterType(type);
    if (type === 'All') {
      loadHistory();
    } else {
      filter(type);
    }
  };

  const handleSelectConversation = (conversation) => {
    setSelectedConversation(conversation);
  };

  const handleReRun = (question, solutionType) => {
    onSelectItem(question, solutionType);
  };

  const handleDelete = async (conversationId) => {
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      try {
        await deleteItem(conversationId);
      } catch (err) {
        alert('Failed to delete conversation');
      }
    }
  };

  const handleClearAll = async () => {
    if (window.confirm('Are you sure you want to clear all conversations? This cannot be undone.')) {
      try {
        await clearHistory();
        setSearchQuery('');
        setFilterType('All');
      } catch (err) {
        alert('Failed to clear history');
      }
    }
  };

  return (
    <>
      {/* History Sidebar */}
      <div
        className={`w-80 bg-white shadow-lg flex flex-col flex-shrink-0 border-r border-gray-300 overflow-hidden ${
          isExpanded ? 'block' : 'hidden'
        }`}
      >
        {/* Header */}
        <div className="bg-green-600 text-white p-4 flex-none flex justify-between items-center">
          <div>
            <h2 className="text-lg font-bold">Conversation History</h2>
            <p className="text-sm text-green-100">Total: {conversations.length}</p>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="text-white hover:bg-green-700 w-8 h-8 flex items-center justify-center rounded"
            >
              ✕
            </button>
          )}
        </div>

        {/* Search */}
        <form onSubmit={handleSearch} className="border-b border-gray-200 p-3 flex-none">
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Search conversations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-green-600"
            />
            <button
              type="submit"
              className="bg-green-600 text-white px-2 py-1 rounded text-sm hover:bg-green-700"
            >
              🔍
            </button>
          </div>
        </form>

        {/* Filter */}
        <div className="border-b border-gray-200 p-3 flex-none">
          <div className="flex gap-1 flex-wrap">
            {['All', 'Organic Only', 'Inorganic Only', 'Both'].map((type) => (
              <button
                key={type}
                onClick={() => handleFilter(type)}
                className={`text-xs px-2 py-1 rounded transition ${
                  filterType === type
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto">
          {loading && (
            <div className="p-4 text-center text-gray-500">
              <p>Loading history...</p>
            </div>
          )}

          {error && (
            <div className="p-4 bg-red-50 text-red-700 text-sm border-b border-red-200">
              <p>Error: {error}</p>
            </div>
          )}

          {!loading && conversations.length === 0 && (
            <div className="p-4 text-center text-gray-500">
              <p>No conversations yet</p>
              <p className="text-xs mt-1">Your conversations will appear here</p>
            </div>
          )}

          {conversations.map((conversation) => (
            <HistoryItem
              key={conversation.id}
              item={conversation}
              onDelete={handleDelete}
              onSelect={handleSelectConversation}
            />
          ))}
        </div>

        {/* Actions */}
        {conversations.length > 0 && (
          <div className="border-t border-gray-200 p-3 flex-none bg-gray-50">
            <button
              onClick={handleClearAll}
              className="w-full bg-red-500 text-white px-3 py-2 rounded text-sm hover:bg-red-600 transition"
            >
              Clear All History
            </button>
          </div>
        )}
      </div>

      {/* Modal */}
      {selectedConversation && (
        <HistoryModal
          conversation={selectedConversation}
          onClose={() => setSelectedConversation(null)}
          onReRun={handleReRun}
        />
      )}
    </>
  );
};

export default HistoryPanel;
