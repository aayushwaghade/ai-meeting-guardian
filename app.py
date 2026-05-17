from flask import Flask
import threading
from gmail_reader import start_monitoring
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "AI Meeting Guardian Running"

def run_bot():
    start_monitoring()

threading.Thread(target=run_bot).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)