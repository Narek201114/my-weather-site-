import os
from flask import Flask, render_template, request, redirect, url_for, session
import requests
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

# 🔑 Flask Session-ի գաղտնի բանալին և MongoDB-ի միացման տողը
# Render-ի Environment Variables-ում կավելացնենք MONGO_URI-ն
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super-secret-key-123")
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/weather_db")

# 🔌 Միացում MongoDB-ին
client = MongoClient(MONGO_URI)
db = client.get_default_database() # Ավտոմատ վերցնում է բազայի անունը URI-ից
users_col = db["users"]
history_col = db["search_history"]

# 🌦️ WMO Կոդերի թարգմանությունը (Մնացել է նույնը)
WMO_CODES = {
    0: "Պարզ երկինք", 1: "Մեծ մասամբ պարզ", 2: "Փոփոխական ամպամածություն", 3: "Ամբողջովին ամպամած",
    45: "Մառախուղ", 48: "Մառախուղ և եղյամ", 51: "Թույլ մաղող անձրև", 53: "Չափավոր մաղող անձրև",
    55: "Ինտենսիվ մաղող անձրև", 61: "Թույլ անձրև", 63: "Չափավոր անձրև", 65: "Ուժեղ անձրև",
    71: "Թույլ ձյուն", 73: "Չափավոր ձյուն", 75: "Ուժեղ ձյուն", 77: "Կարկուտ",
    80: "Թույլ անձրևային տեղումներ", 81: "Չափավոր անձրևային տեղումներ", 82: "Ուժեղ անձրևային տեղումներ",
    85: "Թույլ ձնախառն տեղումներ", 86: "Ուժեղ ձնախառն տեղումներ", 95: "Ամպրոպ",
    96: "Ամպրոպ թույլ կարկուտով", 97: "Ամպրոպ ուժեղ կարկուտով"
}

def get_weather_data(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=auto"
    res = requests.get(url).json()
    
    current = res.get("current_weather", {})
    daily = res.get("daily", {})
    
    forecast_list = []
    if daily:
        for i in range(min(5, len(daily.get("time", [])))):
            code = daily.get("weathercode")[i]
            forecast_list.append({
                "date": daily.get("time")[i],
                "max_temp": daily.get("temperature_2m_max")[i],
                "min_temp": daily.get("temperature_2m_min")[i],
                "condition": WMO_CODES.get(code, "Անհայտ")
            })
            
    return {
        "temp": current.get("temperature"),
        "wind_speed": current.get("windspeed"),
        "code": current.get("weathercode"),
        "forecast": forecast_list
    }

# 🏠 Գլխավոր էջ (Եթե լոգին եղած չէ, տանում է լոգինի էջ)
@app.route("/", methods=["GET"])
@app.route("/weather", methods=["GET", "POST"])
def weather():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    # Սկզբնական արժեքներ (Երևան)
    lat, lon = 40.1792, 44.5152
    city_name, country_name = "Yerevan", "Armenia"
    error = None

    if request.method == "POST":
        search_input = request.form.get("city", "").strip()
        if search_input:
            if "," in search_input: # Քարտեզի սեղմում (Lat,Lng)
                try:
                    lat, lon = search_input.split(",")
                    geo_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=en"
                    geo_res = requests.get(geo_url, headers={'User-Agent': 'MyWeatherApp/1.0'}).json()
                    address = geo_res.get("address", {})
                    city_name = address.get("city") or address.get("town") or address.get("village") or address.get("state") or "Անհայտ վայր"
                    country_name = address.get("country", "")
                except Exception:
                    error = "Քարտեզի տվյալների սխալ:"
            else: # Քաղաքի անունով որոնում
                geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={search_input}&count=1&language=en&format=json"
                geo_res = requests.get(geo_url).json()
                results = geo_res.get("results")
                if results:
                    lat = results[0]["latitude"]
                    lon = results[0]["longitude"]
                    city_name = results[0]["name"]
                    country_name = results[0].get("country", "")
                else:
                    error = f"'{search_input}' վայրը չի գտնվել։ Ցուցադրվում է Երևանը։"
                    city_name, country_name = "Yerevan", "Armenia"

            # 💾 ՊԱՀՊԱՆՈՒՄ ԵՆՔ ՈՐՈՆՄԱՆ ՊԱՏՄՈՒԹՅՈՒՆԸ ՄՈՆԳՈՅՈՒՄ (եթե սխալ չկա)
            if not error:
                history_col.insert_one({
                    "user_id": session["user_id"],
                    "city": city_name,
                    "country": country_name,
                    "lat": lat,
                    "lon": lon,
                    "timestamp": datetime.utcnow()
                })

    # Ստանում ենք եղանակը
    w_data = get_weather_data(lat, lon)
    weather_text = WMO_CODES.get(w_data["code"], "Անհայտ")

    # 📜 Բերում ենք տվյալ օգտատիրոջ վերջին 5 որոնումները բազայից
    user_history = list(history_col.find({"user_id": session["user_id"]}).sort("timestamp", -1).limit(5))

    return render_template(
        "weather.html",
        city_name=city_name,
        country_name=country_name,
        temp=w_data["temp"],
        wind_speed=w_data["wind_speed"],
        weather_text=weather_text,
        forecast=w_data["forecast"],
        error=error,
        username=session["username"],
        history=user_history
    )

# 📝 ԳՐԱՆՑՄԱՆ ԷՋ (/register)
@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("weather"))
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if username and password:
            # Ստուգում ենք՝ արդյոք անունը զբաղված չէ
            if users_col.find_one({"username": username}):
                error = "Այս օգտանունը արդեն զբաղված է:"
            else:
                hashed_pw = generate_password_hash(password)
                user_id = users_col.insert_one({"username": username, "password": hashed_pw}).inserted_id
                session["user_id"] = str(user_id)
                session["username"] = username
                return redirect(url_for("weather"))
        else:
            error = "Լրացրեք բոլոր դաշտերը:"
    return render_template("register.html", error=error)

# 🔑 ԼՈԳԻՆԻ ԷՋ (/login)
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("weather"))
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        user = users_col.find_one({"username": username})
        if user and check_password_hash(user["password"], password):
            session["user_id"] = str(user["_id"])
            session["username"] = user["username"]
            return redirect(url_for("weather"))
        else:
            error = "Սխալ օգտանուն կամ գաղտնաբառ:"
    return render_template("login.html", error=error)

# 🚪 ԴՈՒՐՍ ԳԱԼ (/logout)
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
