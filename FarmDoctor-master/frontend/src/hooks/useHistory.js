import { useState, useCallback } from 'react';
import {
  getAllHistory,
  deleteConversation,
  clearAllHistory,
  searchHistory,
  filterHistoryByType
} from '../api/historyApi';

export function useHistory() {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getAllHistory();
      setConversations(data);
    } catch (err) {
      setError(err.message || 'Failed to load history');
      console.error('Error loading history:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteItem = useCallback(async (conversationId) => {
    try {
      await deleteConversation(conversationId);
      setConversations((prev) =>
        prev.filter((item) => item.id !== conversationId)
      );
    } catch (err) {
      setError(err.message || 'Failed to delete conversation');
      console.error('Error deleting conversation:', err);
      throw err;
    }
  }, []);

  const clearHistory = useCallback(async () => {
    try {
      await clearAllHistory();
      setConversations([]);
    } catch (err) {
      setError(err.message || 'Failed to clear history');
      console.error('Error clearing history:', err);
      throw err;
    }
  }, []);

  const search = useCallback(async (query) => {
    setLoading(true);
    setError(null);
    try {
      const data = await searchHistory(query);
      setConversations(data);
    } catch (err) {
      setError(err.message || 'Failed to search history');
      console.error('Error searching history:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const filter = useCallback(async (solutionType) => {
    setLoading(true);
    setError(null);
    try {
      const data = await filterHistoryByType(solutionType);
      setConversations(data);
    } catch (err) {
      setError(err.message || 'Failed to filter history');
      console.error('Error filtering history:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    conversations,
    loading,
    error,
    loadHistory,
    deleteItem,
    clearHistory,
    search,
    filter
  };
}
