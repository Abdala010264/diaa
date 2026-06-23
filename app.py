from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import os

load_dotenv()

app = Flask(__name__)

HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL_NAME = "openai/gpt-oss-120b"

SYSTEM_PROMPT = "اسمك الطيبات. انت مساعد ذكاء اصطناعي ودود ومرن جدا في اسلوبك. ممكن تكون رسمي لما الموضوع جاد، وممكن تكون عامي ومرح لما الجو خفيف. لو حد سألك بالعربي رد بالعربي وافضل تستخدم اللهجة المصرية بطلاقة لو المستخدم بيكلمك بالمصري. لو حد سألك بالانجليزي رد بالانجليزي. لو عندك معلومات من البحث استخدمها في ردك وقول المصدر."

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
    except Exception as e:
        return ""

def needs_search(message):
    keywords = ["سعر", "كام", "اليوم", "الان", "دلوقتي", "اخبار", "نتيجة", "طقس", "عملة", "دولار", "يورو", "جنيه", "بورصة", "price", "today", "news", "weather", "current", "latest", "now", "2025", "2026"]
    message_lower = message.lower()
    return any(k in message_lower for k in keywords)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    history = data.get("history", [])

    search_context = ""
    if needs_search(user_message):
        search_result = web_search(user_message)
        if search_result:
            search_context = f"\n\n[نتائج البحث على الإنترنت]: {search_result}"

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += history
    messages.append({"role": "user", "content": user_message + search_context})

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
