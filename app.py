from flask import Flask, render_template, request, redirect, url_for, session
import urllib.request
import urllib.parse
import json
import os

app = Flask(__name__)
# Ապահով սեսիաների գաղտնի բանալի
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
        
        # Մուտքի ճիշտ տվյալները
        if username == "admin" and password == "12345":
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
    # Սեսիայի պաշտպանություն. եթե լոգին չի եղել, հետ է ուղարկում
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
            
            # Եթե հարցումը քարտեզի կոորդինատներ են
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
                # Տեքստային որոնում քաղաքի անունով
                safe_city = urllib.parse.quote(search_query)
                url = f"https://api.openweathermap.org/data/2.5/weather?q={safe_city}&appid={API_KEY}&units=metric&lang=am"
