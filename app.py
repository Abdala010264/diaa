from flask import Flask, request, jsonify
from dotenv import load_dotenv
from duckduckgo_search import DDGS
import requests
import os

load_dotenv()

app = Flask(__name__)

HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL_NAME = "openai/gpt-oss-120b"

SYSTEM_PROMPT = "اسمك الطيبات. انت مساعد ذكاء اصطناعي ودود ومرن جدا في اسلوبك. ممكن تكون رسمي لما الموضوع جاد، وممكن تكون عامي ومرح لما الجو خفيف. لو حد سألك بالعربي رد بالعربي وافضل تستخدم اللهجة المصرية بطلاقة لو المستخدم بيكلمك بالمصري. لو حد سألك بالانجليزي رد بالانجليزي. كن مفيد وصادق ومباشر دايما. لو في نتايج بحث هتتبعتلك استخدمها في ردك وكن محدد."

def search_web(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if results:
                search_text = ""
                for r in results:
                    search_text += f"- {r['title']}: {r['body']}\n"
                return search_text
    except Exception as e:
        print(f"Search error: {str(e)}")
    return None

def needs_search(message):
    keywords = ["ابحث", "بحث", "اخبار", "أخبار", "دلوقتي", "الآن", "اليوم", "سعر", "نتيجة", "search", "news", "today", "price", "latest", "2024", "2025", "2026"]
    for kw in keywords:
        if kw in message.lower():
            return True
    return False

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    messages = data.get("history", [])

    system_content = SYSTEM_PROMPT

    if needs_search(user_message):
        search_results = search_web(user_message)
        if search_results:
            system_content += f"\n\nنتايج البحث على الإنترنت:\n{search_results}"

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    all_messages = [{"role": "system", "content": system_content}]
    all_messages += messages
    all_messages.append({"role": "user", "content": user_message})

    payload = {
        "model": MODEL_NAME,
        "messages": all_messages,
        "max_tokens": 500
    }

    try:
        res = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        res_data = res.json()

        if "choices" in res_data and len(res_data["choices"]) > 0:
            reply = res_data["choices"][0]["message"]["content"]
        elif "error" in res_data:
            reply = "Error from API: " + str(res_data["error"])
        else:
            reply = "Unexpected response: " + str(res_data)

        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"response": "Error: " + str(e)})

@app.route("/")
def home():
    return open("index.html").read()

@app.route("/style.css")
def css():
    return open("style.css").read(), 200, {"Content-Type": "text/css"}

@app.route("/script.js")
def js():
    return open("script.js").read(), 200, {"Content-Type": "application/javascript"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
