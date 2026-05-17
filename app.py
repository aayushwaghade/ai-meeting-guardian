from flask import Flask, request
import threading
import time
from gmail_reader import check_gmail

app = Flask(__name__)

# =========================
# HOME ROUTE
# =========================

@app.route("/")
def home():
    return "AI Meeting Guardian Running"

# =========================
# WHATSAPP WEBHOOK
# =========================

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    print("\n📩 Incoming WhatsApp Reply")
    print(data)

    try:
        message = (
            data["entry"][0]["changes"][0]["value"]
            ["messages"][0]["text"]["body"]
            .strip()
            .lower()
        )

        print(f"💬 User Reply: {message}")

        if message == "done":
            print("✅ Task marked completed!")

    except Exception as e:
        print("⚠️ Error:", e)

    return "ok", 200

# =========================
# MAIN BOT LOOP
# =========================

def bot_loop():

    print("🚀 Bot Started Successfully")

    while True:

        try:

            print("\n🚀 AI Meeting Guardian Checking Gmail...\n")

            check_gmail()

            print("\n⏳ Waiting 5 mins...\n")

        except Exception as e:

            print("❌ BOT ERROR:", e)

        time.sleep(300)

# =========================
# START BACKGROUND THREAD
# =========================

thread = threading.Thread(target=bot_loop)

thread.daemon = True

thread.start()

# =========================
# START FLASK SERVER
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )