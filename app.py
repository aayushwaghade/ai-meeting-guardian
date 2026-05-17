from flask import Flask, request
from gmail_reader import start_monitoring
import threading

app = Flask(__name__)

VERIFY_TOKEN = "aayush123"


# ============================================
# HOME ROUTE
# ============================================

@app.route("/")
def home():
    return "AI Meeting Guardian Running"


# ============================================
# META WEBHOOK VERIFICATION
# ============================================

@app.route("/webhook", methods=["GET"])
def verify_webhook():

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:

        print("✅ WEBHOOK VERIFIED")
        return challenge, 200

    return "Verification failed", 403


# ============================================
# RECEIVE WHATSAPP MESSAGES
# ============================================

@app.route("/webhook", methods=["POST"])
def receive_message():

    data = request.get_json()

    print("\n📩 Incoming WhatsApp Message:")
    print(data)

    return "ok", 200


# ============================================
# START BOT THREAD
# ============================================

def run_monitor():

    start_monitoring()


monitor_thread = threading.Thread(
    target=run_monitor
)

monitor_thread.daemon = True
monitor_thread.start()


# ============================================
# RUN FLASK
# ============================================

if __name__ == "__main__":

    print("🚀 Flask Server Started")

    app.run(
        host="0.0.0.0",
        port=8080
    )