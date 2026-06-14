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

@app.route('/weather', methods=['GET', 'POST'])
def show_weather():
    city_query = "Yerevan"
    error_message = None

    if request.method == 'POST':
        city_query = request.form.get('city', 'Yerevan').strip()

    geo_data = get_coordinates(city_query)
    
    if not geo_data:
        geo_data = get_coordinates("Yerevan")
        error_message = f"'{city_query}' քաղաքը համակարգում չի գտնվել: Ցուցադրվում է Երևանը:"

    # Ավելացրել ենք daily պարամետրը 7 օրվա համար (որից կվերցնենք 5-ը)
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
        
        # Պատրաստում ենք 5 օրվա կանխատեսման տվյալները
        forecast_days = []
        if "daily" in data:
            daily_data = data["daily"]
            # Վերցնում ենք 1-ից մինչև 6-րդ օրերը (այսինքն՝ այսօրվանից հետո մոտակա 5 օրը)
            for i in range(1, 6):
                forecast_days.append({
                    "date": daily_data["time"][i],
                    "max_temp": daily_data["temperature_2m_max"][i],
                    "min_temp": daily_data["temperature_2m_min"][i],
                    "code": daily_data["weathercode"][i]
                })
        
        return render_template(
            'weather.html',
            city_name=geo_data["name"],
            country_name=geo_data["country"],
            temp=current['temperature'], 
            wind_speed=current['windspeed'],
            weather_code=current['weathercode'],
            forecast=forecast_days,  # Ուղարկում ենք HTML-ին
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
