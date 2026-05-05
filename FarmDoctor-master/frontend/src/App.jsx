import React, { useState } from 'react';
import { ChatProvider } from './context/ChatContext';
import Home from './pages/Home';
import WeatherAdvisory from './components/WeatherAdvisory';
import HistoryPanel from './components/HistoryPanel';
import IntroAnimation from './components/IntroAnimation';

function App() {
  const [showIntro, setShowIntro] = useState(true);
  const [currentPage, setCurrentPage] = useState('home'); // 'home' or 'weather'
  const [showHistory, setShowHistory] = useState(false);
  const [pendingQuery, setPendingQuery] = useState(null);

  const handleIntroComplete = () => {
    setShowIntro(false);
  };

  const handleSelectFromHistory = async (question, solutionType) => {
    setCurrentPage('home');
    setPendingQuery({ question, solutionType });
    setShowHistory(false);
  };

  return (
    <ChatProvider>
      {showIntro ? (
        <IntroAnimation onComplete={handleIntroComplete} />
      ) : (
        <div className="w-full h-screen flex flex-row">
          {/* Left Sidebar Navigation */}
          <div className="w-48 bg-gradient-to-b from-green-700 via-green-600 to-emerald-600 shadow-xl border-r-4 border-amber-600 flex flex-col">
            {/* Logo / Brand */}
            <div className="p-6 border-b-2 border-green-500 bg-black bg-opacity-20">
              <h1 className="text-2xl font-bold text-white text-center">🌾</h1>
              <p className="text-center text-sm text-green-100 mt-2 font-semibold">Farm Assistant</p>
            </div>

            {/* Navigation Buttons */}
            <nav className="flex-1 p-4 space-y-4 flex flex-col">
              <button
                onClick={() => setCurrentPage('home')}
                className={`w-full px-4 py-4 font-semibold transition transform hover:scale-105 rounded-lg border-l-4 flex items-center justify-center gap-2 ${
                  currentPage === 'home'
                    ? 'text-white border-yellow-300 bg-black bg-opacity-20 shadow-lg'
                    : 'text-gray-100 border-transparent hover:text-white hover:bg-black hover:bg-opacity-10'
                }`}
                title="FarmDoctor Assistant"
              >
                <span className="text-xl">💬</span>
                <span>Assistant</span>
              </button>
              
              <button
                onClick={() => setCurrentPage('weather')}
                className={`w-full px-4 py-4 font-semibold transition transform hover:scale-105 rounded-lg border-l-4 flex items-center justify-center gap-2 ${
                  currentPage === 'weather'
                    ? 'text-white border-yellow-300 bg-black bg-opacity-20 shadow-lg'
                    : 'text-gray-100 border-transparent hover:text-white hover:bg-black hover:bg-opacity-10'
                }`}
                title="Weather Guide"
              >
                <span className="text-xl">🌾</span>
                <span>Weather</span>
              </button>

              <button
                onClick={() => setShowHistory(!showHistory)}
                className={`w-full px-4 py-4 font-semibold transition transform hover:scale-105 rounded-lg border-l-4 flex items-center justify-center gap-2 ${
                  showHistory
                    ? 'text-white border-yellow-300 bg-black bg-opacity-20 shadow-lg'
                    : 'text-gray-100 border-transparent hover:text-white hover:bg-black hover:bg-opacity-10'
                }`}
                title="Conversation History"
              >
                <span className="text-xl">📜</span>
                <span>History</span>
              </button>
            </nav>

            {/* Footer Info */}
            <div className="p-4 border-t-2 border-green-500 bg-black bg-opacity-20 text-center">
              <p className="text-xs text-green-100">Smart Farming</p>
              <p className="text-xs text-green-100">Assistant</p>
            </div>
          </div>

          {/* History Panel */}
          {showHistory && (
            <HistoryPanel 
              isExpanded={showHistory}
              onClose={() => setShowHistory(false)}
              onSelectItem={handleSelectFromHistory}
            />
          )}

          {/* Page Content */}
          <div className="flex-1 overflow-auto">
            {currentPage === 'home' ? (
              <Home pendingQuery={pendingQuery} />
            ) : currentPage === 'weather' ? (
              <WeatherAdvisory />
            ) : null}
          </div>
        </div>
      )}
    </ChatProvider>
  );
}

export default App;
