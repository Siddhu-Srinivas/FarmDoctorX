import requests, os
api = os.getenv('OPENWEATHER_API_KEY')
print('api', api)
locs = ['Delhi', 'New Delhi', 'Delhi,in', 'New Delhi,in']
for loc in locs:
    r = requests.get('https://api.openweathermap.org/data/2.5/weather', params={'q': loc, 'appid': api, 'units': 'metric'})
    print(loc, r.status_code, r.text[:200])
