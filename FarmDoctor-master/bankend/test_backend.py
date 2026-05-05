import requests
import json

url = "http://localhost:8000/generate"
payload = {
    "query": "how to treat rice blast",
    "solution_type": "Both",
    "language": "English"
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
