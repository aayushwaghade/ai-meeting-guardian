from flask import Flask, request
import threading
from gmail_reader import start_monitoring

app = Flask(__name__)

VERIFY_TOKEN = "aayush123"

# WEBHOOK VERIFICATION
@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ WEBHOOK VERIFIED")
        return challenge, 200

    return "Verification failed", 403


# RECEIVE WHATSAPP MESSAGES
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    print("📩 Incoming WhatsApp Message:")
    print(data)

    return "ok", 200


# START GMAIL MONITORING
def run_bot():
    print("🚀 Google AI Guardian Running...")
    print("📩 Monitoring Google Ambassador Updates...")
    start_monitoring()


thread = threading.Thread(target=run_bot)
thread.start()


@app.route('/')
def home():
    return "AI Meeting Guardian Running"


if __name__ == "__main__":
    print("🚀 Bot Started Successfully")
    app.run(host="0.0.0.0", port=8080)