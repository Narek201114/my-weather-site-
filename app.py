import os
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

IMAGE_FOLDER = "images"
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
            return {"lat": float(lat.strip()), "lon": float(lon.strip()), "name": f"📍 Կետ քարտեզի վրա", "country": "Ընտրված վայր"}
        except:
            pass

    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
    try:
        response = requests.get(geo_url, timeout=5)
        if response.status_code == 200 and "results" in response.json():
            result = response.json()["results"][0]
            return {"lat": result["latitude"], "lon": result["longitude"], "name": result["name"], "country": result.get("country", "Unknown")}
    except Exception as e:
        print(f"Geocoding error: {e}")
    
    # Եթե ամեն ինչ ձախողվի, վերադարձնել Երևանը
    return {"lat": 40.1792, "lon": 44.5152, "name": "Yerevan", "country": "Armenia"}

@app.route('/', methods=['GET', 'POST'])
@app.route('/weather', methods=['GET', 'POST'])
def show_weather():
    city_query = "Yerevan"
    error_message = None

    if request.method == 'POST':
        city_query = request.form.get('city', 'Yerevan').strip()

    geo_data = get_coordinates(city_query)

    weather_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": geo_data["lat"],
        "longitude": geo_data["lon"],
        "current_weather": "true",
        "timezone": "auto"
    }
    
    try:
        response = requests.get(weather_url, params=params, timeout=5)
        data = response.json()
        
        # Անվտանգ ստուգում
        current = data.get("current_weather", {"temperature": 0, "windspeed": 0, "weathercode": 0})
        
        return render_template(
            'weather.html',
            city_name=geo_data["name"],
            country_name=geo_data["country"],
            temp=current.get('temperature', 0), 
            wind_speed=current.get('windspeed', 0),
            weather_text=translate_weather_code(current.get('weathercode', 0)),
            forecast=[],
            error=error_message
        )
    except Exception as e:
        return f"Սխալ տվյալներ ստանալիս: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
