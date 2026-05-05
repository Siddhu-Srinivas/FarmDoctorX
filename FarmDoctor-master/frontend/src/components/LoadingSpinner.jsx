import React from 'react';

const LoadingSpinner = () => (
  <div className="flex flex-col items-center justify-center py-8">
    <div className="animate-spin rounded-full h-10 w-10 border-4 border-gray-300 border-t-green-600"></div>
    <p className="mt-3 text-gray-600 text-sm">Processing your question...</p>
  </div>
);

export default LoadingSpinner;
