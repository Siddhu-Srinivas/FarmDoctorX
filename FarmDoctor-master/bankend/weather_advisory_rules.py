"""
Weather Advisory Rules Engine
Rule-based logic for generating crop advisories based on weather data
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict

@dataclass
class AdvisoryAlert:
    """Represents a single advisory alert"""
    title: str
    severity: str  # "low", "medium", "high"
    description: str
    recommendation: str
    action_required: bool

class AdvisoryRulesEngine:
    """
    Rule-based advisory engine for generating crop-specific recommendations
    based on weather data
    """
    
    # Thresholds for various conditions
    THRESHOLDS = {
        "irrigation_rain_low": 10,  # mm - below this suggests irrigation needed
        "irrigation_temp_high": 30,  # °C
        "irrigation_humidity_low": 40,  # %
        "heavy_rain": 25,  # mm
        "fungal_temp_min": 15,  # °C
        "fungal_temp_max": 25,  # °C
        "fungal_humidity": 80,  # %
        "frost_temp": 0,  # °C
        "pest_temp_min": 20,  # °C
        "pest_temp_max": 35,  # °C
        "pest_humidity": 60,  # %
        "wind_speed_high": 40,  # km/h
        "hail_wind_speed": 50,  # km/h
    }
    
    def __init__(self, crop_type: str = "general"):
        """
        Initialize the rules engine
        
        Args:
            crop_type: Type of crop (wheat, rice, tomato, cotton, sugarcane, etc.)
        """
        self.crop_type = crop_type.lower()
    
    def generate_advisories(self, weather_data: Dict, crop_type: str = None) -> Dict:
        """
        Generate complete advisory based on weather data
        
        Args:
            weather_data: Weather information from WeatherService
            crop_type: Optional crop type (overrides init value)
            
        Returns:
            Dictionary with comprehensive advisories
        """
        if crop_type:
            self.crop_type = crop_type.lower()
        
        irrigation_alerts = self._check_irrigation_needs(weather_data)
        disease_alerts = self._check_disease_risks(weather_data)
        pest_alerts = self._check_pest_risks(weather_data)
        weather_alerts = self._check_weather_hazards(weather_data)
        fertilizer_alerts = self._check_fertilizer_needs(weather_data)
        
        # Combine all alerts
        all_alerts = [
            *irrigation_alerts,
            *disease_alerts,
            *pest_alerts,
            *weather_alerts,
            *fertilizer_alerts
        ]
        
        # Generate action steps
        action_steps = self._generate_action_steps(all_alerts, weather_data)
        
        # Generate summary
        summary = self._generate_summary(weather_data, all_alerts)
        
        return {
            "location": weather_data.get("location", "Unknown"),
            "weather_summary": summary,
            "alerts": [asdict(alert) for alert in all_alerts],
            "irrigation_advice": self._get_irrigation_advice(weather_data),
            "disease_prevention": self._get_disease_prevention(weather_data),
            "pest_management": self._get_pest_management(weather_data),
            "action_steps": action_steps,
            "severity_level": self._calculate_severity(all_alerts),
            "safe_operations": self._get_safe_operations(weather_data),
        }
    
    def _check_irrigation_needs(self, weather: Dict) -> List[AdvisoryAlert]:
        """Check irrigation needs based on weather"""
        alerts = []
        rainfall = weather.get("rainfall", 0)
        temp = weather.get("temperature", 20)
        humidity = weather.get("humidity", 60)
        
        # High temperature + low rain + low humidity = irrigation needed
        if rainfall < self.THRESHOLDS["irrigation_rain_low"] and \
           temp > self.THRESHOLDS["irrigation_temp_high"]:
            alerts.append(AdvisoryAlert(
                title="Irrigation Required",
                severity="high",
                description=f"Temperature is high ({temp}°C) with low recent rainfall ({rainfall}mm). Soil moisture is likely depleted.",
                recommendation="Increase irrigation frequency. Water in early morning or late evening to minimize evaporation.",
                action_required=True
            ))
        
        # Heavy rain - no irrigation needed
        elif rainfall > self.THRESHOLDS["heavy_rain"]:
            alerts.append(AdvisoryAlert(
                title="Skip Irrigation",
                severity="low",
                description=f"Heavy rainfall detected ({rainfall}mm). Soil has sufficient moisture.",
                recommendation="Avoid irrigation for the next 2-3 days unless soil becomes too waterlogged.",
                action_required=False
            ))
        
        # Moderate conditions - normal irrigation
        else:
            alerts.append(AdvisoryAlert(
                title="Normal Irrigation Advised",
                severity="low",
                description=f"Weather conditions are moderate (Temp: {temp}°C, Rain: {rainfall}mm). Follow normal irrigation schedule.",
                recommendation="Continue regular irrigation based on crop water requirement and soil moisture.",
                action_required=False
            ))
        
        return alerts
    
    def _check_disease_risks(self, weather: Dict) -> List[AdvisoryAlert]:
        """Check fungal and disease risks"""
        alerts = []
        temp = weather.get("temperature", 20)
        humidity = weather.get("humidity", 60)
        rainfall = weather.get("rainfall", 0)
        
        # Fungal disease risk: warm, humid conditions
        if (self.THRESHOLDS["fungal_temp_min"] < temp < self.THRESHOLDS["fungal_temp_max"]) and \
           humidity > self.THRESHOLDS["fungal_humidity"] and \
           rainfall > 5:  # Recent moisture
            alerts.append(AdvisoryAlert(
                title="High Fungal Disease Risk",
                severity="high",
                description=f"Optimal fungal disease conditions: Temperature {temp}°C, Humidity {humidity}%, Recent rainfall. High risk for blight, powdery mildew, rust.",
                recommendation="Spray fungicide immediately. Increase spray frequency. Remove diseased leaves. Improve air circulation.",
                action_required=True
            ))
        
        # Late blight risk for potatoes/tomatoes
        if self.crop_type in ["tomato", "potato", "nightshade"] and \
           humidity > 85 and \
           15 < temp < 20:
            alerts.append(AdvisoryAlert(
                title="Late Blight Risk (Specific to Your Crop)",
                severity="high",
                description="Perfect conditions for late blight. Cool, wet weather is ideal for pathogen spread.",
                recommendation="Apply mancozeb or metalaxyl-based fungicides. Ensure good drainage. Remove lower leaves.",
                action_required=True
            ))
        
        # Moderate disease risk
        elif humidity > self.THRESHOLDS["fungal_humidity"] and \
             rainfall > 0:
            alerts.append(AdvisoryAlert(
                title="Moderate Disease Risk",
                severity="medium",
                description=f"High humidity ({humidity}%) with recent rainfall creates conditions favoring disease development.",
                recommendation="Monitor crops daily. Spray preventive fungicides. Remove affected plant parts immediately.",
                action_required=False
            ))
        
        # Low disease risk
        else:
            alerts.append(AdvisoryAlert(
                title="Low Disease Risk",
                severity="low",
                description="Current weather is unfavorable for major fungal diseases.",
                recommendation="Continue regular monitoring and preventive schedule.",
                action_required=False
            ))
        
        return alerts
    
    def _check_pest_risks(self, weather: Dict) -> List[AdvisoryAlert]:
        """Check pest risks"""
        alerts = []
        temp = weather.get("temperature", 20)
        humidity = weather.get("humidity", 60)
        wind_speed = weather.get("wind_speed", 0)
        
        # Pest risk: warm, humid conditions
        if temp > self.THRESHOLDS["pest_temp_min"] and \
           humidity > self.THRESHOLDS["pest_humidity"]:
            alerts.append(AdvisoryAlert(
                title="Moderate to High Pest Risk",
                severity="medium",
                description=f"Warm ({temp}°C) and humid ({humidity}%) conditions favor insect pest reproduction and activity.",
                recommendation="Increase scouting frequency. Apply appropriate insecticides. Use yellow sticky traps for monitoring. Release beneficial insects.",
                action_required=True
            ))
        
        # High temperature favors certain pests
        if temp > 35:
            alerts.append(AdvisoryAlert(
                title="Extreme Heat - Spider Mite Risk",
                severity="high",
                description=f"Very high temperature ({temp}°C) creates ideal conditions for spider mite outbreaks.",
                recommendation="Increase irrigation frequency. Spray water to cool plants. Use sulfur or insecticidal soap. Monitor regularly.",
                action_required=True
            ))
        
        # Low pest risk
        if temp < 15:
            alerts.append(AdvisoryAlert(
                title="Low Pest Activity",
                severity="low",
                description=f"Cool temperature ({temp}°C) reduces pest activity. Most insects are less active.",
                recommendation="Continue routine monitoring. No urgent pest control needed.",
                action_required=False
            ))
        
        return alerts
    
    def _check_weather_hazards(self, weather: Dict) -> List[AdvisoryAlert]:
        """Check severe weather hazards"""
        alerts = []
        temp = weather.get("temperature", 20)
        wind_speed = weather.get("wind_speed", 0)
        rainfall = weather.get("rainfall", 0)
        condition = weather.get("main_condition", "Clear")
        
        # Frost risk
        if temp < self.THRESHOLDS["frost_temp"]:
            alerts.append(AdvisoryAlert(
                title="Frost Alert",
                severity="high",
                description=f"Temperature below freezing ({temp}°C). Frost can damage tender crops.",
                recommendation="Use frost protection measures: sprinklers, heaters, mulch. Cover sensitive crops. Monitor through the night.",
                action_required=True
            ))
        
        # High wind risk
        if wind_speed > self.THRESHOLDS["wind_speed_high"]:
            alerts.append(AdvisoryAlert(
                title="High Wind Warning",
                severity="high",
                description=f"Strong winds ({wind_speed} km/h) can cause lodging, damage, and spray drift.",
                recommendation="Avoid pesticide spraying. Support tall crops. Delay harvest of delicate crops. Check staking and support systems.",
                action_required=True
            ))
        
        # Hail/severe weather risk
        if condition.lower() in ["thunderstorm", "rain", "heavy rain"] and \
           wind_speed > 30:
            alerts.append(AdvisoryAlert(
                title="Severe Weather Warning",
                severity="high",
                description="Severe thunderstorm conditions detected. Risk of hail and heavy rain.",
                recommendation="Harvest ripe fruits/vegetables immediately if possible. Ensure drainage systems are clear. Check crop supports.",
                action_required=True
            ))
        
        # Heavy rain waterlogging risk
        if rainfall > self.THRESHOLDS["heavy_rain"]:
            alerts.append(AdvisoryAlert(
                title="Waterlogging Risk",
                severity="medium",
                description=f"Heavy rainfall ({rainfall}mm) can cause waterlogging and root diseases.",
                recommendation="Ensure adequate drainage. Check for standing water. Monitor for root rot. Improve soil aeration.",
                action_required=True
            ))
        
        return alerts
    
    def _check_fertilizer_needs(self, weather: Dict) -> List[AdvisoryAlert]:
        """Check fertilizer needs based on weather"""
        alerts = []
        rainfall = weather.get("rainfall", 0)
        temp = weather.get("temperature", 20)
        
        # Heavy rain can wash away fertilizers
        if rainfall > self.THRESHOLDS["heavy_rain"]:
            alerts.append(AdvisoryAlert(
                title="Nutrient Loss Risk",
                severity="medium",
                description=f"Heavy rainfall ({rainfall}mm) can leach nitrogen from soil.",
                recommendation="Apply water-soluble nitrogen fertilizer 1-2 days after heavy rain to replenish lost nutrients. Use slow-release formulas.",
                action_required=True
            ))
        
        # High temperature increases nutrient demand
        if temp > 30:
            alerts.append(AdvisoryAlert(
                title="Increased Nutrient Demand",
                severity="medium",
                description=f"High temperature ({temp}°C) increases crop metabolic rate and nutrient uptake.",
                recommendation="Increase fertilizer frequency slightly. Use foliar feeds for quick nutrient availability. Monitor for nutrient deficiency symptoms.",
                action_required=False
            ))
        
        return alerts
    
    def _generate_action_steps(self, alerts: List[AdvisoryAlert], weather: Dict) -> List[str]:
        """Generate prioritized action steps"""
        actions = []
        critical_alerts = [a for a in alerts if a.action_required and a.severity == "high"]
        
        # Priority actions from critical alerts
        if critical_alerts:
            actions.append("⚠️ IMMEDIATE ACTIONS REQUIRED:")
            for alert in critical_alerts:
                actions.append(f"  • {alert.title}: {alert.recommendation}")
        
        # Standard actions
        actions.extend([
            "",
            "📋 TODAY'S FARMING SCHEDULE:",
            "  • Monitor crops for early signs of stress",
            "  • Check irrigation systems",
            "  • Inspect for pests and diseases",
            "  • Review weather forecast for next 3 days",
        ])
        
        # Additional actions based on conditions
        if weather.get("rainfall", 0) < 5 and weather.get("temperature", 20) > 25:
            actions.append("  • Schedule irrigation for early morning")
        
        if weather.get("humidity", 60) > 80:
            actions.append("  • Prepare fungicide spray for late evening")
        
        if weather.get("wind_speed", 0) > 20:
            actions.append("  • Delay pesticide spraying until wind reduces")
        
        return actions
    
    def _generate_summary(self, weather: Dict, alerts: List[AdvisoryAlert]) -> Dict:
        """Generate weather summary"""
        critical_count = len([a for a in alerts if a.severity == "high"])
        warning_count = len([a for a in alerts if a.severity == "medium"])
        
        return {
            "temperature": f"{weather.get('temperature', 0)}°C",
            "feels_like": f"{weather.get('feels_like', 0)}°C",
            "humidity": f"{weather.get('humidity', 0)}%",
            "rainfall": f"{weather.get('rainfall', 0)}mm",
            "wind_speed": f"{weather.get('wind_speed', 0)} km/h",
            "condition": weather.get("description", "Unknown"),
            "visibility": f"{weather.get('visibility', 10000)} meters",
            "critical_alerts": critical_count,
            "warning_alerts": warning_count,
        }
    
    def _get_irrigation_advice(self, weather: Dict) -> str:
        """Get specific irrigation advice"""
        rainfall = weather.get("rainfall", 0)
        temp = weather.get("temperature", 20)
        humidity = weather.get("humidity", 60)
        
        if rainfall > 20:
            return "Skip irrigation for next 2-3 days. Monitor soil moisture."
        elif temp > 30 and rainfall < 10:
            return "Increase irrigation. Water 2-3 times daily in small amounts. Early morning and evening preferred."
        elif 20 <= temp <= 30 and rainfall < 10:
            return "Normal irrigation schedule. Water once daily in morning or evening."
        else:
            return "Monitor soil moisture. Irrigate based on soil water availability."
    
    def _get_disease_prevention(self, weather: Dict) -> str:
        """Get disease prevention advice"""
        humidity = weather.get("humidity", 60)
        temp = weather.get("temperature", 20)
        
        if humidity > 85 and 15 < temp < 25:
            return "Critical: Spray fungicide immediately. Use copper-based or sulfur-based fungicides. Repeat every 7-10 days."
        elif humidity > 75 and 18 < temp < 28:
            return "High risk: Spray preventive fungicides. Ensure good air circulation. Remove lower leaves."
        elif humidity > 65:
            return "Moderate risk: Continue regular fungicide spraying schedule. Monitor daily for symptoms."
        else:
            return "Low risk: Continue routine monitoring. No urgent fungicide needed."
    
    def _get_pest_management(self, weather: Dict) -> str:
        """Get pest management advice"""
        temp = weather.get("temperature", 20)
        humidity = weather.get("humidity", 60)
        
        if temp > 30 and humidity > 70:
            return "High pest risk: Daily scouting required. Apply insecticides. Use pheromone traps for monitoring."
        elif 20 <= temp <= 30 and humidity > 60:
            return "Moderate risk: Scout crops every 2-3 days. Use integrated pest management. Spray if population exceeds threshold."
        else:
            return "Low risk: Routine scouting sufficient. Use preventive measures."
    
    def _calculate_severity(self, alerts: List[AdvisoryAlert]) -> str:
        """Calculate overall severity level"""
        critical = len([a for a in alerts if a.severity == "high"])
        if critical >= 2:
            return "CRITICAL"
        elif critical >= 1:
            return "HIGH"
        elif len([a for a in alerts if a.severity == "medium"]) >= 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_safe_operations(self, weather: Dict) -> List[str]:
        """Get list of safe farm operations"""
        operations = []
        wind = weather.get("wind_speed", 0)
        rain = weather.get("rainfall", 0)
        temp = weather.get("temperature", 20)
        
        if wind < 15:
            operations.append("✓ Pesticide spraying safe (low wind)")
        else:
            operations.append("✗ Avoid pesticide spraying (high wind)")
        
        if rain < 10:
            operations.append("✓ Harvesting safe (no/light rain)")
        else:
            operations.append("✗ Avoid harvesting (heavy rain expected)")
        
        if -5 < temp < 40:
            operations.append("✓ General outdoor work safe (moderate temperature)")
        else:
            operations.append("✗ Avoid outdoor work (extreme temperature)")
        
        return operations
