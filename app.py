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
    # Եթե կոդը ստացել է կոորդինատներ (ստորակետով թվեր)
    if "," in city_name:
        try:
            lat, lon = city_name.split(",")
            lat = lat.strip()
            lon = lon.strip()
            
            # Դիմում ենք API-ին՝ կոորդինատով անունը գտնելու համար (Reverse Geocoding)
            reverse_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=hy,en"
            headers = {'User-Agent': 'MyWeatherApp/1.0'} # Պարտադիր է Nominatim-ի համար
            
            response = requests.get(reverse_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                geo_data = response.json()
                address = geo_data.get("address", {})
                
                # Փորձում ենք հերթով գտնել գյուղի, քաղաքի կամ շրջանի անունը
                place_name = address.get("village") or address.get("town") or address.get("city") or address.get("suburb") or address.get("county")
                country = address.get("country", "Unknown")
                
                if place_name:
                    return {
                        "lat": float(lat),
                        "lon": float(lon),
                        "name": f"📍 {place_name}",
                        "country": country
                    }
            
            # Եթե անունը չգտնվեց, թողնում ենք կոորդինատները
            return {
                "lat": float(lat),
                "lon": float(lon),
                "name": f"📍 Կետ քարտեզի վրա ({lat}, {lon})",
                "country": "Ընտրված վայր"
            }
        except Exception as e:
            print(f"Reverse geocoding error: {e}")
            return None

    # Եթե սովորական տեքստ է գրվել փնտրման դաշտում
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

    weather_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": geo_data["lat"],
        "longitude": geo_data["lon"],
        "current_weather": True,
        "daily": "temperature_2m_max,temperature_2m_min,weathercode",
        "timezone": "auto"
    }
    
    try:
        response = requests.get(weather_url, params=params, timeout=5)
        data = response.json()
        current = data["current_weather"]
        
        forecast_days = []
        if "daily" in data:
            daily_data = data["daily"]
            for i in range(1, 6):
                weather_text = translate_weather_code(daily_data["weathercode"][i])
                forecast_days.append({
                    "date": daily_data["time"][i],
                    "max_temp": daily_data["temperature_2m_max"][i],
                    "min_temp": daily_data["temperature_2m_min"][i],
                    "condition": weather_text
                })
        
        return render_template(
            'weather.html',
            city_name=geo_data["name"],
            country_name=geo_data["country"],
            temp=current['temperature'], 
            wind_speed=current['windspeed'],
            weather_text=translate_weather_code(current['weathercode']),
            forecast=forecast_days,
            error=error_message
        )
    except Exception as e:
        return f"Սխալ տվյալներ ստանալիս: {e}", 500

@app.route('/api/images', methods=['POST'])
def get_images():
    image_list = [f for f in os.listdir(IMAGE_FOLDER) if os.path.splitext(f)[1].lower() in ALLOWED_EXTENSIONS]
    return jsonify({
        "status": "success", 
        "total_images": len(image_list),
        "images": image_list
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
