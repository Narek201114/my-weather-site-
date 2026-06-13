import os
import requests
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

# Մաքուր և ստանդարտ Flask: Այն ավտոմատ կգտնի քո templates պապկան
app = Flask(__name__)
CORS(app)

IMAGE_FOLDER = "images"
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}

# Ստեղծում ենք images պապկան, եթե չկա
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
