import os
import requests
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

# Ավտոմատ գտնում ենք այն թղթապանակի հասցեն, որտեղ գտնվում է այս app.py-ը
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
IMAGE_FOLDER = os.path.join(BASE_DIR, "images")

# Ստեղծում ենք Flask հավելվածը՝ ճիշտ մատնանշելով templates-ի տեղը
app = Flask(__name__, template_folder=TEMPLATE_DIR)
CORS(app)

# Եթե սերվերում images պապկան չկա, ավտոմատ ստեղծում ենք
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}

# Ֆունկցիա՝ քաղաքի անունը կոորդինատների վերածելու համար (Geocoding API)
def get_coordinates(city_name):
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=5&language=en&format=json"
    try:
        response = requests.get(geo_url, timeout=5)
        if response.status_code == 200 and "results" in response.json():
            result = response.json()["results"][0]
            return {
                "lat": result["latitude"],
                "lon": result["longitude"],
                "name": result["name"],
                "country": result.get("country", "Unknown")
            }
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None
    return None

# Գեղեցիկ և դինամիկ եղանակի էջը
@app.route('/weather', methods=['GET', 'POST'])
def show_weather():
    city_query = "Yerevan"
    error_message = None

    # Եթե օգտատերը որոնման դաշտում քաղաք է գրել
    if request.method == 'POST':
        city_query = request.form.get('city', 'Yerevan').strip()

    # 1. Գտնում ենք քաղաքի կոորդինատները
    geo_data = get_coordinates(city_query)
    
    if not geo_data:
        # Եթե քաղաքը չգտնվեց, որպես լռելյայն վերադառնում ենք Երևանին
        geo_data = get_coordinates("Yerevan")
        error_message = f"'{city_query}' քաղաքը համակարգում չի գտնվել: Ցուցադրվում է Երևանը:"

    # 2. Ստանում ենք եղանակի տվյալները Open-Meteo API-ից
    weather_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": geo_data["lat"],
        "longitude": geo_data["lon"],
        "current_weather": True
    }
    
    try:
        response = requests.get(weather_url, params=params, timeout=5)
        data = response.json()
        current = data["current_weather"]
        
        # Տվյալները փոխանցում ենք HTML էջին
        return render_template(
            'weather.html',
            city_name=geo_data["name"],
            country_name=geo_data["country"],
            temp=current['temperature'], 
            wind_speed=current['windspeed'],
            weather_code=current['weathercode'],
            error=error_message
        )
    except Exception as e:
        return f"Սխալ տվյալներ ստանալիս: {e}", 500

# Նկարների API հասցեն (POST)
@app.route('/api/images', methods=['POST'])
def get_images():
    image_list = [f for f in os.listdir(IMAGE_FOLDER) if os.path.splitext(f)[1].lower() in ALLOWED_EXTENSIONS]
