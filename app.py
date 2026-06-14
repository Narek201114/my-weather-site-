from flask import Flask, render_template, request
from pymongo import MongoClient
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

# Միացում MongoDB-ին՝ օգտագործելով Render-ի Environment փոփոխականը
client = MongoClient(os.environ.get('MONGO_URI'))
db = client.weather_db

@app.route('/login')
def login():
    # Սա կբացի templates/login.html ֆայլը
    return render_template('login.html')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
