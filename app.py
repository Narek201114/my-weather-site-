from flask import Flask, render_template, request, redirect, url_for, session
import urllib.request
import urllib.parse
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'weather_secure_session_key_2026')

API_KEY = 'b7376e7399b3986a7ffc33eb6c34a6ef'

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'logged_in' in session:
        return redirect(url_for('weather'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Քո ճիշտ տվյալները՝ հաշվի առնելով Narek2011. գաղտնաբառը
        if username == "Narek" and password == "Narek2011.":
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('weather'))
        else:
            error = "⚠️ Սխալ օգտանուն կամ գաղտնաբառ։"
            
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/weather', methods=['GET', 'POST'])
def weather():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    city_name = "Ընտրեք քաղաք"
    temp = "--"
    wind_speed = "0"
    weather_text = "Սպասում է որոնման"
    forecast = []
    error = None

    if request.method == 'POST':
        search_query = request.form.get('city', '').strip()
        
        if search_query and search_query != "Ընտրեք քաղաք":
            url = None
            forecast_url = None
            
            if ',' in search_query:
                try:
                    parts = search_query.split(',')
                    if len(parts) == 2:
                        lat = parts[0].strip()
                        lon = parts[1].strip()
                        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=am"
                        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=am"
                except Exception:
                    error = "Բնակավայրը չգտնվեց"
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
                            
                            city_name = data.get('name', '').strip()
                            if not city_name:
                                city_name = "Հայտնաբերված վայր"
                                
                            temp = f"{round(data.get('main', {}).get('temp', 0))}"
                            wind_speed = f"{round(data.get('wind', {}).get('speed', 0) * 3.6)}"
                            weather_text = data.get('weather', [{}])[0].get('description', '').capitalize()
                            
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
                            error = "Բնակավայրը չգտնվեց"
                except Exception:
                    error = "Բնակավայրը չգտնվեց"

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
