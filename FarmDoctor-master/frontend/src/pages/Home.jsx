import React, { useRef, useEffect, useState } from 'react';
import ChatContainer from '../components/ChatContainer';
import useChat from '../hooks/useChat';

const Home = ({ pendingQuery }) => {
  const { history, sendMessage, clearHistory } = useChat();
  const chatContainerRef = useRef(null);
  const [isProcessing, setIsProcessing] = useState(false);

  // Handle re-running query from history
  useEffect(() => {
    if (pendingQuery && !isProcessing) {
      setIsProcessing(true);
      handleSelectFromHistory(pendingQuery.question, pendingQuery.solutionType);
    }
  }, [pendingQuery]);

  const handleSelectFromHistory = async (question, solutionType) => {
    try {
      // Send the query again
      await sendMessage(question, solutionType);
      
      // Scroll to view new message after a short delay to allow state update
      setTimeout(() => {
        if (chatContainerRef.current && chatContainerRef.current.scrollToBottom) {
          chatContainerRef.current.scrollToBottom();
        }
      }, 100);
    } catch (error) {
      console.error('Error re-running query:', error);
      alert('Failed to re-run query. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const backgroundStyle = {
    // Local background image in public folder: put your file at public/assistant-bg.png
    backgroundImage: "url('/assistant-bg.png')",
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundRepeat: 'no-repeat',
    // Add fallback for loading issues
    backgroundColor: '#f0fdf4', // Light green fallback
  };

  return (
    <div style={backgroundStyle} className="w-full h-screen flex flex-col">
      <ChatContainer ref={chatContainerRef} sendMessage={sendMessage} clearHistory={clearHistory} />
    </div>
  );
};

export default Home;
