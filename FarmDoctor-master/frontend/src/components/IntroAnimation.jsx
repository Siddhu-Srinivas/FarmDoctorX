import React, { useEffect, useState } from 'react';
import '../styles/intro-animation.css';
// import { playIntroAudio, stopAudio } from '../utils/audioUtils'; // Uncomment for audio

const IntroAnimation = ({ onComplete }) => {
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    // TEMP: Force show intro for debugging
    const hasSeenIntro = null; // Force show intro

    if (hasSeenIntro) {
      // Skip intro if already seen
      onComplete();
      return;
    }

    // Optional: Play ambient audio (uncomment to enable)
    // const audio = playIntroAudio('ambient');

    // Set up timers for animation completion
    const completeTimer = setTimeout(() => {
      setIsComplete(true);

      // Mark as seen and complete after fade-out
      setTimeout(() => {
        localStorage.setItem('farmAssistantIntroSeen', 'true');
        onComplete();
      }, 1000); // Fade-out duration
    }, 3500); // Total animation duration

    return () => {
      clearTimeout(completeTimer);
      // Optional: Stop audio on unmount (uncomment to enable)
      // stopAudio(audio);
    };
  }, [onComplete]);

  return (
    <div className={`intro-container ${isComplete ? 'intro-fade-out' : ''}`}>
      {/* Debug: Temporary visible text */}
      <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', color: 'white', fontSize: '24px', zIndex: 10000 }}>
        
      </div>

      {/* Animated Clouds */}
      <div className="cloud cloud-1">☁️</div>
      <div className="cloud cloud-2">☁️</div>
      <div className="cloud cloud-3">☁️</div>

      {/* Flying Birds */}
      <div className="bird bird-1">🐦</div>
      <div className="bird bird-2">🐦</div>
      <div className="bird bird-3">🐦</div>

      {/* Smart Drone */}
      <div className="drone">🚁</div>

      {/* Floating Particles (Pollen/Dust) */}
      {Array.from({ length: 15 }, (_, i) => (
        <div key={i} className="particle"></div>
      ))}
      {/* Logo and Tagline */}
      <div className="logo-container">
        <h1 className="logo-text">🌱 Farm Assistant</h1>
        <p className="tagline">Smart Farming Solutions</p>
      </div>

      {/* Swaying Crops */}
      <div className="crop-field">
        <span className="crop">🌾</span>
        <span className="crop">🌽</span>
        <span className="crop">🌾</span>
        <span className="crop">🌻</span>
        <span className="crop">🌾</span>
      </div>
    </div>
  );
};

export default IntroAnimation;