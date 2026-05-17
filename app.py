from flask import Flask, request
import json
import os

app = Flask(__name__)

REMINDER_FILE = "reminders.json"

VERIFY_TOKEN = "myverifytoken"

# =====================================
# LOAD REMINDERS
# =====================================

def load_reminders():

    if not os.path.exists(REMINDER_FILE):

        with open(REMINDER_FILE, "w") as f:
            json.dump({}, f)

    with open(REMINDER_FILE, "r") as f:
        return json.load(f)

# =====================================
# SAVE REMINDERS
# =====================================

def save_reminders(data):

    with open(REMINDER_FILE, "w") as f:
        json.dump(data, f, indent=4)

# =====================================
# VERIFY WEBHOOK
# =====================================

@app.route("/webhook", methods=["GET"])

def verify():

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:

        if token == VERIFY_TOKEN:
            return challenge, 200

    return "Verification failed", 403

# =====================================
# RECEIVE WHATSAPP REPLIES
# =====================================

@app.route("/webhook", methods=["POST"])

def webhook():

    data = request.get_json()

    print("\n📩 Incoming WhatsApp Reply")
    print(json.dumps(data, indent=2))

    try:

        message = data["entry"][0]["changes"][0]["value"]["messages"][0]

        user_text = message["text"]["body"].strip().lower()

        print(f"\n💬 User Reply: {user_text}")

        # =====================================
        # DONE DETECTION
        # =====================================

        if user_text == "done":

            reminders = load_reminders()

            updated = False

            for reminder_id in reminders:

                if reminders[reminder_id]["completed"] == False:

                    reminders[reminder_id]["completed"] = True

                    updated = True

                    break

            save_reminders(reminders)

            if updated:

                print("\n✅ Reminder marked completed")

            else:

                print("\n❌ No pending reminder found")

    except Exception as e:

        print("\n❌ Error")
        print(str(e))

    return "OK", 200

# =====================================
# START SERVER
# =====================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )