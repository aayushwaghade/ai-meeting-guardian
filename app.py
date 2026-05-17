from flask import Flask, request
import threading
import time
import json
from gmail_reader import check_gmail

app = Flask(__name__)

# =========================
# LOAD REMINDERS
# =========================

def load_reminders():
    try:
        with open("reminders.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_reminders(data):
    with open("reminders.json", "w") as f:
        json.dump(data, f, indent=2)

# =========================
# WHATSAPP WEBHOOK
# =========================

@app.route("/webhook", methods=["GET"])
def verify():
    VERIFY_TOKEN = "hello123"

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200

    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    print("\n📩 Incoming WhatsApp Reply")

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]

        if message["type"] == "text":
            user_text = message["text"]["body"].strip().lower()

            print(f"💬 User Reply: {user_text}")

            if user_text == "done":

                reminders = load_reminders()

                found = False

                for key in reminders:
                    if reminders[key]["completed"] == False:
                        reminders[key]["completed"] = True
                        found = True
                        break

                save_reminders(reminders)

                if found:
                    print("✅ Reminder marked completed")
                else:
                    print("❌ No pending reminder found")

    except Exception as e:
        print("Webhook Error:", e)

    return "ok", 200

# =========================
# GMAIL LOOP
# =========================

def gmail_loop():
    while True:
        try:
            print("\n🚀 AI Meeting Guardian Checking Gmail...\n")

            check_gmail()

        except Exception as e:
            print("Gmail Loop Error:", e)

        print("\n⏳ Waiting 5 mins...\n")

        time.sleep(300)

# =========================
# START EVERYTHING
# =========================

if __name__ == "__main__":

    t = threading.Thread(target=gmail_loop)
    t.daemon = True
    t.start()

    print("🚀 Bot Started Successfully")

    app.run(host="0.0.0.0", port=5000)