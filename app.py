import os
import requests
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'my_secret_key_123'  # Փոխիր այս գաղտնաբառը քո ցանկությամբ

IMAGE_FOLDER = "images"
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

def translate_weather_code(code):
    weather_mapping = {
        0: "☀️ Պարզ երկինք", 1: "🌤️ Մեծ մասամբ պարզ", 2: "⛅ Փոփոխական ամպամածություն",
        3: "☁️ Ամպամած", 45: "🌫️ Մառախուղ", 48: "🌫️ Սառցե մառախուղ", 51: "🌧️ Թույլ մաղող անձրև",
        53: "🌧️ Մաղող անձրև", 55: "🌧️ Ուժեղ մաղող անձրև", 61: "🌧️ Թույլ անձրև",
        63: "🌧️ Անձրև", 65: "🌧️ Ուժեղ անձրև", 71: "🌨️ Թույլ ձյուն", 73: "🌨️ Ձյուն",
        75: "🌨️ Ուժեղ ձյուն", 77: "🌨️ Կարկուտ", 80: "🌦️ Թույլ անձրևային տեղումներ",
        81: "🌦️ Անձրևային տեղումներ", 82: "⛈️ Ուժեղ տեղումներ", 95: "⛈️ Ամպրոպ",
        96: "⛈️ Ամպրոպ և թույլ կարկուտ", 99: "⛈️ Ամպրոպ և ուժեղ կարկուտ"
    }
    return weather_mapping.get(code, "🔮 Անհայտ եղանակ")

def get_coordinates(city_name):
    if "," in city_name:
        try:
            lat, lon = city_name.split(",")
            lat, lon = lat.strip(), lon.strip()
            reverse_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=hy,en"
            response = requests.get(reverse_url, headers={'User-Agent': 'MyWeatherApp/1.0'}, timeout=5)
            if response.status_code == 200:
                geo_data = response.json()
                address = geo_data.get("address", {})
                place_name = address.get("village") or address.get("town") or address.get("city") or address.get("suburb") or address.get("county")
                return {"lat": float(lat), "lon": float(lon), "name": f"📍 {place_name or 'Կետ'}", "country": address.get("country", "Ընտրված վայր")}
        except Exception: return None

    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=5&language=en&format=json"
    try:
        response = requests.get(geo_url, timeout=5)
        if response.status_code == 200 and "results" in response.json():
            result = response.json()["results"][0]
            return {"lat": result["latitude"], "lon": result["longitude"], "name": result["name"], "country": result.get("country", "Unknown")}
    except Exception: return None
    return None

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == '1234': # Քո գաղտնաբառը
            session['logged_in'] = True
            return redirect(url_for('show_weather'))
    return render_template('login.html')

@app.route('/weather', methods=['GET', 'POST'])
def show_weather():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    city_query = "Yerevan"
    error_message = None
    if request.method == 'POST':
        city_query = request.form.get('city', 'Yerevan').strip()

    geo_data = get_coordinates(city_query)
    if not geo_data:
        geo_data = get_coordinates("Yerevan")
        error_message = f"'{city_query}' վայրը չի գտնվել:"

    weather_url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": geo_data["lat"], "longitude": geo_data["lon"], "current_weather": True, "daily": "temperature_2m_max,temperature_2m_min,weathercode", "timezone": "auto"}
    
    try:
        data = requests.get(weather_url, params=params, timeout=5).json()
        current = data["current_weather"]
        forecast_days = []
        for i in range(1, 6):
            forecast_days.append({
                "date": data["daily"]["time"][i],
                "max_temp": data["daily"]["temperature_2m_max"][i],
                "min_temp": data["daily"]["temperature_2m_min"][i],
                "condition": translate_weather_code(data["daily"]["weathercode"][i])
            })
        return render_template('weather.html', city_name=geo_data["name"], country_name=geo_data["country"], 
                               temp=current['temperature'], wind_speed=current['windspeed'], 
                               weather_text=translate_weather_code(current['weathercode']), 
                               forecast=forecast_days, error=error_message)
    except Exception as e:
        return f"Սխալ տվյալներ ստանալիս: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
