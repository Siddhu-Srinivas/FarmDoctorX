/**
 * AdvisoryAlertCard Component
 * Displays individual alert with severity level and recommendations
 */

import React from 'react';

const AdvisoryAlertCard = ({ alert }) => {
  const getSeverityStyle = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'high':
        return {
          bg: 'bg-red-50',
          border: 'border-red-300',
          icon: '🔴',
          badgeBg: 'bg-red-600',
          titleColor: 'text-red-900',
          descColor: 'text-red-800',
          badgeColor: 'text-white',
        };
      case 'medium':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-300',
          icon: '🟡',
          badgeBg: 'bg-yellow-600',
          titleColor: 'text-yellow-900',
          descColor: 'text-yellow-800',
          badgeColor: 'text-white',
        };
      case 'low':
        return {
          bg: 'bg-green-50',
          border: 'border-green-300',
          icon: '🟢',
          badgeBg: 'bg-green-600',
          titleColor: 'text-green-900',
          descColor: 'text-green-800',
          badgeColor: 'text-white',
        };
      default:
        return {
          bg: 'bg-blue-50',
          border: 'border-blue-300',
          icon: '🔵',
          badgeBg: 'bg-blue-600',
          titleColor: 'text-blue-900',
          descColor: 'text-blue-800',
          badgeColor: 'text-white',
        };
    }
  };

  const style = getSeverityStyle(alert.severity);

  return (
    <div className={`${style.bg} border-l-6 ${style.border} rounded-lg p-4 shadow-lg hover:shadow-xl transition transform hover:scale-102`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-start gap-3 flex-1">
          <span className="text-2xl mt-0.5">{style.icon}</span>
          <div>
            <h4 className={`font-bold ${style.titleColor} text-lg`}>{alert.title}</h4>
            <p className={`text-sm mt-1 ${style.descColor}`}>{alert.description}</p>
          </div>
        </div>
        <span className={`${style.badgeBg} ${style.badgeColor} px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap ml-2`}>
          {alert.severity.toUpperCase()}
        </span>
      </div>

      <div className="bg-white bg-opacity-70 backdrop-blur-sm rounded p-3 mt-3">
        <p className="text-sm font-semibold text-gray-800 mb-1">💡 Recommendation:</p>
        <p className="text-sm text-gray-700 leading-relaxed">{alert.recommendation}</p>
      </div>

      {alert.action_required && (
        <div className="mt-3 flex items-center gap-2 text-red-700 text-sm font-semibold">
          <span>⚠️</span>
          <span>Action Required</span>
        </div>
      )}
    </div>
  );
};

export default AdvisoryAlertCard;
