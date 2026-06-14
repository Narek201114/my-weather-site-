from flask import Flask, render_template, request
from pymongo import MongoClient
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'mysecretkey')

# MongoDB կապ
client = MongoClient(os.environ.get('MONGO_URI'))
db = client.weather_db

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Այստեղ կավելացնես մուտքի տրամաբանությունը
        return "Մուտքի հարցումը ստացվել է"
    return render_template('login.html')

@app.route('/weather')
def weather():
    return render_template('weather.html')

if __name__ == '__main__':
    app.run(debug=True)
