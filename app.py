from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'super_secret_key_weather_site')

# MongoDB Միացում
mongo_uri = os.environ.get('MONGO_URI')
client = MongoClient(mongo_uri)
db = client.weather_db

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Երբ սեղմում են մուտք, այն տանում է դեպի /weather
        return redirect(url_for('weather'))
    return render_template('login.html')

@app.route('/weather')
def weather():
    return render_template('weather.html')

if __name__ == '__main__':
    app.run(debug=True)
