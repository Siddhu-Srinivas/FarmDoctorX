import { useChatState, useChatDispatch } from '../context/ChatContext';
import { generateAnswer } from '../api/ragApi';
import parseResponse from '../utils/parseResponse';
import { saveToHistory } from '../api/historyApi';

export default function useChat() {
  const { history } = useChatState();
  const dispatch = useChatDispatch();

  async function sendMessage(query, solutionType, language = 'English') {
    if (!query || !query.trim()) {
      throw new Error('Query cannot be empty');
    }

    try {
      const data = await generateAnswer(query, solutionType, language);
      
      // Check if response contains an error
      if (data.error) {
        throw new Error(data.error);
      }
      
      const parsed = parseResponse(data);
      dispatch({ 
        type: 'ADD_MESSAGE', 
        payload: { user: query, ai: parsed } 
      });

      // Automatically save to history database
      try {
        await saveToHistory(query, data.raw_answer, solutionType);
        console.log('Conversation saved to history');
      } catch (historyError) {
        console.warn('Failed to save to history:', historyError.message);
        // Don't throw - history saving is not critical
      }
    } catch (error) {
      console.error('Error in sendMessage:', error);
      dispatch({ 
        type: 'ADD_MESSAGE', 
        payload: { user: query, ai: { error: error.message || 'Failed to generate answer' } } 
      });
      throw error;
    }
  }

  function clearHistory() {
    dispatch({ type: 'CLEAR_HISTORY' });
  }

  return { history, sendMessage, clearHistory };
}
