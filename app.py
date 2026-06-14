from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'my_secret_key_123')

# MongoDB միացում
mongo_uri = os.environ.get('MONGO_URI')
client = MongoClient(mongo_uri)
db = client.weather_db

# 1. Կայք մտնելիս միանգամից բացվում է լոգինի էջը
@app.route('/')
def index():
    return render_template('login.html')

# 2. Երբ սեղմում են «Մուտք», այս ֆունկցիան ավտոմատ տեղափոխում է եղանակի էջ
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Օգտատերը սեղմեց մուտքի կոճակը -> տանում ենք իրական էջ
        return redirect(url_for('weather'))
    return render_template('login.html')

# 3. Սա քո սարքած էջն է՝ քարտեզով ու բոլոր ֆունկցիաներով
@app.route('/weather')
def weather():
    return render_template('weather.html')

if __name__ == '__main__':
    app.run(debug=True)
