"""
Weather Service Module
Fetches real-time weather data from OpenWeatherMap API
and provides structured weather information for advisory generation.
"""

import os
import json
import requests
from typing import Dict, Optional, Tuple
from datetime import datetime

class WeatherService:
    """
    Service for fetching weather data from OpenWeatherMap API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize WeatherService
        
        Args:
            api_key: OpenWeatherMap API key. If None, uses OPENWEATHER_API_KEY env var
        """
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY", "")
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
        self.timeout = 10
        
    def validate_api_key(self) -> bool:
        """Check if API key is configured"""
        return bool(self.api_key and len(self.api_key) > 0)
    
    def get_coordinates(self, location: str) -> Optional[Tuple[float, float]]:
        """
        Get latitude and longitude for a location using geocoding API
        
        Args:
            location: City name or location string
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            if not self.validate_api_key():
                raise ValueError("OpenWeatherMap API key not configured")
            
            # First try: Use current weather endpoint (has city name)
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                lat = data["coord"]["lat"]
                lon = data["coord"]["lon"]
                return (lat, lon)
            elif response.status_code == 404:
                return None
            else:
                raise Exception(f"API Error: {response.status_code}")
                
        except requests.RequestException as e:
            print(f"Error fetching coordinates: {e}")
            return None
        except Exception as e:
            print(f"Error in get_coordinates: {e}")
            return None
    
    def get_current_weather(self, location: str) -> Optional[Dict]:
        """
        Fetch current weather data for a location
        
        Args:
            location: City name or location string
            
        Returns:
            Dictionary with weather data or None if error
        """
        try:
            if not self.validate_api_key():
                raise ValueError("OpenWeatherMap API key not configured")
            
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric"  # Use Celsius
            }
            
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            
            if response.status_code != 200:
                raise Exception(f"API Error: {response.status_code} - {response.text}")
            
            data = response.json()
            
            # Extract relevant data
            weather_data = {
                "location": data.get("name", location),
                "country": data.get("sys", {}).get("country", ""),
                "latitude": data["coord"]["lat"],
                "longitude": data["coord"]["lon"],
                "temperature": round(data["main"]["temp"], 1),
                "feels_like": round(data["main"]["feels_like"], 1),
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "rainfall": self._extract_rainfall(data),
                "clouds": data.get("clouds", {}).get("all", 0),
                "wind_speed": round(data["wind"]["speed"], 1),
                "wind_direction": data["wind"].get("deg", 0),
                "description": data["weather"][0]["description"],
                "main_condition": data["weather"][0]["main"],
                "icon": data["weather"][0]["icon"],
                "timestamp": datetime.fromtimestamp(data["dt"]).isoformat(),
                "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).isoformat(),
                "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).isoformat(),
                "visibility": data.get("visibility", 10000),
                "uv_index": None  # Not available in free tier
            }
            
            return weather_data
            
        except requests.RequestException as e:
            print(f"Error fetching weather: {e}")
            return None
        except Exception as e:
            print(f"Error in get_current_weather: {e}")
            return None
    
    def get_forecast_weather(self, location: str, days: int = 5) -> Optional[Dict]:
        """
        Fetch weather forecast for a location
        
        Args:
            location: City name
            days: Number of days to forecast (1-5)
            
        Returns:
            Dictionary with forecast data or None
        """
        try:
            if not self.validate_api_key():
                raise ValueError("OpenWeatherMap API key not configured")
            
            coords = self.get_coordinates(location)
            if not coords:
                return None
            
            lat, lon = coords
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric",
                "cnt": days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = requests.get(self.forecast_url, params=params, timeout=self.timeout)
            
            if response.status_code != 200:
                raise Exception(f"API Error: {response.status_code}")
            
            data = response.json()
            forecasts = []
            
            for forecast_item in data["list"][:days * 8]:
                forecasts.append({
                    "timestamp": datetime.fromtimestamp(forecast_item["dt"]).isoformat(),
                    "temperature": round(forecast_item["main"]["temp"], 1),
                    "humidity": forecast_item["main"]["humidity"],
                    "rainfall": self._extract_rainfall(forecast_item),
                    "wind_speed": round(forecast_item["wind"]["speed"], 1),
                    "description": forecast_item["weather"][0]["description"],
                    "main_condition": forecast_item["weather"][0]["main"],
                })
            
            return {
                "location": location,
                "forecasts": forecasts,
                "retrieved_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error in get_forecast_weather: {e}")
            return None
    
    def _extract_rainfall(self, weather_data: Dict) -> float:
        """
        Extract rainfall amount from weather data
        
        Args:
            weather_data: Weather data dictionary
            
        Returns:
            Rainfall in mm (0 if no rain)
        """
        rainfall = 0.0
        
        # Check 3-hour rainfall
        if "rain" in weather_data:
            rainfall += weather_data["rain"].get("3h", 0)
        
        # Check 1-hour rainfall (less common)
        if "rain" in weather_data:
            rainfall += weather_data["rain"].get("1h", 0)
        
        return round(rainfall, 1)
    
    def get_weather_by_coordinates(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Fetch current weather by latitude and longitude
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary with weather data or None
        """
        try:
            if not self.validate_api_key():
                raise ValueError("OpenWeatherMap API key not configured")
            
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            
            if response.status_code != 200:
                raise Exception(f"API Error: {response.status_code}")
            
            data = response.json()
            
            weather_data = {
                "location": data.get("name", f"({lat}, {lon})"),
                "country": data.get("sys", {}).get("country", ""),
                "latitude": data["coord"]["lat"],
                "longitude": data["coord"]["lon"],
                "temperature": round(data["main"]["temp"], 1),
                "feels_like": round(data["main"]["feels_like"], 1),
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "rainfall": self._extract_rainfall(data),
                "clouds": data.get("clouds", {}).get("all", 0),
                "wind_speed": round(data["wind"]["speed"], 1),
                "wind_direction": data["wind"].get("deg", 0),
                "description": data["weather"][0]["description"],
                "main_condition": data["weather"][0]["main"],
                "icon": data["weather"][0]["icon"],
                "timestamp": datetime.fromtimestamp(data["dt"]).isoformat(),
                "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).isoformat(),
                "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).isoformat(),
                "visibility": data.get("visibility", 10000),
            }
            
            return weather_data
            
        except Exception as e:
            print(f"Error in get_weather_by_coordinates: {e}")
            return None


# Test function
if __name__ == "__main__":
    service = WeatherService()
    
    if not service.validate_api_key():
        print("⚠️ WARNING: OpenWeatherMap API key not configured")
        print("Set OPENWEATHER_API_KEY environment variable to use this service")
    else:
        # Test with a sample location
        weather = service.get_current_weather("New York")
        if weather:
            print(json.dumps(weather, indent=2))
        else:
            print("Failed to fetch weather")
