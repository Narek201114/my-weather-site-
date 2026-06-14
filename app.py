from flask import Flask, render_template, request
from pymongo import MongoClient
import os

app = Flask(__name__)
# Օգտագործում ենք Render-ի Environment-ում սահմանված գաղտնի բանալին
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

# Միացում MongoDB-ին՝ օգտագործելով MONGO_URI-ն
client = MongoClient(os.environ.get('MONGO_URI'))
db = client.weather_db

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/weather')
def weather():
    return render_template('weather.html')

if __name__ == '__main__':
    app.run(debug=True)
