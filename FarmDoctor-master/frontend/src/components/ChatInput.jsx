import React, { useState, useEffect, useRef } from 'react';

const ChatInput = ({ onSend, disabled, language }) => {
  const [text, setText] = useState('');
  const [listening, setListening] = useState(false);
  const [micSupported, setMicSupported] = useState(false);
  const recognitionRef = useRef(null);

  const langCodes = {
    'English': 'en-IN',
    'Hindi': 'hi-IN',
    'Telugu': 'te-IN',
    'Marathi': 'mr-IN',
    'Tamil': 'ta-IN',
    'Kannada': 'kn-IN'
  };

  // Check for browser speech recognition support
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      setMicSupported(true);
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = langCodes[language] || 'en-IN';

      recognition.onresult = (e) => {
        const transcript = e.results[0][0].transcript;
        setText((prev) => (prev ? prev + ' ' + transcript : transcript));
      };

      recognition.onerror = () => setListening(false);
      recognition.onend   = () => setListening(false);

      recognitionRef.current = recognition;
    }
  }, []);

  // Update recognition language when the prop changes
  useEffect(() => {
    if (recognitionRef.current) {
      recognitionRef.current.lang = langCodes[language] || 'en-IN';
    }
  }, [language]);

  const toggleMic = () => {
    if (!recognitionRef.current) return;
    if (listening) {
      recognitionRef.current.stop();
      setListening(false);
    } else {
      recognitionRef.current.start();
      setListening(true);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim()) {
      // Stop mic if still running
      if (listening && recognitionRef.current) {
        recognitionRef.current.stop();
        setListening(false);
      }
      onSend(text);
      setText('');
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '8px', width: '100%', alignItems: 'center' }}>

      {/* ── Mic button (left) ── */}
      {micSupported && (
        <button
          type="button"
          onClick={toggleMic}
          disabled={disabled}
          title={listening ? 'Stop recording' : 'Speak your question'}
          style={{
            flexShrink: 0,
            width: '44px',
            height: '44px',
            borderRadius: '50%',
            border: listening ? '2px solid #dc2626' : '1.5px solid #d1d5db',
            background: listening ? '#fee2e2' : '#ffffff',
            cursor: disabled ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '18px',
            transition: 'all 0.2s ease',
            boxShadow: listening
              ? '0 0 0 4px rgba(220,38,38,0.15)'
              : '0 1px 3px rgba(0,0,0,0.08)',
            animation: listening ? 'micPulse 1.2s infinite' : 'none',
            outline: 'none',
          }}
        >
          {listening ? '⏹️' : '🎙️'}
        </button>
      )}

      {/* ── Text input ── */}
      <input
        type="text"
        style={{
          flex: 1,
          border: '1.5px solid #d1d5db',
          borderRadius: '10px',
          padding: '10px 16px',
          fontSize: '14px',
          outline: 'none',
          color: '#111111',
          background: '#ffffff',
          transition: 'border-color 0.2s',
        }}
        placeholder={listening ? '🎙️ Listening…' : 'Ask about a crop disease…'}
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={disabled}
        onFocus={e  => (e.target.style.borderColor = '#4ade80')}
        onBlur={e   => (e.target.style.borderColor = '#d1d5db')}
      />

      {/* ── Send button (right) ── */}
      <button
        type="submit"
        disabled={disabled || !text.trim()}
        style={{
          flexShrink: 0,
          background: disabled || !text.trim() ? '#9ca3af' : '#16a34a',
          color: '#ffffff',
          border: 'none',
          borderRadius: '10px',
          padding: '10px 20px',
          fontSize: '14px',
          fontWeight: '600',
          cursor: disabled || !text.trim() ? 'not-allowed' : 'pointer',
          transition: 'background 0.2s',
          whiteSpace: 'nowrap',
        }}
      >
        {disabled ? '⏳ Sending…' : '📤 Send'}
      </button>

      {/* Pulse animation keyframes injected inline */}
      <style>{`
        @keyframes micPulse {
          0%   { box-shadow: 0 0 0 0   rgba(220,38,38,0.35); }
          70%  { box-shadow: 0 0 0 10px rgba(220,38,38,0);   }
          100% { box-shadow: 0 0 0 0   rgba(220,38,38,0);    }
        }
      `}</style>
    </form>
  );
};

export default ChatInput;
