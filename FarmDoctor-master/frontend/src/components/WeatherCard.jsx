/**
 * WeatherCard Component
 * Displays current weather information in a formatted card
 */

import React from 'react';

const WeatherCard = ({ weather }) => {
  if (!weather) return null;

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {/* Temperature */}
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200 hover:shadow-lg transform hover:scale-105 transition cursor-pointer">
          <p className="text-sm text-gray-600">Temperature</p>
          <p className="text-2xl font-bold text-blue-700">{weather.temperature || 'N/A'}°C</p>
          <p className="text-xs text-gray-500 mt-1">Feels like {weather.feels_like || 'N/A'}°C</p>
        </div>

        {/* Humidity */}
        <div className="bg-cyan-50 rounded-lg p-4 border border-cyan-200 hover:shadow-lg transform hover:scale-105 transition cursor-pointer">
          <p className="text-sm text-gray-600">Humidity</p>
          <p className="text-2xl font-bold text-cyan-700">{weather.humidity || 'N/A'}%</p>
          <p className="text-xs text-gray-500 mt-1">Moisture level</p>
        </div>

        {/* Rainfall */}
        <div className="bg-green-50 rounded-lg p-4 border border-green-200 hover:shadow-lg transform hover:scale-105 transition cursor-pointer">
          <p className="text-sm text-gray-600">Rainfall</p>
          <p className="text-2xl font-bold text-green-700">{weather.rainfall || 'N/A'}mm</p>
          <p className="text-xs text-gray-500 mt-1">Recent precipitation</p>
        </div>

        {/* Wind Speed */}
        <div className="bg-orange-50 rounded-lg p-4 border border-orange-200 hover:shadow-lg transform hover:scale-105 transition cursor-pointer">
          <p className="text-sm text-gray-600">Wind Speed</p>
          <p className="text-2xl font-bold text-orange-700">{weather.wind_speed || 'N/A'}</p>
          <p className="text-xs text-gray-500 mt-1">km/h</p>
        </div>

        {/* Cloud Cover */}
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:shadow-lg transform hover:scale-105 transition cursor-pointer">
          <p className="text-sm text-gray-600">Cloud Cover</p>
          <p className="text-2xl font-bold text-gray-700">{weather.clouds || 'N/A'}%</p>
          <p className="text-xs text-gray-500 mt-1">Sky cover</p>
        </div>

        {/* Visibility */}
        <div className="bg-indigo-50 rounded-lg p-4 border border-indigo-200 hover:shadow-lg transform hover:scale-105 transition cursor-pointer">
          <p className="text-sm text-gray-600">Visibility</p>
          <p className="text-2xl font-bold text-indigo-700">{(weather.visibility / 1000).toFixed(1) || 'N/A'} km</p>
          <p className="text-xs text-gray-500 mt-1">Air clarity</p>
        </div>
      </div>

      {/* Condition Description */}
      <div className="bg-gradient-to-r from-blue-100 to-cyan-100 rounded-lg p-4 border border-blue-200 hover:shadow-lg transition cursor-pointer">
        <p className="text-sm text-gray-600">Current Condition</p>
        <p className="text-lg font-semibold text-blue-900 capitalize">{weather.condition || 'Unknown'}</p>
      </div>

      {/* Critical Alerts Count */}
      {(weather.critical_alerts || weather.warning_alerts) && (
        <div className="flex gap-4">
          {weather.critical_alerts > 0 && (
            <div className="flex-1 bg-red-50 rounded-lg p-3 border border-red-200">
              <p className="text-xs text-gray-600">Critical Alerts</p>
              <p className="text-lg font-bold text-red-700">{weather.critical_alerts}</p>
            </div>
          )}
          {weather.warning_alerts > 0 && (
            <div className="flex-1 bg-yellow-50 rounded-lg p-3 border border-yellow-200">
              <p className="text-xs text-gray-600">Warnings</p>
              <p className="text-lg font-bold text-yellow-700">{weather.warning_alerts}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default WeatherCard;
