from flask import Flask, render_template, request, redirect, url_for, session
import urllib.request
import urllib.parse
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'weather_secure_session_key_2026')
API_KEY = 'b7376e7399b3986a7ffc33eb6c34a6ef'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == "Narek" and request.form.get('password') == "Narek2011.":
            session['logged_in'] = True
            return redirect(url_for('weather'))
    return render_template('login.html')

@app.route('/weather', methods=['GET', 'POST'])
def weather():
    if 'logged_in' not in session: return redirect(url_for('login'))
    
    context = {'city_name': 'Ընտրեք քաղաք', 'temp': '--', 'wind_speed': '0', 'weather_text': 'Սպասում է որոնման', 'forecast': []}
    
    if request.method == 'POST':
        query = request.form.get('city', '').strip()
        # Օգտագործում ենք քաղաքի անվան համար հատուկ ֆորմատ
        url = f"https://api.openweathermap.org/data/2.5/weather?q={urllib.parse.quote(query)}&appid={API_KEY}&units=metric&lang=am"
        
        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                context['city_name'] = data['name']
                context['temp'] = round(data['main']['temp'])
                context['wind_speed'] = round(data['wind']['speed'] * 3.6)
                context['weather_text'] = data['weather'][0]['description']
        except:
            context['error'] = "Բնակավայրը չգտնվեց"
            
    return render_template('weather.html', **context)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()
