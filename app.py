import os
import requests
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

IMAGE_FOLDER = "images"
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}

if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

def translate_weather_code(code):
    weather_mapping = {
        0: "☀️ Պարզ երկինք",
        1: "🌤️ Մեծ մասամբ պարզ",
        2: "⛅ Փոփոխական ամպամածություն",
        3: "☁️ Ամպամած",
        45: "🌫️ Մառախուղ",
        48: "🌫️ Սառցե մառախուղ",
        51: "🌧️ Թույլ մաղող անձրև",
        53: "🌧️ Մաղող անձրև",
        55: "🌧️ Ուժեղ մաղող անձրև",
        61: "🌧️ Թույլ անձրև",
        63: "🌧️ Անձրև",
        65: "🌧️ Ուժեղ անձրև",
        71: "🌨️ Թույլ ձյուն",
        73: "🌨️ Ձյուն",
        75: "🌨️ Ուժեղ ձյուն",
        77: "🌨️ Կարկուտ",
        80: "🌦️ Թույլ անձրևային տեղումներ",
        81: "🌦️ Անձրևային տեղումներ",
        82: "⛈️ Ուժեղ տեղումներ",
        95: "⛈️ Ամպրոպ",
        96: "⛈️ Ամպրոպ և թույլ կարկուտ",
        99: "⛈️ Ամպրոպ և ուժեղ կարկուտ"
    }
    return weather_mapping.get(code, "🔮 Անհայտ եղանակ")

def get_coordinates(city_name):
    if "," in city_name:
        try:
            lat, lon = city_name.split(",")
            lat = lat.strip()
            lon = lon.strip()
            
            reverse_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=hy,en"
            headers = {'User-Agent': 'MyWeatherApp/1.0'}
            
            response = requests.get(reverse_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                geo_data = response.json()
                address = geo_data.get("address", {})
                
                place_name = address.get("village") or address.get("town") or address.get("city") or address.get("suburb") or address.get("county")
                country = address.get("country", "Unknown")
                
                if place_name:
                    return {
                        "lat": float(lat),
                        "lon": float(lon),
                        "name": f"📍 {place_name}",
                        "country": country
                    }
            
            return {
                "lat": float(lat),
                "lon": float(lon),
                "name": f"📍 Կետ քարտեզի վրա ({lat}, {lon})",
                "country": "Ընտրված վայր"
            }
        except Exception as e:
            print(f"Reverse geocoding error: {e}")
            return None

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

@app.route('/weather', methods=['GET', 'POST'])
def show_weather():
    city_query = "Yerevan"
    error_message = None

    if request.method == 'POST':
        city_query = request.form.get('city', 'Yerevan').strip()

    geo_data = get_coordinates(city_query)
    
    if not geo_data:
        geo_data = get_coordinates("Yerevan")
        error_message = f"'{city_query}' վայրը չի գտնվել: Ցուցադրվում է Երևանը:"

    weather_url = "https://api.open-meteo
