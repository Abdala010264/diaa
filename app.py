from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from googlesearch import search

# تحميل متغيرات البيئة من .env
load_dotenv()

app = Flask(__name__)

HF_TOKEN = os.getenv("HF_TOKEN")

# دالة البحث اللي كانت ناقصة
def search_web(query):
    try:
        results = []
        # بنجيب اول 3 نتائج بحث بالعربي
        for url in search(query, num_results=3, lang="ar"):
            results.append(url)
        
        if results:
            return "نتائج البحث:\n" + "\n".join(results)
        else:
            return "مفيش نتائج للبحث ده"
    except Exception as e:
        return f"حصل خطأ في البحث: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    user_message = data.get('message', '')
    
    # لو المستخدم بيسأل عن سعر الدولار او اي حاجة محتاجة بحث
    if 'سعر' in user_message or 'بحث' in user_message or 'الدولار' in user_message:
        result = search_web(user_message)
        return jsonify({"reply": result})
    
    # رد افتراضي
    return jsonify({"reply": f"انت قولت: {user_message}"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
