/**
 * Weather Advisory API Client
 * Handles all API calls to the weather advisory backend endpoints
 */

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance for weather endpoints
const weatherApi = axios.create({
  baseURL: API_URL + '/api/weather',
  timeout: 60000,  // Increased to 1 minute
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Check if the OpenWeatherMap API is configured on backend
 */
export const validateWeatherAPI = async () => {
  try {
    const response = await weatherApi.get('/validate-api');
    return response.data;
  } catch (error) {
    console.error('Error validating weather API:', error);
    throw error;
  }
};

/**
 * Get comprehensive weather-based crop advisory
 * @param {string} location - City name
 * @param {string} cropType - Type of crop (general, wheat, rice, tomato, etc.)
 * @param {boolean} includeForecast - Include 5-day forecast
 * @param {boolean} includeRagAdvice - Include RAG-enhanced advice
 * @returns {Promise<Object>} Advisory response
 */
export const getWeatherAdvisory = async (
  location,
  cropType = 'general',
  includeForecast = true,
  includeRagAdvice = true
) => {
  try {
    const response = await weatherApi.post('/advisory', {
      location,
      crop_type: cropType,
      include_forecast: includeForecast,
      include_rag_advice: includeRagAdvice,
    });

    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.error || 'Failed to get advisory');
    }
  } catch (error) {
    console.error('Error getting weather advisory:', error.response?.data || error.message);
    throw error;
  }
};

/**
 * Get current weather for a location
 * @param {string} location - City name
 * @returns {Promise<Object>} Current weather data
 */
export const getCurrentWeather = async (location) => {
  try {
    const response = await weatherApi.get('/current', {
      params: { location },
    });

    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error('Failed to get current weather');
    }
  } catch (error) {
    console.error('Error getting current weather:', error.response?.data || error.message);
    throw error;
  }
};

/**
 * Get weather forecast
 * @param {string} location - City name
 * @param {number} days - Number of days (1-5)
 * @returns {Promise<Object>} Forecast data
 */
export const getWeatherForecast = async (location, days = 5) => {
  try {
    const response = await weatherApi.get('/forecast', {
      params: { location, days: Math.min(days, 5) },
    });

    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error('Failed to get forecast');
    }
  } catch (error) {
    console.error('Error getting forecast:', error.response?.data || error.message);
    throw error;
  }
};

/**
 * Get crop-specific advisory
 * @param {string} location - Farm location
 * @param {string} crop - Crop type
 * @param {boolean} includeForecast - Include forecast
 * @returns {Promise<Object>} Crop-specific advisory
 */
export const getCropSpecificAdvisory = async (
  location,
  crop,
  includeForecast = true
) => {
  try {
    const response = await weatherApi.post('/crop-specific-advisory', {}, {
      params: {
        location,
        crop,
        include_forecast: includeForecast,
      },
    });

    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.error || 'Failed to get crop-specific advisory');
    }
  } catch (error) {
    console.error('Error getting crop-specific advisory:', error.response?.data || error.message);
    throw error;
  }
};

/**
 * Get advisory using GPS coordinates
 * @param {number} lat - Latitude
 * @param {number} lon - Longitude
 * @param {string} cropType - Crop type
 * @returns {Promise<Object>} Advisory response
 */
export const getAdvisoryByCoordinates = async (lat, lon, cropType = 'general') => {
  try {
    const response = await weatherApi.get('/advisory-by-coords', {
      params: {
        lat,
        lon,
        crop_type: cropType,
      },
    });

    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error('Failed to get advisory');
    }
  } catch (error) {
    console.error('Error getting advisory by coordinates:', error.response?.data || error.message);
    throw error;
  }
};

/**
 * Get quick alert summary
 * @param {string} location - City name
 * @returns {Promise<Object>} Alert summary
 */
export const getAlertSummary = async (location) => {
  try {
    const response = await weatherApi.get('/alert-summary', {
      params: { location },
    });

    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error('Failed to get alert summary');
    }
  } catch (error) {
    console.error('Error getting alert summary:', error.response?.data || error.message);
    throw error;
  }
};

/**
 * Get user's current location using geolocation API
 * @returns {Promise<{lat: number, lon: number}>} User coordinates
 */
export const getUserLocation = () => {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation not supported by browser'));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          lat: position.coords.latitude,
          lon: position.coords.longitude,
        });
      },
      (error) => {
        console.error('Geolocation error:', error);
        reject(error);
      }
    );
  });
};

export default {
  validateWeatherAPI,
  getWeatherAdvisory,
  getCurrentWeather,
  getWeatherForecast,
  getCropSpecificAdvisory,
  getAdvisoryByCoordinates,
  getAlertSummary,
  getUserLocation,
};
