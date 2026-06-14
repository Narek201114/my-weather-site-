from flask import Flask, render_template, request, redirect, url_for
import requests
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'weather_secret_key_2026')

# Քո OpenWeather API բանալին
API_KEY = 'b7376e7399b3986a7ffc33eb6c34a6ef'

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('weather'))
    return render_template('login.html')

@app.route('/weather', methods=['GET', 'POST'])
def weather():
    # Սկզբնական արժեքներ՝ սխալներից խուսափելու համար
    city_name = "Ընտրեք քաղաք"
    country_name = ""
    temp = "--"
    wind_speed = "0"
    weather_text = "Սպասում է ընտրության"
    forecast = []
    error = None

    if request.method == 'POST':
        search_query = request.form.get('city', '').strip()
        
        if search_query:
            # Քարտեզից եկած կոորդինատների մշակում
            if ',' in search_query:
                try:
                    lat, lon = search_query.split(',')
                    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=am"
                    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=am"
                except ValueError:
                    error = "Կոորդինատների սխալ ձևաչափ։"
            else:
                # Քաղաքի անունով որոնում
                url = f"https://api.openweathermap.org/data/2.5/weather?q={search_query}&appid={API_KEY}&units=metric&lang=am"
                forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={search_query}&appid={API_KEY}&units=metric&lang=am"

            if not error:
                try:
                    res = requests.get(url, timeout=10)
                    if res.status_code == 200:
                        data = res.json()
                        city_name = data.get('name', 'Անհայտ')
                        country_name = data.get('sys', {}).get('country', '')
                        temp = round(data.get('main', {}).get('temp', 0))
                        wind_speed = round(data.get('wind', {}).get('speed', 0) * 3.6)
                        weather_text = data.get('weather', [{}])[0].get('description', '').capitalize()
                        
                        # 5 օրվա կանխատեսման մշակում
                        f_res = requests.get(forecast_url, timeout=10)
                        if f_res.status_code == 200:
                            f_data = f_res.json()
                            for item in f_data.get('list', [])[::8]:
                                forecast.append({
                                    'date': item.get('dt_txt', '').split(' ')[0],
                                    'condition': item.get('weather', [{}])[0].get('description', ''),
                                    'max_temp': round(item.get('main', {}).get('temp_max', 0)),
                                    'min_temp': round(item.get('main', {}).get('temp_min', 0))
                                })
                    else:
                        error = "Վայրը չգտնվեց։"
                except Exception:
                    error = "Միացման սխալ։"

    return render_template(
        'weather.html',
        city_name=city_name,
        country_name=country_name,
        temp=temp,
        wind_speed=wind_speed,
        weather_text=weather_text,
        forecast=forecast,
        error=error
    )

if __name__ == '__main__':
    app.run(debug=True)
