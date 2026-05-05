/**
 * WeatherAdvisory Component
 * Main component for weather-based crop advisory system
 * Displays weather data, alerts, and recommendations
 */

import React, { useState } from 'react';
import useWeather from '../hooks/useWeather';
import WeatherCard from './WeatherCard';
import AdvisoryAlertCard from './AdvisoryAlertCard';
import ActionStepsCard from './ActionStepsCard';
import RagAdviceCard from './RagAdviceCard';

const CROP_TYPES = ['general', 'wheat', 'rice', 'tomato', 'potato', 'cotton', 'sugarcane', 'maize'];

const WeatherAdvisory = () => {
  const {
    location,
    cropType,
    currentWeather,
    advisory,
    forecast,
    loading,
    error,
    success,
    setLocation,
    setCropType,
    fetchAdvisory,
    fetchAdvisoryByGPS,
    clearData,
    clearError,
  } = useWeather();

  const [expandedSection, setExpandedSection] = useState('weather');
  const [showForecast, setShowForecast] = useState(false);

  // State for form inputs
  const [inputLocation, setInputLocation] = useState('');

  const backgroundStyle = {
    backgroundImage: "url('/assistant-bg.png')",
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundRepeat: 'no-repeat',
    // Add fallback for loading issues
    backgroundColor: '#fef3c7', // Light amber fallback
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputLocation.trim()) {
      setLocation(inputLocation);
      fetchAdvisory(inputLocation, cropType, showForecast);
    }
  };

  const handleAutoLocation = async () => {
    await fetchAdvisoryByGPS(cropType);
  };

  const toggleSection = (section) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL':
        return 'bg-red-50 border-red-300';
      case 'HIGH':
        return 'bg-orange-50 border-orange-300';
      case 'MEDIUM':
        return 'bg-yellow-50 border-yellow-300';
      default:
        return 'bg-green-50 border-green-300';
    }
  };

  const getSeverityBadgeColor = (severity) => {
    switch (severity) {
      case 'CRITICAL':
        return 'bg-red-600';
      case 'HIGH':
        return 'bg-orange-600';
      case 'MEDIUM':
        return 'bg-yellow-600';
      default:
        return 'bg-green-600';
    }
  };

  return (
    <div style={backgroundStyle} className="min-h-screen p-4 sm:p-6 relative overflow-hidden">
      {/* Decorative farm background elements */}
      <div className="absolute top-0 right-0 opacity-5 pointer-events-none">
        <svg width="400" height="400" viewBox="0 0 400 400" className="text-green-700">
          <text x="50" y="100" fontSize="80" opacity="0.3" fill="currentColor">🌾</text>
          <text x="300" y="150" fontSize="60" opacity="0.2" fill="currentColor">🚜</text>
          <text x="100" y="350" fontSize="70" opacity="0.25" fill="currentColor">🌱</text>
        </svg>
      </div>

      {/* Header - Farm Branding */}
      <div className="max-w-4xl mx-auto mb-8">
        <div className="bg-white bg-opacity-95 backdrop-blur-sm rounded-lg shadow-xl p-8 border-l-8 border-green-600 relative">
          <div className="flex items-center gap-4 mb-4">
            <span className="text-5xl">🌾</span>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-green-700 to-emerald-600 bg-clip-text text-transparent">Farmer's Weather & Crop Guide</h1>
              <p className="text-green-700 font-medium mt-1">Smart farming starts with knowing your weather ☀️💧</p>
            </div>
          </div>
          <p className="text-gray-700 text-base leading-relaxed">
            Get real-time weather updates tailored to your fields, smart alerts for diseases and pests, and expert crop advice right at your fingertips. Your farm's best friend is just a click away!
          </p>
        </div>
      </div>

      {/* Input Section */}
      <div className="max-w-4xl mx-auto mb-6">
        <div className="bg-white bg-opacity-90 backdrop-blur-sm rounded-lg shadow-lg p-6 transition transform hover:scale-105">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Location Input */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">📍 Farm Location</label>
                <input
                  type="text"
                  value={inputLocation}
                  onChange={(e) => setInputLocation(e.target.value)}
                  placeholder="Enter city name (e.g., New Delhi, Mumbai)"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>

              {/* Crop Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">🌱 Crop Type</label>
                <select
                  value={cropType}
                  onChange={(e) => setCropType(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  {CROP_TYPES.map((crop) => (
                    <option key={crop} value={crop}>
                      {crop.charAt(0).toUpperCase() + crop.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Options and Buttons */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={showForecast}
                  onChange={(e) => setShowForecast(e.target.checked)}
                  className="w-4 h-4 text-green-600 rounded focus:ring-green-500"
                />
                <span className="ml-2 text-sm text-gray-700">Include 5-day weather forecast</span>
              </label>

              <div className="flex gap-3 w-full sm:w-auto">
                <button
                  type="button"
                  onClick={handleAutoLocation}
                  disabled={loading}
                  className="flex-1 sm:flex-none px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg font-medium hover:from-indigo-600 hover:to-blue-700 transition transform hover:scale-105 disabled:bg-gray-400 text-sm"
                  title="Use GPS to get your location"
                >
                  📡 My Farm Location
                </button>
                <button
                  type="submit"
                  disabled={loading || !inputLocation.trim()}
                  className="flex-1 sm:flex-none px-6 py-2 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-lg font-medium hover:from-teal-600 hover:to-green-700 transition transform hover:scale-105 disabled:bg-gray-400 text-sm"
                >
                  {loading ? 'Getting Data...' : '🔍 Get Weather & Advice'}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="max-w-4xl mx-auto mb-6 bg-red-50 bg-opacity-90 backdrop-blur-sm border border-red-300 rounded-lg p-4 flex items-start shadow-lg">
          <span className="text-red-600 mr-3">⚠️</span>
          <div className="flex-1">
            <p className="text-red-800 font-medium">Error</p>
            <p className="text-red-700 text-sm">{error}</p>
          </div>
          <button
            onClick={clearError}
            className="text-red-600 hover:text-red-800 font-bold"
          >
            ×
          </button>
        </div>
      )}

      {/* Results Section */}
      {success && advisory && (
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Severity Banner */}
          <div className={`rounded-lg shadow-lg p-6 border border-gray-300 flex items-center justify-between ${getSeverityColor(advisory.severity_level)} transition transform hover:scale-102`}>
            <div>
              <p className="text-sm text-gray-600">Current Risk Level</p>
              <h2 className="text-2xl font-bold text-gray-800">{advisory.severity_level}</h2>
            </div>
            <div className={`${getSeverityBadgeColor(advisory.severity_level)} text-white rounded-full w-20 h-20 flex items-center justify-center`}>
              <span className="text-3xl">
                {advisory.severity_level === 'CRITICAL' ? '🔴' :
                 advisory.severity_level === 'HIGH' ? '🟠' :
                 advisory.severity_level === 'MEDIUM' ? '🟡' : '🟢'}
              </span>
            </div>
          </div>

          {/* Current Weather Card */}
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <button
              onClick={() => toggleSection('weather')}
              className="w-full px-6 py-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold flex items-center justify-between hover:from-blue-700 hover:to-blue-800 transition transform hover:scale-102 shadow-md"
            >
              <span>☀️ Today's Weather at Your Farm</span>
              <span className="text-lg">{expandedSection === 'weather' ? '−' : '+'}</span>
            </button>
            {expandedSection === 'weather' && currentWeather && (
              <div className="p-6">
                <WeatherCard weather={advisory.weather_summary} />
              </div>
            )}
          </div>

          {/* Alerts Section */}
          {advisory.alerts && advisory.alerts.length > 0 && (
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <button
                onClick={() => toggleSection('alerts')}
                className="w-full px-6 py-4 bg-gradient-to-r from-red-600 to-red-700 text-white font-semibold flex items-center justify-between hover:from-red-700 hover:to-red-800 transition transform hover:scale-102 shadow-md"
              >
                <span>
                  ⚠️ Farm Alerts ({advisory.alerts.filter(a => a.severity === 'high').length} warnings)
                </span>
                <span className="text-lg">{expandedSection === 'alerts' ? '−' : '+'}</span>
              </button>
              {expandedSection === 'alerts' && (
                <div className="p-6 space-y-4">
                  {advisory.alerts.map((alert, index) => (
                    <AdvisoryAlertCard key={index} alert={alert} />
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Action Steps */}
          {advisory.action_steps && advisory.action_steps.length > 0 && (
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <button
                onClick={() => toggleSection('actions')}
                className="w-full px-6 py-4 bg-gradient-to-r from-green-600 to-green-700 text-white font-semibold flex items-center justify-between hover:from-green-700 hover:to-green-800 transition transform hover:scale-102 shadow-md"
              >
                <span>✅ Action Plan for Your Farm Today</span>
                <span className="text-lg">{expandedSection === 'actions' ? '−' : '+'}</span>
              </button>
              {expandedSection === 'actions' && (
                <div className="p-6">
                  <ActionStepsCard steps={advisory.action_steps} />
                </div>
              )}
            </div>
          )}

          {/* Detailed Recommendations */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Irrigation */}
            <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
              <h3 className="text-lg font-bold text-blue-900 mb-3">💧 Watering Your Crops</h3>
              <p className="text-blue-800 text-sm leading-relaxed">{advisory.irrigation_advice}</p>
            </div>

            {/* Disease Prevention */}
            <div className="bg-purple-50 rounded-lg border border-purple-200 p-6">
              <h3 className="text-lg font-bold text-purple-900 mb-3">🦠 Keep Your Crops Healthy</h3>
              <p className="text-purple-800 text-sm leading-relaxed">{advisory.disease_prevention}</p>
            </div>

            {/* Pest Management */}
            <div className="bg-orange-50 rounded-lg border border-orange-200 p-6">
              <h3 className="text-lg font-bold text-orange-900 mb-3">🐛 Protect from Pests & Insects</h3>
              <p className="text-orange-800 text-sm leading-relaxed">{advisory.pest_management}</p>
            </div>

            {/* Safe Operations */}
            <div className="bg-green-50 rounded-lg border border-green-200 p-6">
              <h3 className="text-lg font-bold text-green-900 mb-3">✓ What's Safe to Do Now</h3>
              <ul className="space-y-2">
                {advisory.safe_operations?.map((op, idx) => (
                  <li key={idx} className="text-green-800 text-sm flex items-start">
                    <span className="mr-2">{op.includes('✓') ? '✅' : '❌'}</span>
                    <span>{op.replace('✓ ', '').replace('✗ ', '')}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* RAG-Enhanced Advice */}
          {advisory.rag_enhanced_advice && (
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <button
                onClick={() => toggleSection('rag')}
                className="w-full px-6 py-4 bg-gradient-to-r from-purple-600 to-purple-700 text-white font-semibold flex items-center justify-between hover:from-purple-700 hover:to-purple-800 transition transform hover:scale-102 shadow-md"
              >
                <span>� Smart Farming Tips from Expert Knowledge</span>
                <span className="text-lg">{expandedSection === 'rag' ? '−' : '+'}</span>
              </button>
              {expandedSection === 'rag' && (
                <div className="p-6">
                  <RagAdviceCard advice={advisory.rag_enhanced_advice} />
                </div>
              )}
            </div>
          )}

          {/* Forecast Section */}
          {showForecast && advisory.forecast && (
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <button
                onClick={() => toggleSection('forecast')}
                className="w-full px-6 py-4 bg-gradient-to-r from-indigo-600 to-indigo-700 text-white font-semibold flex items-center justify-between hover:from-indigo-700 hover:to-indigo-800 transition"
              >
                <span>📅 5-Day Forecast</span>
                <span className="text-lg">{expandedSection === 'forecast' ? '−' : '+'}</span>
              </button>
              {expandedSection === 'forecast' && (
                <div className="p-6">
                  <div className="space-y-3">
                    {advisory.forecast.forecasts?.slice(0, 8).map((f, idx) => (
                      <div key={idx} className="text-sm border-b border-gray-200 pb-3 last:border-0">
                        <div className="flex justify-between items-center">
                          <span className="font-medium text-gray-800">{new Date(f.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</span>
                          <span className="text-gray-600">{f.description}</span>
                        </div>
                        <div className="flex gap-4 text-xs text-gray-600 mt-1">
                          <span>🌡️ {f.temperature}°C</span>
                          <span>💧 {f.humidity}%</span>
                          <span>🌧️ {f.rainfall}mm</span>
                          <span>💨 {f.wind_speed}km/h</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Clear Data Button */}
          <div className="flex justify-center">
            <button
              onClick={clearData}
              className="px-6 py-2 bg-gray-600 text-white rounded-lg font-medium hover:bg-gray-700 transition"
            >
              Clear All
            </button>
          </div>
        </div>
      )}

      {/* Initial State */}
      {!success && (
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <div className="text-6xl mb-4">🌾</div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Welcome to Weather Advisory</h2>
            <p className="text-gray-600 mb-6">
              Enter your location and select your crop type to get personalized weather-based farming recommendations
            </p>
            <div className="text-gray-500 text-sm">
              <p>✓ Real-time weather data</p>
              <p>✓ Disease and pest risk alerts</p>
              <p>✓ Irrigation recommendations</p>
              <p>✓ AI-powered agricultural advice</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WeatherAdvisory;
