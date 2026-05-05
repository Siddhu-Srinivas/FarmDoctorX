import React, { useState, useRef } from 'react';

/* ══════════════════════════════════════════════
   Shared helpers
══════════════════════════════════════════════ */

/**
 * Split a string on **...** and return an array of React nodes,
 * where matched parts are <strong> and the rest is plain text.
 */
function renderInlineBold(text) {
  const parts = text.split(/\*\*(.*?)\*\*/g);
  return parts.map((part, i) =>
    i % 2 === 1
      ? <strong key={i} style={{ fontWeight: '700' }}>{part}</strong>
      : part
  );
}

function stripLeading(text = '') {
  return text.replace(/^[\s\-–#>|]+/, '').trim();
}

/** Speak helper component — Uses ElevenLabs with Browser Fallback */
const SpeakButton = ({ text, language }) => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const audioRef = useRef(null);

  const speak = async () => {
    if (isSpeaking) {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    const cleanSpeechText = text.replace(/\*\*/g, '').replace(/[-–*•]/g, '').trim();

    try {
      setIsSpeaking(true);
      
      const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      // 1. Try ElevenLabs via our backend
      const response = await fetch(`${API_BASE}/api/tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: cleanSpeechText, language })
      });

      if (!response.ok) throw new Error('ElevenLabs API returned error');

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audioRef.current = audio;

      audio.onended = () => {
        setIsSpeaking(false);
        URL.revokeObjectURL(url);
      };

      await audio.play();
    } catch (err) {
      console.warn("ElevenLabs failed, falling back to Browser TTS:", err);

      // 2. Browser Fallback (Standard Web Speech API)
      if (!window.speechSynthesis) {
        setIsSpeaking(false);
        return;
      }

      const utterance = new SpeechSynthesisUtterance(cleanSpeechText);
      const langMap = {
        'English': 'en-IN', 'Hindi': 'hi-IN', 'Telugu': 'te-IN',
        'Marathi': 'mr-IN', 'Tamil': 'ta-IN', 'Kannada': 'kn-IN'
      };
      const targetLang = langMap[language] || 'en-IN';
      utterance.lang = targetLang;

      const voices = window.speechSynthesis.getVoices();
      const nativeVoice = voices.find(v => v.lang.replace('_', '-') === targetLang) || 
                          voices.find(v => v.lang.split(/[-_]/)[0] === targetLang.split('-')[0]);
      if (nativeVoice) utterance.voice = nativeVoice;
      
      utterance.rate = 0.95;
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(utterance);
    }
  };

  return (
    <button
      onClick={speak}
      style={{
        background: 'none',
        border: 'none',
        cursor: 'pointer',
        fontSize: '18px',
        padding: '4px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: isSpeaking ? '#16a34a' : '#666666',
        transition: 'color 0.2s',
        marginLeft: 'auto',
        borderRadius: '50%',
      }}
      title={isSpeaking ? "Stop Speaking" : "Listen to this section (AI Voice)"}
    >
      {isSpeaking ? '🔊' : '🔈'}
    </button>
  );
};

function RichText({ text }) {
  const lines = text.split('\n').filter(l => l.trim());
  return (
    <div style={{ fontSize: '14px', lineHeight: '1.85', color: '#222222', fontWeight: '400' }}>
      {lines.map((line, i) => {
        const trimmed = line.trim();
        const isSubHeader = /^\*\*[^*]+\*\*:?\s*$/.test(trimmed);
        const isBullet = /^[-–*•]\s/.test(trimmed);

        if (isSubHeader) {
          const label = trimmed.replace(/^\*\*/, '').replace(/\*\*:?\s*$/, '');
          return (
            <p key={i} style={{
              fontWeight: '700', fontSize: '13.5px',
              color: '#111111', marginTop: '10px', marginBottom: '3px',
            }}>
              {label}
            </p>
          );
        }

        if (isBullet) {
          const content = stripLeading(trimmed);
          return (
            <div key={i} style={{ display: 'flex', gap: '8px', marginBottom: '5px', paddingLeft: '2px', fontWeight: '400' }}>
              <span style={{ flexShrink: 0, color: '#555555', marginTop: '1px' }}>•</span>
              <span>{renderInlineBold(content)}</span>
            </div>
          );
        }

        return (
          <p key={i} style={{ marginBottom: '6px', fontWeight: '400' }}>
            {renderInlineBold(trimmed)}
          </p>
        );
      })}
    </div>
  );
}

/* ══════════════════════════════════════════════
   Generic Section Card
══════════════════════════════════════════════ */
function SectionCard({ icon, label, text, language, children }) {
  const contentText = text || (typeof children === 'string' ? children : '');

  return (
    <div style={{
      background: '#ffffff',
      border: '1px solid #e0e0e0',
      borderRadius: '14px',
      padding: '18px 20px',
      marginBottom: '12px',
      boxShadow: '0 1px 4px rgba(0,0,0,0.07)',
    }}>
      <div style={{
        display: 'flex', alignItems: 'center', gap: '9px',
        marginBottom: '12px',
        paddingBottom: '10px',
        borderBottom: '1px solid #eeeeee',
      }}>
        <span style={{ fontSize: '18px', lineHeight: 1 }}>{icon}</span>
        <span style={{
          fontWeight: '700', fontSize: '14px',
          color: '#111111', letterSpacing: '0.01em',
        }}>{label}</span>
        {contentText && <SpeakButton text={contentText} language={language} />}
      </div>

      <div style={{ paddingLeft: '2px' }}>
        {typeof children === 'string' ? <RichText text={children} /> : children}
      </div>
    </div>
  );
}

/* ══════════════════════════════════════════════
   Combined Diagnosis block
══════════════════════════════════════════════ */
function SubSection({ icon, label, text, language }) {
  if (!text) return null;
  return (
    <div style={{ marginBottom: '4px' }}>
      <div style={{
        display: 'flex', alignItems: 'center', gap: '7px',
        marginBottom: '8px',
      }}>
        <span style={{ fontSize: '16px', lineHeight: 1 }}>{icon}</span>
        <span style={{ fontWeight: '700', fontSize: '13px', color: '#111111' }}>{label}</span>
        <SpeakButton text={text} language={language} />
      </div>
      <div style={{ paddingLeft: '4px' }}>
        <RichText text={text} />
      </div>
    </div>
  );
}

function DiagnosisBlock({ problem, organic, inorganic, language }) {
  const hasAny = problem || organic || inorganic;
  if (!hasAny) return null;

  const sections = [
    { icon: '🔎', label: 'Problem', text: problem },
    { icon: '🌿', label: 'Organic Solution', text: organic },
    { icon: '⚗️', label: 'Inorganic Solution', text: inorganic },
  ].filter(s => s.text);

  return (
    <div style={{
      background: '#ffffff',
      border: '1px solid #e0e0e0',
      borderRadius: '14px',
      padding: '18px 20px',
      marginBottom: '12px',
      boxShadow: '0 1px 4px rgba(0,0,0,0.07)',
    }}>
      {sections.map((s, idx) => (
        <div key={idx}>
          <SubSection icon={s.icon} label={s.label} text={s.text} language={language} />
          {idx < sections.length - 1 && (
            <hr style={{
              border: 'none', borderTop: '1px solid #eeeeee',
              margin: '14px 0',
            }} />
          )}
        </div>
      ))}
    </div>
  );
}

const SuccessTipCard = ({ text, language }) => <SectionCard icon="🏆" label="Success Tip" text={text} language={language}>{text}</SectionCard>;
const AdditionalTipsCard = ({ text, language }) => <SectionCard icon="🌾" label="Additional Tips" text={text} language={language}>{text}</SectionCard>;

/* ══════════════════════════════════════════════
   Fallback raw card
══════════════════════════════════════════════ */
const RawCard = ({ raw, language }) => {
  const [expanded, setExpanded] = useState(false);
  const PREVIEW = 500;
  const isLong = raw.length > PREVIEW;

  return (
    <div style={{
      background: '#ffffff',
      border: '1px solid #e0e0e0',
      borderRadius: '14px',
      padding: '18px 20px',
      boxShadow: '0 1px 4px rgba(0,0,0,0.07)',
    }}>
      <div style={{
        display: 'flex', alignItems: 'center', gap: '9px',
        marginBottom: '12px', paddingBottom: '10px',
        borderBottom: '1px solid #eeeeee',
      }}>
        <span style={{ fontSize: '18px', lineHeight: 1 }}>📝</span>
        <span style={{ fontWeight: '700', fontSize: '14px', color: '#111111' }}>Answer</span>
        <SpeakButton text={raw} language={language} />
      </div>
      <RichText text={expanded ? raw : raw.substring(0, PREVIEW) + (isLong ? '…' : '')} />
      {isLong && (
        <button onClick={() => setExpanded(v => !v)} style={{
          marginTop: '10px', background: 'none', border: 'none',
          color: '#444444', fontWeight: '600', fontSize: '13px',
          cursor: 'pointer', padding: 0, textDecoration: 'underline',
        }}>
          {expanded ? '↑ Show Less' : '↓ Show More'}
        </button>
      )}
    </div>
  );
};

/* ══════════════════════════════════════════════
   Main AnswerCard
══════════════════════════════════════════════ */
const AnswerCard = ({ answer }) => {
  const { problem, organic, inorganic, successTip, additionalTips, raw, language } = answer;
  const hasStructured = problem || organic || inorganic || successTip || additionalTips;

  if (!hasStructured && raw) return <RawCard raw={raw} language={language} />;

  return (
    <div style={{ width: '100%' }}>
      <DiagnosisBlock problem={problem} organic={organic} inorganic={inorganic} language={language} />
      {successTip && <SuccessTipCard text={successTip} language={language} />}
      {additionalTips && <AdditionalTipsCard text={additionalTips} language={language} />}
      {!hasStructured && raw && <RawCard raw={raw} language={language} />}
    </div>
  );
};

export default AnswerCard;
