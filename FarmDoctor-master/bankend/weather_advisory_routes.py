"""
Weather Advisory Routes
FastAPI endpoints for weather-based crop advisory system
Integrates with RAG pipeline for enhanced recommendations
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from weather_service import WeatherService
from weather_advisory_rules import AdvisoryRulesEngine
from answer_generation import generate_answer

router = APIRouter(prefix="/api/weather", tags=["weather"])

# Initialize services
weather_service = WeatherService()
advisory_engine = AdvisoryRulesEngine()


class WeatherAdvisoryRequest(BaseModel):
    """Request model for weather advisory"""
    location: str
    crop_type: Optional[str] = "general"
    include_forecast: Optional[bool] = False
    include_rag_advice: Optional[bool] = True


class WeatherAdvisoryResponse(BaseModel):
    """Response model for weather advisory"""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


@router.get("/validate-api")
async def validate_weather_api():
    """
    Validate if OpenWeatherMap API is configured
    
    Returns:
        Status of API configuration
    """
    is_valid = weather_service.validate_api_key()
    return {
        "api_configured": is_valid,
        "message": "OpenWeatherMap API is configured" if is_valid else "OpenWeatherMap API key not found. Set OPENWEATHER_API_KEY environment variable.",
        "setup_docs": "https://openweathermap.org/api"
    }


@router.post("/advisory")
async def get_weather_advisory(request: WeatherAdvisoryRequest):
    """
    Get comprehensive weather-based crop advisory
    
    Args:
        request: Advisory request with location and crop type
        
    Returns:
        Advisory response with weather data, alerts, and recommendations
    """
    try:
        # Validate API configuration
        if not weather_service.validate_api_key():
            raise HTTPException(
                status_code=400,
                detail="OpenWeatherMap API not configured. Set OPENWEATHER_API_KEY environment variable."
            )
        
        # Fetch current weather
        weather_data = weather_service.get_current_weather(request.location)
        if not weather_data:
            raise HTTPException(
                status_code=404,
                detail=f"Location '{request.location}' not found. Please check spelling or try another location."
            )
        
        # Generate rule-based advisory
        advisory = advisory_engine.generate_advisories(weather_data, request.crop_type)
        
        # Optional: Fetch forecast
        forecast_data = None
        if request.include_forecast:
            forecast_data = weather_service.get_forecast_weather(request.location, days=5)
        
        # Optional: Enhance with RAG-based advice
        rag_advice = None
        if request.include_rag_advice:
            rag_advice = _generate_rag_advisory(weather_data, request.crop_type, advisory)
        
        # Combine all data
        response_data = {
            "location": weather_data.get("location"),
            "country": weather_data.get("country"),
            "timestamp": weather_data.get("timestamp"),
            "weather_summary": advisory["weather_summary"],
            "alerts": advisory["alerts"],
            "irrigation_advice": advisory["irrigation_advice"],
            "disease_prevention": advisory["disease_prevention"],
            "pest_management": advisory["pest_management"],
            "action_steps": advisory["action_steps"],
            "safe_operations": advisory["safe_operations"],
            "severity_level": advisory["severity_level"],
            "crop_type": request.crop_type,
            "raw_weather_data": {
                "temperature": weather_data.get("temperature"),
                "humidity": weather_data.get("humidity"),
                "rainfall": weather_data.get("rainfall"),
                "wind_speed": weather_data.get("wind_speed"),
                "clouds": weather_data.get("clouds"),
                "visibility": weather_data.get("visibility"),
            },
            "forecast": forecast_data,
            "rag_enhanced_advice": rag_advice,
        }
        
        return WeatherAdvisoryResponse(success=True, data=response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating advisory: {str(e)}")


@router.get("/current")
async def get_current_weather(location: str = Query(..., description="City name or location")):
    """
    Get current weather for a location
    
    Args:
        location: City name
        
    Returns:
        Current weather data
    """
    try:
        if not weather_service.validate_api_key():
            raise HTTPException(
                status_code=400,
                detail="OpenWeatherMap API not configured"
            )
        
        weather = weather_service.get_current_weather(location)
        if not weather:
            raise HTTPException(status_code=404, detail=f"Location '{location}' not found")
        
        return WeatherAdvisoryResponse(success=True, data=weather)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast")
async def get_forecast(
    location: str = Query(..., description="City name"),
    days: int = Query(5, ge=1, le=5, description="Number of days (1-5)")
):
    """
    Get weather forecast for a location
    
    Args:
        location: City name
        days: Number of days to forecast
        
    Returns:
        Forecast data
    """
    try:
        if not weather_service.validate_api_key():
            raise HTTPException(
                status_code=400,
                detail="OpenWeatherMap API not configured"
            )
        
        forecast = weather_service.get_forecast_weather(location, days=days)
        if not forecast:
            raise HTTPException(status_code=404, detail=f"Could not fetch forecast for '{location}'")
        
        return WeatherAdvisoryResponse(success=True, data=forecast)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crop-specific-advisory")
async def get_crop_specific_advisory(
    location: str = Query(..., description="Farm location"),
    crop: str = Query(..., description="Crop type (wheat, rice, tomato, potato, cotton, etc.)"),
    include_forecast: bool = Query(False, description="Include 5-day forecast")
):
    """
    Get crop-specific weather advisory
    
    Args:
        location: Farm location
        crop: Crop type
        include_forecast: Whether to include forecast
        
    Returns:
        Crop-specific advisory
    """
    request = WeatherAdvisoryRequest(
        location=location,
        crop_type=crop,
        include_forecast=include_forecast,
        include_rag_advice=True
    )
    return await get_weather_advisory(request)


@router.get("/advisory-by-coords")
async def get_advisory_by_coordinates(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    crop_type: str = Query("general", description="Crop type")
):
    """
    Get weather advisory using GPS coordinates
    
    Args:
        lat: Latitude
        lon: Longitude
        crop_type: Crop type
        
    Returns:
        Advisory for that location
    """
    try:
        if not weather_service.validate_api_key():
            raise HTTPException(
                status_code=400,
                detail="OpenWeatherMap API not configured"
            )
        
        weather_data = weather_service.get_weather_by_coordinates(lat, lon)
        if not weather_data:
            raise HTTPException(status_code=404, detail="Location not found")
        
        # Generate advisory
        advisory = advisory_engine.generate_advisories(weather_data, crop_type)
        
        # RAG-enhanced advice
        rag_advice = _generate_rag_advisory(weather_data, crop_type, advisory)
        
        response_data = {
            "location": weather_data.get("location"),
            "coordinates": {"lat": lat, "lon": lon},
            "weather_summary": advisory["weather_summary"],
            "alerts": advisory["alerts"],
            "irrigation_advice": advisory["irrigation_advice"],
            "disease_prevention": advisory["disease_prevention"],
            "pest_management": advisory["pest_management"],
            "action_steps": advisory["action_steps"],
            "severity_level": advisory["severity_level"],
            "rag_enhanced_advice": rag_advice,
        }
        
        return WeatherAdvisoryResponse(success=True, data=response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alert-summary")
async def get_alert_summary(location: str = Query(..., description="City name")):
    """
    Get quick alert summary for a location
    
    Returns only critical alerts and action items
    
    Args:
        location: City name
        
    Returns:
        Alert summary
    """
    try:
        if not weather_service.validate_api_key():
            raise HTTPException(status_code=400, detail="API not configured")
        
        weather = weather_service.get_current_weather(location)
        if not weather:
            raise HTTPException(status_code=404, detail=f"Location '{location}' not found")
        
        advisory = advisory_engine.generate_advisories(weather)
        
        # Filter critical information only
        critical_alerts = [a for a in advisory["alerts"] if a["severity"] in ["high", "medium"]]
        
        return WeatherAdvisoryResponse(success=True, data={
            "location": location,
            "severity": advisory["severity_level"],
            "critical_alerts": critical_alerts,
            "immediate_actions": [s for s in advisory["action_steps"] if "IMMEDIATE" in s] or \
                               [advisory["action_steps"][0]] if advisory["action_steps"] else [],
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _generate_rag_advisory(weather_data: dict, crop_type: str, advisory: dict) -> Optional[str]:
    """
    Generate RAG-enhanced advisory using the existing RAG pipeline
    
    Args:
        weather_data: Current weather data
        crop_type: Type of crop
        advisory: Rule-based advisory
        
    Returns:
        Extended advisory from RAG system
    """
    try:
        # Build context prompt with weather data
        context = f"""
