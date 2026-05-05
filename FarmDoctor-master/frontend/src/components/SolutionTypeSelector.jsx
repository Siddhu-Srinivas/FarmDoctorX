import React from 'react';

const OPTIONS = ['Organic Only', 'Inorganic Only', 'Both'];

const SolutionTypeSelector = ({ value, onChange }) => {
  return (
    <div className="flex items-center gap-2">
      <label className="font-medium text-gray-700">Solution Type:</label>
      <select
        className="border border-gray-300 rounded-lg px-3 py-1 focus:outline-none focus:ring-2 focus:ring-green-600"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        {OPTIONS.map((opt) => (
          <option key={opt} value={opt}>
            {opt}
          </option>
        ))}
      </select>
    </div>
  );
};

export default SolutionTypeSelector;
