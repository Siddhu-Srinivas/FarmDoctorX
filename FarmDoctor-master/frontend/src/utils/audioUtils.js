// Audio Utilities for Intro Animation
// Optional audio playback with graceful fallbacks

/**
 * Play intro audio with error handling
 * @param {string} type - Audio type ('ambient', 'nature', 'birds')
 * @returns {HTMLAudioElement|null} - Audio element or null if failed
 */
export const playIntroAudio = (type = 'ambient') => {
  try {
    // Check if audio is supported and autoplay is allowed
    if (typeof Audio === 'undefined') {
      console.warn('Audio not supported in this browser');
      return null;
    }

    // Map audio types to file paths
    const audioFiles = {
      ambient: '/audio/nature-ambience.mp3',
      nature: '/audio/nature-ambience.mp3',
      birds: '/audio/birds-chirping.mp3'
    };

    const audioPath = audioFiles[type];
    if (!audioPath) {
      console.warn(`Unknown audio type: ${type}`);
      return null;
    }

    const audio = new Audio(audioPath);

    // Set audio properties
    audio.volume = 0.3; // Low volume for ambient sound
    audio.loop = true; // Loop ambient audio

    // Add error handling
    audio.addEventListener('error', (e) => {
      console.warn('Audio failed to load:', e);
    });

    // Add load handling
    audio.addEventListener('canplaythrough', () => {
      // Only play if user hasn't interacted (respects autoplay policies)
      const playPromise = audio.play();
      if (playPromise !== undefined) {
        playPromise
          .then(() => {
            console.log('Intro audio playing');
          })
          .catch((error) => {
            console.warn('Audio autoplay blocked:', error);
          });
      }
    });

    return audio;
  } catch (error) {
    console.warn('Failed to initialize audio:', error);
    return null;
  }
};

/**
 * Stop and cleanup audio
 * @param {HTMLAudioElement|null} audio - Audio element to stop
 */
export const stopAudio = (audio) => {
  if (audio && typeof audio.pause === 'function') {
    try {
      audio.pause();
      audio.currentTime = 0;
      console.log('Intro audio stopped');
    } catch (error) {
      console.warn('Failed to stop audio:', error);
    }
  }
};

/**
 * Check if audio files exist
 * @param {string} type - Audio type to check
 * @returns {Promise<boolean>} - True if audio file exists
 */
export const checkAudioExists = async (type = 'ambient') => {
  try {
    const audioFiles = {
      ambient: '/audio/nature-ambience.mp3',
      nature: '/audio/nature-ambience.mp3',
      birds: '/audio/birds-chirping.mp3'
    };

    const audioPath = audioFiles[type];
    if (!audioPath) return false;

    const response = await fetch(audioPath, { method: 'HEAD' });
    return response.ok;
  } catch (error) {
    console.warn('Audio check failed:', error);
    return false;
  }
};