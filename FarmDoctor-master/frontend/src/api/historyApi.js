import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const historyApi = axios.create({
  baseURL: `${API_URL}/api/history`,
  timeout: 30000  // Increased timeout
});

export async function saveToHistory(question, answer, solutionType) {
  try {
    const response = await historyApi.post('/save', {
      question,
      answer,
      solution_type: solutionType
    });
    return response.data;
  } catch (error) {
    console.error('Error saving to history:', error);
    throw error;
  }
}

export async function getAllHistory() {
  try {
    const response = await historyApi.get('/all');
    return response.data.conversations || [];
  } catch (error) {
    console.error('Error fetching history:', error);
    throw error;
  }
}

export async function getPaginatedHistory(page = 1, perPage = 20) {
  try {
    const response = await historyApi.get('/paginated', {
      params: { page, per_page: perPage }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching paginated history:', error);
    throw error;
  }
}

export async function getConversation(conversationId) {
  try {
    const response = await historyApi.get(`/${conversationId}`);
    return response.data.conversation;
  } catch (error) {
    console.error('Error fetching conversation:', error);
    throw error;
  }
}

export async function deleteConversation(conversationId) {
  try {
    const response = await historyApi.delete(`/${conversationId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting conversation:', error);
    throw error;
  }
}

export async function clearAllHistory() {
  try {
    const response = await historyApi.delete('');
    return response.data;
  } catch (error) {
    console.error('Error clearing history:', error);
    throw error;
  }
}

export async function searchHistory(query) {
  try {
    const response = await historyApi.get('/search', {
      params: { q: query }
    });
    return response.data.conversations || [];
  } catch (error) {
    console.error('Error searching history:', error);
    throw error;
  }
}

export async function filterHistoryByType(solutionType) {
  try {
    const response = await historyApi.get(`/filter/${solutionType}`);
    return response.data.conversations || [];
  } catch (error) {
    console.error('Error filtering history:', error);
    throw error;
  }
}
