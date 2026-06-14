from flask import Flask, render_template, request, redirect, url_for
import requests
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'weather_secret_key_2026')

# OpenWeather API-ի բանալին
API_KEY = 'b7376e7399b3986a7ffc33eb6c34a6ef'

# 1. Գլխավոր էջ մտնելիս միանգամից բացվում է լոգինի էջը
@app.route('/')
def index():
    return render_template('login.html')

# 2. Լոգինի մշակումը. սեղմելիս տանում է եղանակի էջ
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Այստեղ ստացվում է հարցումը, և «Մուտքի հարցումը ստացվել է» տեքստի փոխարեն
        # օգտատիրոջը միանգամից ուղարկում ենք եղանակի էջ
        return redirect(url_for('weather_page'))
    return render_template('login.html')

# 3. Եղանակի էջի հիմնական տրամաբանությունը (Քարտեզ + Որոնում)
@app.route('/weather', methods=['GET', 'POST'])
def weather_page():
    city_name = ""
    country_name = ""
    temp = ""
    wind_speed = ""
    weather_text = ""
    forecast = []
    error = None

    if request.method == 'POST':
        search_query = request.form.get('city', '').strip()
        
        if search_query:
            # Ստուգում ենք՝ արդյո՞ք քարտեզից կոորդինատներ են եկել (լայնություն, երկարություն)
            if ',' in search_query:
                try:
                    lat, lon = search_query.split(',')
                    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=am"
                    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=am"
                except ValueError:
                    error = "Կոորդինատների սխալ ձևաչափ։"
            else:
                # Եթե ուղղակի քաղաքի անուն է գրվել
                url = f"https://api.openweathermap.org/data/2.5/weather?q={search_query}&appid={API_KEY}&units=metric&lang=am"
                forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={search_query}&appid={API_KEY}&units=metric&lang=am"

            if not error:
                # 1. Ընթացիկ եղանակի հարցում
                res = requests.get(url)
                if res.status_code == 200:
                    data = res.json()
                    city_name = data.get('name')
                    country_name = data.get('sys', {}).get('country', '')
                    temp = round(data.get('main', {}).get('temp', 0))
                    wind_speed = round(data.get('wind', {}).get('speed', 0) * 3.6) # մ/վ-ը դարձնում ենք կմ/ժ
                    weather_text = data.get('weather', [{}])[0].get('description', '').capitalize()
                    
                    # 2. 5 օրվա կանխատեսման հարցում
                    f_res = requests.get(forecast_url)
                    if f_res.status_code == 200:
                        f_data = f_res.json()
                        # Քանի որ API-ն տալիս է տվյալներ 3 ժամը մեկ, վերցնում ենք օրական 1 նմուշ (ամեն 8-րդը)
                        for item in f_data.get('list', [])[::8]:
                            forecast.append({
                                'date': item.get('dt_txt', '').split(' ')[0],
                                'condition': item.get('weather', [{}])[0].get('description', ''),
                                'max_temp': round(item.get('main', {}).get('temp_max', 0)),
                                'min_temp': round(item.get('main', {}).get('temp_min', 0))
                            })
                else:
                    error = "Վայրը չգտնվեց։ Խնդրում ենք ստուգել անվանումը։"

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
