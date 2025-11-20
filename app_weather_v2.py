from flask import Flask, render_template_string, request, jsonify
import requests
import html
from dotenv import load_dotenv # Import dotenv
import os # Import os

# --- 1. CONFIGURATION ----------------------------------------------------

load_dotenv() # Load variables from .env file

# Now we get the key from the environment variable!
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# External APIs
GEOCODING_API_URL = os.getenv('GEOCODING_API_URL')
WEATHER_API_URL = os.getenv('WEATHER_API_URL')
AIR_QUALITY_API_URL = os.getenv('AIR_QUALITY_API_URL')
GROQ_PROXY_URL = os.getenv('GROQ_PROXY_URL')

app = Flask(__name__)

# --- 2. HELPER FUNCTIONS  

def get_coordinates(city_name):
    """
    Uses Open-Meteo Geocoding API to find lat/long for a city name.
    """
    try:
        params = {'name': city_name, 'count': 1, 'language': 'en', 'format': 'json'}
        response = requests.get(GEOCODING_API_URL, params=params, timeout=5)
        data = response.json()
        
        if 'results' in data and len(data['results']) > 0:
            result = data['results'][0]
            return {
                'lat': result['latitude'], 
                'long': result['longitude'], 
                'name': result['name'], 
                'country': result.get('country', '')
            }
        return None
    except Exception as e:
        return None

def get_wmo_description(code):
    """Translates a WMO weather code into a description."""
    if code == 0: return "Clear sky"
    if code in (1, 2, 3): return "Partly cloudy"
    if code in (45, 48): return "Foggy"
    if code in (51, 53, 55, 56, 57): return "Drizzling"
    if code in (61, 63, 65, 66, 67): return "Raining"
    if code in (80, 81, 82): return "Rain showers"
    if code in (95, 96, 99): return "Thunderstorm"
    return "Unknown weather"

def fetch_weather_data(lat, long):
    """Fetches weather and air quality data."""
    # 1. Get Weather
    weather_params = {
        'latitude': lat, 
        'longitude': long, 
        'current_weather': 'true'
    }
    weather_res = requests.get(WEATHER_API_URL, params=weather_params, timeout=5)
    weather_data = weather_res.json()
    
    # 2. Get Air Quality (New Feature!)
    aqi_params = {
        'latitude': lat, 
        'longitude': long, 
        'current': 'us_aqi'
    }
    aqi_res = requests.get(AIR_QUALITY_API_URL, params=aqi_params, timeout=5)
    aqi_data = aqi_res.json()
    
    return {
        'temperature': weather_data['current_weather']['temperature'],
        'weathercode': weather_data['current_weather']['weathercode'],
        'description': get_wmo_description(weather_data['current_weather']['weathercode']),
        'aqi': aqi_data.get('current', {}).get('us_aqi', 'N/A')
    }

def generate_ai_summary(city, country, temp, desc, aqi):
    """Asks Groq for a friendly summary."""
    # Check if the key was loaded correctly
    if not GROQ_API_KEY or GROQ_API_KEY == 'YOUR_GROQ_API_KEY_HERE':
        return "Error: GROQ_API_KEY not set in .env file."

    prompt = (f"The weather in {city}, {country} is {temp}°C and {desc}. "
              f"The Air Quality Index (AQI) is {aqi}. "
              "Write a short, witty 2-sentence weather report for a visitor.")
    
    try:
        payload = {'api_key': GROQ_API_KEY, 'prompt': prompt}
        response = requests.post(GROQ_PROXY_URL, json=payload, timeout=10)
        data = response.json()
        return data.get('reply', 'No summary available.')
    except Exception as e:
        return f"AI Error: {str(e)}"

