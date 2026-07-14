import os
import requests
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'super_secret_key_123'  # Պարտադիր է session-ի համար

# ... [translate_weather_code և get_coordinates ֆունկցիաները թողնում ես նույնը] ...

# Նոր Login էջը
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Սա քո գաղտնաբառն է, կարող ես փոխել
        if request.form.get('password') == '1234': 
            session['logged_in'] = True
            return redirect(url_for('show_weather'))
    return render_template('login.html') # Ստեղծիր այս ֆայլը templates թղթապանակում

@app.route('/weather', methods=['GET', 'POST'])
def show_weather():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    city_query = "Yerevan"
    # ... [մնացած կոդը թողնում ես նույնը] ...
    # Քո նախկին տրամաբանությունը...
    return render_template(...) 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
