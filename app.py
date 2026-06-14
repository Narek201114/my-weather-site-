from flask import Flask, render_template, request, redirect, url_for
import requests
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'weather_rev_geocoding_2026')

# OpenWeather API-ի հուսալի բանալին
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
    # Սկզբնական լռելյայն արժեքներ էջի առաջին մուտքի համար
    city_name = "Ընտրեք քաղաք"
    temp = "--"
    wind_speed = "0"
    weather_text = "Սպասում է ընտրության"
    forecast = []
    error = None

    if request.method == 'POST':
        search_query = request.form.get('city', '').strip()
        
        if search_query:
            lat, lon = None, None
            
            # 1. Ստուգում ենք՝ արդյո՞ք հարցումը քարտեզի կոորդինատ է (պարունակում է ստորակետ)
            if ',' in search_query:
                try:
                    lat_parts = search_query.split(',')
                    if len(lat_parts) == 2:
                        lat = lat_parts[0].strip()
                        lon = lat_parts[1].strip()
                except Exception:
                    error = "Կոորդինատների ձևաչափի սխալ։"
            
            # 2. Կախված հարցման տեսակից՝ ձևավորում ենք OpenWeather API-ի հասցեները
            if lat and lon:
                # Քարտեզից եկած կոորդինատներով հարցում
                url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=am"
                forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=am"
            else:
                # Տեքստային որոնում քաղաքի անունով
                url = f"https://api.openweathermap.org/data/2.5/weather?q={search_query}&appid={API_KEY}&units=metric&lang=am"
                forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={search_query}&appid={API_KEY}&units=metric&lang=am"

            if not error:
                try:
                    # Ընթացիկ եղանակի ստացում
                    res = requests.get(url, timeout=10)
                    if res.status_code == 200:
                        data = res.json()
                        
                        # Իրական բնակավայրի անվան որոշում (նույնիսկ եթե քարտեզից է հարցումը)
                        fetched_name = data.get('name', '').strip()
                        if fetched_name:
                            city_name = fetched_name
                        else:
                            # Եթե աշխարհագրական կետը բնակավայր չէ (օրինակ՝ դաշտ կամ լիճ), ցույց տալ ավտոմատ անուն
                            city_name = "Հայտնաբերված վայր"

                        temp = f"{round(data.get('main', {}).get('temp', 0))}"
                        wind_speed = f"{round(data.get('wind', {}).get('speed', 0) * 3.6)}" # մ/վ -> կմ/ժ
                        weather_text = data.get('weather', [{}])[0].get('description', '').capitalize()
                        
                        # 5 օրվա կանխատեսումների ստացում աղյուսակի համար
                        f_res = requests.get(forecast_url, timeout=10)
                        if f_res.status_code == 200:
                            f_data = f_res.json()
                            # Վերցնում ենք յուրաքանչյուր օրվա համար 1 նմուշ (ցուցակի ամեն 8-րդ էլեմենտը)
                            for item in f_data.get('list', [])[::8]:
                                forecast.append({
                                    'date': item.get('dt_txt', '').split(' ')[0],
                                    'condition': item.get('weather', [{}])[0].get('description', '').capitalize(),
                                    'max_temp': round(item.get('main', {}).get('temp_max', 0)),
                                    'min_temp': round(item.get('main', {}).get('temp_min', 0))
                                })
                    else:
                        error = "Բնակավայրը չգտնվեց։"
                except Exception:
                    error = "API-ի հետ կապի սխալ։"

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
