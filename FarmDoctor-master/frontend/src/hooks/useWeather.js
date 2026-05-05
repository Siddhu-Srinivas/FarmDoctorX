/**
 * useWeather Hook
 * Custom React hook for managing weather advisory state and operations
 */

import { useState, useCallback } from 'react';
import {
  getWeatherAdvisory,
  getCurrentWeather,
  getWeatherForecast,
  getCropSpecificAdvisory,
  getAdvisoryByCoordinates,
  getAlertSummary,
  getUserLocation,
} from '../api/weatherApi';

export const useWeather = () => {
  const [location, setLocation] = useState('');
  const [cropType, setCropType] = useState('general');
  const [currentWeather, setCurrentWeather] = useState(null);
  const [advisory, setAdvisory] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [alertSummary, setAlertSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  /**
   * Fetch advisory for given location and crop
   */
  const fetchAdvisory = useCallback(async (loc = location, crop = cropType, includeForecast = true) => {
    if (!loc.trim()) {
      setError('Please enter a location');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const data = await getWeatherAdvisory(loc, crop, includeForecast, true);
      setAdvisory(data);
      setCurrentWeather(data.raw_weather_data);
      if (data.forecast) {
        setForecast(data.forecast);
      }
      setSuccess(true);
      console.log('Advisory fetched successfully:', data);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to fetch advisory';
      setError(errorMsg);
      console.error('Error fetching advisory:', errorMsg);
    } finally {
      setLoading(false);
    }
  }, [location, cropType]);

  /**
   * Fetch current weather only
   */
  const fetchCurrentWeather = useCallback(async (loc = location) => {
    if (!loc.trim()) {
      setError('Please enter a location');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await getCurrentWeather(loc);
      setCurrentWeather(data);
      setSuccess(true);
      console.log('Current weather fetched:', data);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to fetch weather';
      setError(errorMsg);
      console.error('Error fetching weather:', errorMsg);
    } finally {
      setLoading(false);
    }
  }, [location]);

  /**
   * Fetch weather forecast
   */
  const fetchForecast = useCallback(async (loc = location, days = 5) => {
    if (!loc.trim()) {
      setError('Please enter a location');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await getWeatherForecast(loc, days);
      setForecast(data);
      setSuccess(true);
      console.log('Forecast fetched:', data);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to fetch forecast';
      setError(errorMsg);
      console.error('Error fetching forecast:', errorMsg);
    } finally {
      setLoading(false);
    }
  }, [location]);

  /**
   * Fetch crop-specific advisory
   */
  const fetchCropSpecificAdvisory = useCallback(async (loc = location, crop = cropType) => {
    if (!loc.trim()) {
      setError('Please enter a location');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await getCropSpecificAdvisory(loc, crop, true);
      setAdvisory(data);
      setCurrentWeather(data.raw_weather_data);
      setSuccess(true);
      console.log('Crop-specific advisory fetched:', data);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to fetch crop advisory';
      setError(errorMsg);
      console.error('Error fetching crop advisory:', errorMsg);
    } finally {
      setLoading(false);
    }
  }, [location, cropType]);

  /**
   * Fetch alert summary only
   */
  const fetchAlertSummary = useCallback(async (loc = location) => {
    if (!loc.trim()) {
      setError('Please enter a location');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await getAlertSummary(loc);
      setAlertSummary(data);
      setSuccess(true);
      console.log('Alert summary fetched:', data);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to fetch alerts';
      setError(errorMsg);
      console.error('Error fetching alerts:', errorMsg);
    } finally {
      setLoading(false);
    }
  }, [location]);

  /**
   * Fetch advisory using user's current GPS coordinates
   */
  const fetchAdvisoryByGPS = useCallback(async (crop = cropType) => {
    setLoading(true);
    setError(null);

    try {
      const coords = await getUserLocation();
      const data = await getAdvisoryByCoordinates(coords.lat, coords.lon, crop);
      setAdvisory(data);
      setLocation(data.location);
      setSuccess(true);
      console.log('GPS-based advisory fetched:', data);
    } catch (err) {
      const errorMsg = err.message || 'Failed to get location or advisory';
      setError(errorMsg);
      console.error('Error fetching GPS advisory:', errorMsg);
    } finally {
      setLoading(false);
    }
  }, [cropType]);

  /**
   * Clear all data
   */
  const clearData = useCallback(() => {
    setLocation('');
    setCropType('general');
    setCurrentWeather(null);
    setAdvisory(null);
    setForecast(null);
    setAlertSummary(null);
    setError(null);
    setSuccess(false);
  }, []);

  /**
   * Clear error message
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    // State
    location,
    cropType,
    currentWeather,
    advisory,
    forecast,
    alertSummary,
    loading,
    error,
    success,

    // Setters
    setLocation,
    setCropType,
    setCurrentWeather,
    setAdvisory,
    setForecast,

    // Actions
    fetchAdvisory,
    fetchCurrentWeather,
    fetchForecast,
    fetchCropSpecificAdvisory,
    fetchAlertSummary,
    fetchAdvisoryByGPS,
    clearData,
    clearError,
  };
};

export default useWeather;
