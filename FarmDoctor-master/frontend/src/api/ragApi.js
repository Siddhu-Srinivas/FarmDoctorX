import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  timeout: 120000  // Increased to 2 minutes for ML model processing
});

export async function generateAnswer(query, solutionType, language = 'English') {
  try {
    const payload = {
      query,
      solution_type: solutionType,
      language: language
    };
    
    console.log('Sending request to:', `${API_URL}/generate`);
    const response = await api.post('/generate', payload);
    console.log('Response received:', response.data);
    return response.data;
  } catch (error) {
    console.error('API Error:', error.message);
    if (error.response) {
      console.error('Response error:', error.response.data);
      throw new Error(`API Error: ${error.response.status} - ${error.response.statusText}`);
    } else if (error.request) {
      throw new Error('No response from server. Make sure backend is running on ' + API_URL);
    } else {
      throw error;
    }
  }
}
