from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import requests
import os

load_dotenv()

app = Flask(__name__)

HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL_NAME = "openai/gpt-oss-120b"

SYSTEM_PROMPT = "اسمك الطيبات. انت مساعد ذكاء اصطناعي ودود ومرن جدا في اسلوبك. ممكن تكون رسمي لما الموضوع جاد، وممكن تكون عامي ومرح لما الجو خفيف. لو حد سألك بالعربي رد بالعربي وافضل تستخدم اللهجة المصرية بطلاقة لو المستخدم بيكلمك بالمصري. لو حد سألك بالانجليزي رد بالانجليزي. كن مفيد وصادق ومباشر دايما."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    history = data.get("history", [])

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += history
    messages.append({"role": "user", "content": user_message})

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
            reply = "Error from API: " + str(res_data["error"])
        else:
            reply = "Unexpected response: " + str(res_data)

        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"response": "Error: " + str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
