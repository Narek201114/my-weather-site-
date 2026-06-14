from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'weather_secret_key_2026')

# 1. Գլխավոր էջ մտնելիս բացվում է լոգինի էջը
@app.route('/')
def index():
    return render_template('login.html')

# 2. Մուտք գործելուց հետո օգտատիրոջը տանում ենք եղանակի էջ
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('weather'))
    return render_template('login.html')

# 3. Քո եղանակի էջը
@app.route('/weather')
def weather():
    return render_template('weather.html')

if __name__ == '__main__':
    app.run(debug=True)
