from flask import Flask, request
import threading
import time
import traceback
import os

from gmail_reader import check_gmail

app = Flask(__name__)

# ==========================================
# HOME ROUTE
# ==========================================

@app.route("/")
def home():
    return "AI Meeting Guardian Running 24/7"

# ==========================================
# WHATSAPP WEBHOOK
# ==========================================

@app.route("/webhook", methods=["POST"])
def webhook():

    try:

        data = request.json

        print("\n📩 Incoming WhatsApp Reply")
        print(data)

        if data:

            entry = data.get("entry", [])

            if entry:

                changes = entry[0].get("changes", [])

                if changes:

                    value = changes[0].get("value", {})

                    messages = value.get("messages", [])

                    if messages:

                        message_text = (
                            messages[0]
                            .get("text", {})
                            .get("body", "")
                            .strip()
                            .lower()
                        )

                        print(f"💬 User Reply: {message_text}")

                        if message_text == "done":
                            print("✅ Task Completed!")

    except Exception as e:

        print("❌ WEBHOOK ERROR")
        traceback.print_exc()

    return "ok", 200

# ==========================================
# MAIN BOT LOOP
# ==========================================

def bot_loop():

    print("🚀 Bot Started Successfully")

    while True:

        try:

            print("\n🚀 AI Meeting Guardian Checking Gmail...\n")

            check_gmail()

            print("\n⏳ Waiting 5 mins...\n")

            time.sleep(300)

        except Exception as e:

            print("\n❌ BOT LOOP ERROR\n")

            traceback.print_exc()

            time.sleep(30)

# ==========================================
# START BACKGROUND THREAD
# ==========================================

thread = threading.Thread(target=bot_loop)

thread.daemon = True

thread.start()

# ==========================================
# START FLASK SERVER
# ==========================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )