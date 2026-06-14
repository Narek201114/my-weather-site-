from flask import Flask, render_template, request, redirect, url_for
import urllib.request
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'weather_secure_pure_2026')

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
    city_name = "Ընտրեք քաղաք"
    temp = "--"
    wind_speed = "0"
    weather_text = "Սպասում է ընտրության"
    forecast = []
    error = None

    if request.method == 'POST':
        search_query = request.form.get('city', '').strip()
        
        if search_query:
            url = None
            forecast_url = None
            
            # 1. Ստուգում ենք՝ արդյո՞ք քարտեզից կոորդինատներ են եկել
            if ',' in search_query:
                try:
                    lat, lon = search_query.split(',')
                    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat.strip()}&lon={lon.strip()}&appid={API_KEY}&units=metric&lang=am"
                    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat.strip()}&lon={lon.strip()}&appid={API_KEY}&units=metric&lang=am"
                except Exception:
                    error = "Կոորդինատների սխալ։"
            else:
                # Տեքստային որոնում քաղաքի անունով
                safe_city = urllib.parse.quote(search_query)
                url = f"https://api.openweathermap.org/data/2.5/weather?q={safe_city}&appid={API_KEY}&units=metric&lang=am"
                forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={safe_city}&appid={API_KEY}&units=metric&lang=am"

            if url and not error:
                try:
                    # Ընթացիկ եղանակի ստացում urllib-ով
                    with urllib.request.urlopen(url, timeout=10) as response:
                        if response.status == 200:
                            data = json.loads(response.read().decode())
                            
                            # Ցույց ենք տալիս բնակավայրի իրական անունը
                            city_name = data.get('name', 'Հայտնաբերված վայր')
                            if not city_name:
                                city_name = "Անհայտ բնակավայր"
                                
                            temp = f"{round(data.get('main', {}).get('temp', 0))}"
                            wind_speed = f"{round(data.get('wind', {}).get('speed', 0) * 3.6)}"
                            weather_text = data.get('weather', [{}])[0].get('description', '').capitalize()
                            
                            # 5 օրվա կանխատեսման ստացում
                            with urllib.request.urlopen(forecast_url, timeout=10) as f_response:
                                if f_response.status == 200:
                                    f_data = json.loads(f_response.read().decode())
                                    for item in f_data.get('list', [])[::8]:
                                        forecast.append({
                                            'date': item.get('dt_txt', '').split(' ')[0],
                                            'condition': item.get('weather', [{}])[0].get('description', '').capitalize(),
                                            'max_temp': round(item.get('main', {}).get('temp_max', 0)),
                                            'min_temp': round(item.get('main', {}).get('temp_min', 0))
                                        })
                        else:
                            error = "Չգտնվեց։"
                except Exception:
                    error = "Վայրը չգտնվեց կամ API-ի սխալ է։"

    return render_template(
        'weather.html',
        city_name=city_name,
        temp=temp,
        wind_speed=wind_speed,
        weather_text=weather_text,
        forecast=forecast,
        error=error
    )

if __name__ == '__main__':
    app.run(debug=True)
