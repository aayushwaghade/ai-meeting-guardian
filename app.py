from flask import Flask
from gmail_reader import start_monitoring
import threading

app = Flask(__name__)

@app.route("/")
def home():
    return "AI Meeting Guardian Running"


@app.route("/webhook")
def webhook():
    return "Webhook Working"


thread = threading.Thread(target=start_monitoring)
thread.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)