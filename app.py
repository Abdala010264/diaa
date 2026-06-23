from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import os

load_dotenv()

app = Flask(__name__)

HF_TOKEN = os.getenv("HF_TOKEN")
WEATHER_KEY = os.getenv("WEATHER_KEY")
API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL_NAME = "openai/gpt-oss-120b"

SYSTEM_PROMPT = "اسمك الطيبات. انت مساعد ذكاء اصطناعي ودود ومرن جدا في اسلوبك. بتتكلم بالمصري بطلاقة لو المستخدم بيكلمك بالمصري. لو عندك معلومات من البحث او الاسعار او الطقس استخدمها في ردك مباشرة وبثقة من غير ما تقول مش عارف."

def get_weather(city="Cairo"):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_KEY}&units=metric&lang=ar"
        res = requests.get(url, timeout=10)
        data = res.json()
        if data.get("cod") == 200:
            temp = data["main"]["temp"]
            feels = data["main"]["feels_like"]
            desc = data["weather"][0]["description"]
            humidity = data["main"]["humidity"]
            city_name = data["name"]
            return f"الطقس في {city_name}: {desc}، درجة الحرارة {temp}°C (تبدو كأنها {feels}°C)، الرطوبة {humidity}%"
        return ""
    except:
        return ""

def get_exchange_rates():
    try:
        res = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=10)
        data = res.json()
        rates = data.get("rates", {})
        egp = rates.get("EGP", "")
        eur = rates.get("EUR", "")
        gbp = rates.get("GBP", "")
        sar = rates.get("SAR", "")
        aed = rates.get("AED", "")
        return f"أسعار الصرف الآن: 1 دولار = {egp} جنيه مصري، {eur} يورو، {gbp} جنيه إسترليني، {sar} ريال سعودي، {aed} درهم إماراتي"
    except:
        return ""

def web_search(query):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        results = []
        for r in soup.find_all("a", class_="result__snippet")[:3]:
            text = r.get_text(strip=True)
            if text:
                results.append(text)
        return " | ".join(results) if results else ""
    except:
        return ""

def needs_weather(message):
    keywords = ["طقس", "حرارة", "درجة", "مطر", "شمس", "رياح", "جو", "weather", "temperature", "rain"]
    return any(k in message.lower() for k in keywords)

def needs_currency(message):
    keywords = ["سعر", "دولار", "يورو", "جنيه", "عملة", "صرف", "ريال", "درهم", "dollar", "euro", "currency", "exchange"]
    return any(k in message.lower() for k in keywords)

def needs_search(message):
    keywords = ["اليوم", "الان", "دلوقتي", "اخبار", "نتيجة", "بورصة", "today", "news", "current", "latest", "now", "2025", "2026"]
    return any(k in message.lower() for k in keywords)

def extract_city(message):
    cities = {"القاهرة": "Cairo", "الاسكندرية": "Alexandria", "الجيزة": "Giza", "اسوان": "Aswan", "الاقصر": "Luxor", "مكة": "Mecca", "الرياض": "Riyadh", "دبي": "Dubai", "لندن": "London", "باريس": "Paris", "نيويورك": "New York"}
    for arabic, english in cities.items():
        if arabic in message:
            return english
    return "Cairo"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    history = data.get("history", [])

    extra_context = ""

    if needs_weather(user_message):
        city = extract_city(user_message)
        weather = get_weather(city)
        if weather:
            extra_context += f"\n\n[معلومات الطقس]: {weather}"

    if needs_currency(user_message):
        rates = get_exchange_rates()
        if rates:
            extra_context += f"\n\n[أسعار العملات]: {rates}"

    if needs_search(user_message):
        search_result = web_search(user_message)
        if search_result:
            extra_context += f"\n\n[نتائج البحث]: {search_result}"

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += history
    messages.append({"role": "user", "content": user_message + extra_context})

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": 1000
    }

    try:
        res = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        res_data = res.json()
        if "choices" in res_data and len(res_data["choices"]) > 0:
            reply = res_data["choices"][0]["message"]["content"]
        elif "error" in res_data:
            reply = "Error: " + str(res_data["error"])
        else:
            reply = "Unexpected: " + str(res_data)
        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"response": "Error: " + str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
