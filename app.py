from flask import Flask
import threading

from gmail_reader import start_monitoring
from webhook import handle_whatsapp_reply

app = Flask(__name__)


@app.route("/")
def home():
    return "AI Meeting Guardian Running 🚀"


# WHATSAPP WEBHOOK
@app.route("/webhook", methods=["POST"])
def webhook():
    return handle_whatsapp_reply()


# START EMAIL MONITOR
threading.Thread(
    target=start_monitoring,
    daemon=True
).start()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080
    )