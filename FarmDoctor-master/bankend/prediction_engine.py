"""
Predictive Analysis Engine for FarmDoctor
Generates dynamic predictions based on form inputs and weather data
"""

import math
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class PredictionEngine:
    """Rule-based prediction engine for agricultural forecasting"""
    
    # Crop characteristics
    CROP_DATA = {
        'rice': {
            'name': 'Rice',
            'avg_yield': 50,  # quintals/hectare
            'water_requirement': 1200,  # mm
            'temperature_optimal': (25, 30),  # Celsius
            'humidity_optimal': (70, 90),
            'diseases': ['Rice Blast', 'Bacterial Leaf Blight', 'Brown Spot'],
            'pests': ['Rice Stem Borer', 'Rice Leaf Folder', 'Brown Planthopper'],
            'season_suitability': {'kharif': 1.0, 'rabi': 0.6, 'summer': 0.3}
        },
        'wheat': {
            'name': 'Wheat',
            'avg_yield': 55,
            'water_requirement': 450,
            'temperature_optimal': (15, 25),
            'humidity_optimal': (40, 70),
            'diseases': ['Leaf Rust', 'Stem Rust', 'Powdery Mildew'],
            'pests': ['Armyworm', 'Wheat Aphid', 'Sawfly'],
            'season_suitability': {'rabi': 1.0, 'kharif': 0.2, 'summer': 0.1}
        },
        'maize': {
            'name': 'Maize',
            'avg_yield': 60,
            'water_requirement': 600,
            'temperature_optimal': (21, 29),
            'humidity_optimal': (60, 80),
            'diseases': ['Gray Leaf Spot', 'Turcicum Leaf Blight'],
            'pests': ['Fall Armyworm', 'Corn Borers'],
            'season_suitability': {'kharif': 0.9, 'rabi': 0.7, 'summer': 0.5}
        },
        'tomato': {
            'name': 'Tomato',
            'avg_yield': 45,
            'water_requirement': 400,
            'temperature_optimal': (20, 28),
            'humidity_optimal': (60, 85),
            'diseases': ['Early Blight', 'Late Blight', 'Septoria Leaf Spot'],
            'pests': ['Whiteflies', 'Thrips', 'Spider Mites'],
            'season_suitability': {'rabi': 1.0, 'summer': 0.8, 'kharif': 0.5}
        }
    }
    
    # Soil characteristics
    SOIL_DATA = {
        'loamy': {'water_retention': 0.9, 'fertility': 0.9, 'drainage': 0.9},
        'clay': {'water_retention': 1.0, 'fertility': 0.8, 'drainage': 0.5},
        'sandy': {'water_retention': 0.4, 'fertility': 0.6, 'drainage': 1.0},
        'silt': {'water_retention': 0.8, 'fertility': 0.85, 'drainage': 0.7}
    }
    
    @staticmethod
    def predict_yield(crop: str, region: str, soil: str, season: str, 
                     temperature: float, humidity: float, rainfall: float) -> Dict:
        """Predict crop yield based on environmental factors"""
        
        if crop not in PredictionEngine.CROP_DATA:
            return {'estimated': 'N/A', 'confidence': '0%', 'factors': []}
        
        crop_info = PredictionEngine.CROP_DATA[crop]
        base_yield = crop_info['avg_yield']
        
        # Calculate yield multipliers (0.5 to 1.5)
        # Temperature factor
        temp_range = crop_info['temperature_optimal']
        if temp_range[0] <= temperature <= temp_range[1]:
            temp_factor = 1.0
        else:
            deviation = min(abs(temperature - temp_range[0]), abs(temperature - temp_range[1]))
            temp_factor = max(0.5, 1.0 - (deviation * 0.05))
        
        # Humidity factor
        humidity_range = crop_info['humidity_optimal']
        if humidity_range[0] <= humidity <= humidity_range[1]:
            humidity_factor = 1.0
        else:
            deviation = min(abs(humidity - humidity_range[0]), abs(humidity - humidity_range[1]))
            humidity_factor = max(0.5, 1.0 - (deviation * 0.01))
        
        # Rainfall factor
        expected_rainfall = crop_info['water_requirement']
        if rainfall == 0:
            rainfall_factor = 0.4
        else:
            rainfall_ratio = rainfall / expected_rainfall
            if 0.8 <= rainfall_ratio <= 1.2:
                rainfall_factor = 1.0
            elif rainfall_ratio < 0.8:
                rainfall_factor = 0.5 + (rainfall_ratio * 0.625)
            else:
                rainfall_factor = min(1.0, 0.7 + (0.3 / (rainfall_ratio)))
        
        # Soil factor
        soil_score = PredictionEngine.SOIL_DATA.get(soil, {}).get('fertility', 0.8)
        
        # Season factor
        season_factor = crop_info['season_suitability'].get(season, 0.5)
        
        # Calculate final yield
        yield_multiplier = temp_factor * humidity_factor * rainfall_factor * soil_score * season_factor
        estimated_yield = base_yield * yield_multiplier
        
        # Confidence based on how aligned conditions are
        alignment = (abs(temp_factor - 1.0) + abs(humidity_factor - 1.0) + 
                    abs(rainfall_factor - 1.0)) / 3
        confidence = max(50, 100 - (alignment * 50))
        
        # Generate factors
        factors = []
        if temp_factor < 0.9:
            factors.append(f"Temperature deviation: {temperature:.1f}°C is not ideal - {int(temp_factor*100)}% impact")
        else:
            factors.append(f"Temperature {temperature:.1f}°C is optimal ✓")
        
        if humidity_factor < 0.9:
            factors.append(f"Humidity {humidity:.0f}% is not optimal - {int(humidity_factor*100)}% impact")
        else:
            factors.append(f"Humidity {humidity:.0f}% is suitable ✓")
        
        rainfall_percent = (rainfall / expected_rainfall) * 100
        if rainfall_factor < 0.9:
            factors.append(f"Rainfall {rainfall:.0f}mm is {rainfall_percent:.0f}% of requirement - Water stress risk")
        else:
            factors.append(f"Rainfall {rainfall:.0f}mm adequate for {crop} - Good coverage ✓")
        
        factors.append(f"Soil type ({soil.capitalize()}) - Good for {crop} cultivation")
        factors.append(f"Season: {season.capitalize()} is {'ideal' if season_factor > 0.8 else 'acceptable'} for {crop}")
        
        return {
            'estimated': f"{estimated_yield:.0f}-{estimated_yield*1.1:.0f} quintals/hectare",
            'confidence': f"{int(confidence)}%",
            'factors': factors
        }
    
    @staticmethod
    def predict_pest_risk(crop: str, temperature: float, humidity: float, 
                         season: str, rainfall: float) -> Dict:
        """Predict pest risk level"""
        
        if crop not in PredictionEngine.CROP_DATA:
            return {'riskLevel': 'UNKNOWN', 'confidence': '0%', 'factors': []}
        
        crop_info = PredictionEngine.CROP_DATA[crop]
        risk_score = 0
        max_score = 100
        
        # Temperature contribution (0-30 points)
        if 20 <= temperature <= 35:
            temp_risk = 30 * (1 - abs(temperature - 27) / 15)
        else:
            temp_risk = 0
        risk_score += temp_risk
        
        # Humidity contribution (0-30 points)
        if humidity >= 70:
            humidity_risk = 30 * min(1.0, (humidity - 60) / 40)
        else:
            humidity_risk = 15
        risk_score += humidity_risk
        
        # Season contribution (0-20 points)
        season_risk_map = {
            'kharif': 20,  # Peak pest season
            'rabi': 10,
            'summer': 5
        }
        risk_score += season_risk_map.get(season, 10)
        
        # Rainfall contribution (0-20 points)
        if rainfall > 800:
            rainfall_risk = 20
        elif rainfall > 500:
            rainfall_risk = 15
        else:
            rainfall_risk = 5
        risk_score += rainfall_risk
        
        # Determine risk level
        if risk_score < 25:
            risk_level = "LOW"
            color = "green"
        elif risk_score < 50:
            risk_level = "MODERATE"
            color = "yellow"
        elif risk_score < 75:
            risk_level = "HIGH"
            color = "orange"
        else:
            risk_level = "VERY HIGH"
            color = "red"
        
        # Generate factors
        factors = []
        pests = crop_info['pests']
        
        if humidity >= 80:
            factors.append(f"High humidity {humidity:.0f}% - Ideal for {pests[0] if pests else 'pests'}")
        if temperature >= 25:
            factors.append(f"Warm temperature {temperature:.0f}°C accelerates pest lifecycle")
        if season == 'kharif':
            factors.append("Monsoon season (Kharif) - High pest pressure expected")
        if rainfall > 800:
            factors.append(f"Heavy rainfall {rainfall:.0f}mm - Creates moist conditions for pests")
        
        factors.append(f"Recommended: Regular scouting for {pests[0] if pests else 'pests'}")
        factors.append(f"Preventive: Use neem-based products or beneficial insects")
        
        return {
            'riskLevel': f"{risk_level} ({int(risk_score)}%)",
            'confidence': f"{min(95, 70 + int(risk_score/2))}%",
            'factors': factors
        }
    
    @staticmethod
    def predict_disease(crop: str, temperature: float, humidity: float, 
                       season: str, soil: str) -> Dict:
        """Predict disease risk"""
        
        if crop not in PredictionEngine.CROP_DATA:
            return {'likelyDiseases': [], 'confidence': '0%', 'riskFactors': []}
        
        crop_info = PredictionEngine.CROP_DATA[crop]
        diseases = crop_info['diseases']
        risk_factors = []
        
        # Calculate disease susceptibility
        disease_risk = 0
        
        # Temperature factor
        if 15 <= temperature <= 28:
            disease_risk += 25
            risk_factors.append(f"Temperature {temperature:.0f}°C - Suitable for fungal diseases")
        
        # Humidity factor (most important)
        if humidity >= 80:
            disease_risk += 35
            risk_factors.append(f"High humidity {humidity:.0f}% - Critical for disease spread")
        elif humidity >= 70:
            disease_risk += 20
            risk_factors.append(f"Moderate humidity {humidity:.0f}% - Favorable for disease development")
        
        # Season factor
        season_disease_risk = {
            'kharif': 30,
            'rabi': 20,
            'summer': 5
        }
        disease_risk += season_disease_risk.get(season, 15)
        
        # Soil factor
        soil_drainage = PredictionEngine.SOIL_DATA.get(soil, {}).get('drainage', 0.7)
        if soil_drainage < 0.7:
            disease_risk += 10
            risk_factors.append(f"Soil type ({soil.capitalize()}) has poor drainage - Increases disease risk")
        
        # Determine likely diseases based on conditions
        likely_diseases = []
        if humidity >= 75 and temperature >= 20:
            likely_diseases.append(diseases[0] if len(diseases) > 0 else "Fungal Disease")
        if humidity >= 70 and temperature >= 15:
            likely_diseases.append(diseases[1] if len(diseases) > 1 else "Leaf Disease")
        if humidity >= 80:
            likely_diseases.append(diseases[2] if len(diseases) > 2 else "Secondary Disease")
        
        # Remove duplicates
        likely_diseases = list(set(likely_diseases))[:3]  # Top 3
        
        if not likely_diseases:
            likely_diseases = [diseases[0]] if diseases else ["Fungal Disease"]
        
        risk_factors.append("Prevention: Improve field drainage and air circulation")
        risk_factors.append("Action: Scout regularly and apply curative fungicides if needed")
        
        return {
            'likelyDiseases': likely_diseases,
            'confidence': f"{min(95, 60 + int(disease_risk/2))}%",
            'riskFactors': risk_factors
        }
    
    @staticmethod
    def predict_water_requirement(crop: str, temperature: float, humidity: float, 
                                 rainfall: float, season: str) -> Dict:
        """Predict water requirement for irrigation"""
        
        if crop not in PredictionEngine.CROP_DATA:
            return {'waterNeeded': 'N/A', 'confidence': '0%', 'schedule': []}
        
        crop_info = PredictionEngine.CROP_DATA[crop]
        base_water = crop_info['water_requirement']
        
        # Adjust based on temperature
        if temperature > 30:
            temp_multiplier = 1.3
        elif temperature > 25:
            temp_multiplier = 1.1
        elif temperature < 15:
            temp_multiplier = 0.7
        else:
            temp_multiplier = 1.0
        
        # Adjust based on humidity
        if humidity >= 80:
            humidity_multiplier = 0.6
        elif humidity >= 70:
            humidity_multiplier = 0.8
        elif humidity >= 50:
            humidity_multiplier = 1.0
        else:
            humidity_multiplier = 1.3
        
        # Adjust based on rainfall
        if rainfall >= 100:
            rainfall_reduction = min(rainfall / 100, 0.8)
        else:
            rainfall_reduction = 0
        
        # Calculate required water
        actual_water_need = base_water * temp_multiplier * humidity_multiplier * (1 - rainfall_reduction)
        weekly_water = actual_water_need / 25  # Assuming ~25 week crop cycle
        
        # Generate schedule based on crop growth stages
        schedule = []
        if crop == 'rice':
            schedule = [
                f"Week 1-4 (Establishment): {weekly_water*0.5:.0f}-{weekly_water*0.7:.0f} mm/week - Keep field flooded",
                f"Week 5-12 (Vegetative): {weekly_water*1.2:.0f}-{weekly_water*1.4:.0f} mm/week - Peak growth period",
                f"Week 13-16 (Flowering): {weekly_water*0.9:.0f}-{weekly_water*1.1:.0f} mm/week - Critical stage",
                f"Week 17-22 (Maturation): {weekly_water*0.4:.0f}-{weekly_water*0.6:.0f} mm/week - Reduce irrigation"
            ]
        elif crop == 'wheat':
            schedule = [
                f"Week 1-3 (Germination): {weekly_water*0.3:.0f}-{weekly_water*0.5:.0f} mm/week",
                f"Week 4-10 (Vegetative): {weekly_water*0.9:.0f}-{weekly_water*1.1:.0f} mm/week - 2-3 irrigations",
                f"Week 11-16 (Heading): {weekly_water*1.0:.0f}-{weekly_water*1.2:.0f} mm/week - Critical",
                f"Week 17-23 (Grain fill): {weekly_water*0.8:.0f}-{weekly_water*1.0:.0f} mm/week"
            ]
        else:
            schedule = [
                f"Initial growth: {weekly_water*0.6:.0f} mm/week",
                f"Vegetative phase: {weekly_water*1.2:.0f}-{weekly_water*1.4:.0f} mm/week",
                f"Flowering/fruiting: {weekly_water*1.0:.0f}-{weekly_water*1.2:.0f} mm/week (most critical)",
                f"Maturation: {weekly_water*0.5:.0f}-{weekly_water*0.7:.0f} mm/week"
            ]
        
        schedule.append(f"Adjust based on rainfall: Currently {rainfall:.0f}mm - Reduce irrigation accordingly")
        
        return {
            'waterNeeded': f"{weekly_water*0.8:.0f}-{weekly_water*1.2:.0f} mm/week (average across season)",
            'confidence': f"{min(95, 75 + int(humidity/10))}%",
            'schedule': schedule
        }
