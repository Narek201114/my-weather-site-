from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import os

app = Flask(__name__)
# Գաղտնի բանալի՝ session-ների համար (անհրաժեշտ է Render-ում)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_super_secret_key_123')

# MongoDB-ի միացում (Render-ի environment variable-ից)
mongo_uri = os.environ.get('MONGO_URI')
client = MongoClient(mongo_uri)
db = client.weather_db

# Գլխավոր էջ
@app.route('/')
def index():
    return render_template('index.html')

# Մուտքի էջ՝ մուտքի տրամաբանությամբ
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Ստանում ենք մուտքագրված տվյալները
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Այստեղ կարող ես ավելացնել տվյալների բազայից ստուգում
        # Օրինակ՝ if db.users.find_one({"username": username}):
        
        # Եթե մուտքը հաջող է, տեղափոխում ենք եղանակի էջ
        return redirect(url_for('weather'))
    
    return render_template('login.html')

# Եղանակի էջ
@app.route('/weather')
def weather():
    return render_template('weather.html')

if __name__ == '__main__':
    app.run(debug=True)