# --- 3. HTML TEMPLATE (Presentation) -------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather App V2</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-blue-50 min-h-screen flex flex-col items-center p-6">
    <div class="max-w-xl w-full bg-white rounded-3xl shadow-2xl overflow-hidden">
        <!-- Search Form -->
        <div class="bg-blue-600 p-6">
            <h1 class="text-3xl font-bold text-white text-center mb-4">Global Weather</h1>
            <form action="/" method="get" class="flex gap-2">
                <input type="text" name="city" placeholder="Enter city (e.g. Tokyo)" 
                       class="flex-1 p-3 rounded-lg focus:outline-none text-gray-800" required>
                <button type="submit" class="bg-yellow-400 text-blue-900 font-bold py-3 px-6 rounded-lg hover:bg-yellow-300 transition">
                    Search
                </button>
            </form>
        </div>

        <div class="p-8">
            {% if error %}
                <div class="bg-red-100 text-red-700 p-4 rounded-lg text-center font-bold">
                    {{ error }}
                </div>
            {% elif data %}
                <div class="text-center">
                    <h2 class="text-4xl font-bold text-gray-800 mb-1">{{ data.location.city }}</h2>
                    <p class="text-gray-500 uppercase tracking-wide text-sm mb-8">{{ data.location.country }}</p>
                    
                    <div class="flex justify-center items-center gap-4 mb-8">
                        <div class="text-7xl font-bold text-blue-600">{{ data.weather.temperature }}°</div>
                        <div class="text-left">
                            <div class="text-xl font-semibold text-gray-700">{{ data.weather.description }}</div>
                            <div class="text-sm text-gray-500">Air Quality: <span class="font-bold {{ 'text-green-500' if data.weather.aqi <= 50 else 'text-orange-500' }}">{{ data.weather.aqi }}</span></div>
                        </div>
                    </div>

                    <div class="bg-gray-100 p-6 rounded-xl border-l-4 border-blue-500 text-left">
                        <h3 class="text-xs font-bold text-gray-400 uppercase mb-2">AI Forecast</h3>
                        <p class="text-gray-700 italic" style="white-space: pre-wrap;">"{{ data.ai_summary }}"</p>
                    </div>
                </div>
                
                <div class="mt-8 pt-6 border-t border-gray-100 text-center text-xs text-gray-400">
                    <p>API Endpoint for Developers:</p> 
                    <code class="bg-gray-100 p-1 rounded">/api/weather?city={{ data.location.city }}</code>
                </div>
            {% else %}
                <div class="text-center text-gray-400 py-10">
                    Search for a city to see the forecast.
                </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

# --- 4. ROUTES (Controllers) ---------------------------------------------

@app.route("/")
def home():
    """
    The Human Interface (HTML). 
    Uses the exact same logic as the API, but formats it nicely for people.
    """
    city = request.args.get('city', 'Manila') # Default to Manila
    
    try:
        # 1. Geocode the city
        coords = get_coordinates(city)
        if not coords:
            return render_template_string(HTML_TEMPLATE, error=f"City '{city}' not found.", data=None)
        
        # 2. Get Data
        weather = fetch_weather_data(coords['lat'], coords['long'])
        
        # 3. Get AI Summary
        summary = generate_ai_summary(coords['name'], coords['country'], weather['temperature'], weather['description'], weather['aqi'])
        
        # 4. Bundle data for template
        full_data = {
            'location': {'city': coords['name'], 'country': coords['country']},
            'weather': weather,
            'ai_summary': summary
        }
        
        return render_template_string(HTML_TEMPLATE, data=full_data, error=None)

    except Exception as e:
        return render_template_string(HTML_TEMPLATE, error=str(e), data=None)


@app.route("/api/weather", methods=['GET'])
def api_weather():
    """
    The Machine Interface (RESTful API).
    Other developers can use this to get raw JSON data.
    """
    city = request.args.get('city')
    
    if not city:
        return jsonify({'status': 'error', 'message': 'Missing city parameter'}), 400
        
    try:
        # Reuse the exact same helper functions!
        coords = get_coordinates(city)
        if not coords:
            return jsonify({'status': 'error', 'message': 'City not found'}), 404
            
        weather = fetch_weather_data(coords['lat'], coords['long'])
        summary = generate_ai_summary(coords['name'], coords['country'], weather['temperature'], weather['description'], weather['aqi'])
        
        response = {
            'status': 'success',
            'location': coords,
            'data': weather,
            'summary': summary,
            'source': 'Manila Weather App API'
        }
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- 5. RUN SERVER -------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)