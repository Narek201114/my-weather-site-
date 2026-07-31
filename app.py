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
    try:
        return weather_mapping.get(int(code), "🔮 Անհայտ եղանակ")
    except:
        return "🔮 Անհայտ եղանակ"

def get_coordinates(city_name):
    if not city_name:
        return {"lat": 40.1792, "lon": 44.5152, "name": "Yerevan", "country": "Armenia"}

    if "," in city_name:
        try:
            parts = city_name.split(",")
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
            return {"lat": lat, "lon": lon, "name": f"📍 Կետ քարտեզի վրա", "country": "Ընտրված վայր"}
        except Exception as e:
            print(f"Lat/Lon parse error: {e}")

    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
    try:
        response = requests.get(geo_url, timeout=5)
        data = response.json()
        if response.status_code == 200 and "results" in data and len(data["results"]) > 0:
            result = data["results"][0]
            return {"lat": result["latitude"], "lon": result["longitude"], "name": result["name"], "country": result.get("country", "Unknown")}
    except Exception as e:
        print(f"Geocoding error: {e}")
    
    return {"lat": 40.1792, "lon": 44.5152, "name": "Yerevan", "country": "Armenia"}

@app.route('/', methods=['GET', 'POST'])
@app.route('/weather', methods=['GET', 'POST'])
def show_weather():
    city_query = "Yerevan"
    if request.method == 'POST':
        city_query = request.form.get('city', 'Yerevan').strip()

    geo_data = get_coordinates(city_query)

    weather_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": geo_data["lat"],
        "longitude": geo_data["lon"],
        "hourly": "temperature_2m,windspeed_10m,weathercode",
        "daily": "temperature_2m_max,temperature_2m_min,weathercode",
        "timezone": "auto"
    }
    
    try:
        response = requests.get(weather_url, params=params, timeout=5)
        data = response.json()
        
        # Վերցնում ենք ժամային տվյալների առաջին տարրը (հենց այս պահի ճշգրիտ ջերմաստիճանը)
        hourly = data.get("hourly", {})
        temps = hourly.get("temperature_2m", [0])
        winds = hourly.get("windspeed_10m", [0])
        codes = hourly.get("weathercode", [0])

        temp = temps[0] if temps else 0
        wind_speed = winds[0] if winds else 0
        weather_code = codes[0] if codes else 0
        weather_text = translate_weather_code(weather_code)

        forecast_days = []
        daily_data = data.get("daily", {})
        times = daily_data.get("time", [])
        max_temps = daily_data.get("temperature_2m_max", [])
        min_temps = daily_data.get("temperature_2m_min", [])
        daily_codes = daily_data.get("weathercode", [])

        for i in range(1, min(6, len(times))):
            forecast_days.append({
                "date": times[i],
                "max_temp": max_temps[i],
                "min_temp": min_temps[i],
                "condition": translate_weather_code(daily_codes[i])
            })
        
        return render_template(
            'weather.html',
            city_name=geo_data["name"],
            country_name=geo_data["country"],
            temp=temp, 
            wind_speed=wind_speed,
            weather_text=weather_text,
            forecast=forecast_days,
            error=None
        )
    except Exception as e:
        return f"Կրիտիկական սխալ: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
