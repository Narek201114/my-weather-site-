from flask import Flask, render_template, request, redirect, url_for
import urllib.request
import urllib.parse
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
        
        # ՖԻՔՍ: Եթե հարցումը դատարկ է, կամ պատահական եկել է հենց "Ընտրեք քաղաք" տեքստը, API-ին հարցում չենք անում
        if search_query and search_query != "" and search_query != "Ընտրեք քաղաք":
            url = None
            forecast_url = None
            
            if ',' in search_query:
                try:
                    lat, lon = search_query.split(',')
                    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat.strip()}&lon={lon.strip()}&appid={API_KEY}&units=metric&lang=am"
                    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat.strip()}&lon={lon.strip()}&appid={API_KEY}&units=metric&lang=am"
                except Exception:
                    error = "Կոորդինատների սխալ։"
            else:
                safe_city = urllib.parse.quote(search_query)
                url = f"https://api.openweathermap.org/data/2.5/weather?q={safe_city}&appid={API_KEY}&units=metric&lang=am"
                forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={safe_city}&appid={API_KEY}&units=metric&lang=am"

            if url and not error:
                try:
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=10) as response:
                        if response.status == 200:
                            data = json.loads(response.read().decode())
                            
                            city_name = data.get('name', 'Հայտնաբերված վայր')
                            if not city_name:
                                city_name = "Անհայտ բնակավայր"
                                
                            temp = f"{round(data.get('main', {}).get('temp', 0))}"
                            wind_speed = f"{round(data.get('wind', {}).get('speed', 0) * 3.6)}"
                            weather_text = data.get('weather', [{}])[0].get('description', '').capitalize()
                            
                            # 5 օրվա կանխատեսում
                            f_req = urllib.request.Request(forecast_url, headers={'User-Agent': 'Mozilla/5.0'})
                            with urllib.request.urlopen(f_req, timeout=10) as f_response:
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
                            error = "Բնակավայրը չգտնվեց:"
                except Exception:
                    error = "Վայրը չգտնվեց կամ API-ի սխալ է:"

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
