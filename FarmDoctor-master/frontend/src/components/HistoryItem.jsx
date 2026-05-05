import React from 'react';

const HistoryItem = ({ item, onDelete, onSelect }) => {
  const formatDate = (timestamp) => {
    if (!timestamp) return 'Unknown date';
    try {
      const date = new Date(timestamp);
      const today = new Date();
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);

      if (date.toDateString() === today.toDateString()) {
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
      } else if (date.toDateString() === yesterday.toDateString()) {
        return 'Yesterday';
      } else {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      }
    } catch (e) {
      return 'Unknown date';
    }
  };

  const getSolutionTypeColor = (type) => {
    switch (type) {
      case 'Organic Only':
        return 'bg-green-100 text-green-700';
      case 'Inorganic Only':
        return 'bg-blue-100 text-blue-700';
      case 'Both':
        return 'bg-purple-100 text-purple-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  const truncateText = (text, length = 50) => {
    if (!text) return '';
    return text.length > length ? text.substring(0, length) + '...' : text;
  };

  return (
    <div className="border-b border-gray-200 p-3 hover:bg-gray-50 transition cursor-pointer">
      <div onClick={() => onSelect(item)} className="flex-1">
        <p className="text-sm font-medium text-gray-800 mb-1">
          {truncateText(item.question, 40)}
        </p>
        <div className="flex items-center gap-2">
          <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${getSolutionTypeColor(item.solution_type)}`}>
            {item.solution_type}
          </span>
          <span className="text-xs text-gray-500">{formatDate(item.timestamp)}</span>
        </div>
      </div>
      <button
        onClick={(e) => {
          e.stopPropagation();
          onDelete(item.id);
        }}
        className="text-red-500 hover:text-red-700 text-xs ml-2 mt-2"
      >
        Delete
      </button>
    </div>
  );
};

export default HistoryItem;
