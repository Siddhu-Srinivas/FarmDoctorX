import requests
import json

response = requests.post('http://localhost:8000/predict', json={
    'cropType': 'rice',
    'region': 'west_bengal',
    'soilType': 'loamy',
    'season': 'kharif',
    'temperature': 25.0,
    'humidity': 70.0,
    'rainfall': 1200.0
})

data = response.json()
print("\n=== YIELD PREDICTION ===")
print(json.dumps(data['predictions']['yield'], indent=2))

print("\n=== PEST RISK ===")
print(json.dumps(data['predictions']['pest_risk'], indent=2))

print("\n=== DISEASE RISK ===")
print(json.dumps(data['predictions']['disease_risk'], indent=2))

print("\n=== WATER REQUIREMENT ===")
print(json.dumps(data['predictions']['water_requirement'], indent=2))
