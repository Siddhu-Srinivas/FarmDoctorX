/**
 * ActionStepsCard Component
 * Displays prioritized action steps farmers should take
 */

import React from 'react';

const ActionStepsCard = ({ steps }) => {
  if (!steps || steps.length === 0) return null;

  // Separate immediate actions from other steps
  const immediateActions = steps.filter(step => step.includes('IMMEDIATE'));
  const regularSteps = steps.filter(step => !step.includes('IMMEDIATE'));

  return (
    <div className="space-y-4">
      {/* Immediate Actions Section */}
      {immediateActions.length > 0 && (
        <div className="bg-red-50 bg-opacity-90 border-l-6 border-red-500 rounded-lg p-4 shadow-md">
          <h3 className="font-bold text-red-900 mb-3 flex items-center gap-2">
            <span>🚨</span> Immediate Actions Required
          </h3>
          <ul className="space-y-2">
            {immediateActions.map((step, idx) => (
              <li
                key={idx}
                className="text-red-800 text-sm flex items-start gap-3 p-2 bg-white rounded border border-red-200 hover:bg-red-100 transition cursor-pointer"
              >
                <span className="text-red-600 font-bold mt-0.5">•</span>
                <span>{step.replace('⚠️ IMMEDIATE ACTIONS REQUIRED:', '').trim()}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Regular Steps */}
      {regularSteps.length > 0 && (
        <div className="bg-green-50 bg-opacity-90 border-l-6 border-green-500 rounded-lg p-4 shadow-md">
          <ul className="space-y-2">
            {regularSteps.map((step, idx) => {
              if (step === '' || step.trim() === '') return null;

              // Check if step is a header (ends with colon)
              const isHeader = step.trim().endsWith(':');

              return (
                <li
                  key={idx}
                  className={`text-sm ${
                    isHeader
                      ? 'font-bold text-green-900 mt-3 mb-2'
                      : 'text-green-800 flex items-start gap-3'
                  }`}
                >
                  {!isHeader && <span className="text-green-600 font-bold">✓</span>}
                  <span>{step}</span>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ActionStepsCard;
