from flask import Flask, render_template, request
from googlesearch import search

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    reply = ""
    if request.method == 'POST':
        user_msg = request.form['message']
        try:
            results = list(search(user_msg, num_results=3))
            reply = "Search results:\n" + "\n".join([f"{i+1}. {url}" for i, url in enumerate(results)])
        except Exception as e:
            reply = f"Error: {e}"
    return render_template('index.html', reply=reply)

if __name__ == '__main__':
    app.run()