Based on current weather conditions, provide detailed farming advice:

Location: {weather_data.get('location', 'Unknown')}
Temperature: {weather_data.get('temperature', 'N/A')}°C
Humidity: {weather_data.get('humidity', 'N/A')}%
Rainfall: {weather_data.get('rainfall', 'N/A')}mm
Wind Speed: {weather_data.get('wind_speed', 'N/A')} km/h
Weather Condition: {weather_data.get('description', 'N/A')}
Crop Type: {crop_type}

Severity Level: {advisory.get('severity_level', 'Unknown')}

Current Alerts Summary:
- Irrigation: {advisory.get('irrigation_advice', 'N/A')}
- Disease Risk: {advisory.get('disease_prevention', 'N/A')}
- Pest Risk: {advisory.get('pest_management', 'N/A')}

Provide detailed, actionable farming recommendations considering these weather conditions and the identified risks.
"""
        
        # Call RAG pipeline with weather context
        # ``generate_answer`` currently returns a tuple (answer_text, docs)
        rag_response = generate_answer(context)
        
        # unpack the tuple safely
        if isinstance(rag_response, tuple) and len(rag_response) >= 1:
            answer_text = rag_response[0]
        else:
            # if some other format is returned, just use it directly
            answer_text = rag_response

        if answer_text:
            return answer_text
        else:
            return None
            
    except Exception as e:
        # log the error to console for easier debugging
        print(f"Error generating RAG advisory: {e}")
        return None
