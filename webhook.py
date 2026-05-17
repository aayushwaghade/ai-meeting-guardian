from flask import request, jsonify
import json
import os

REMINDER_FILE = "reminders.json"


def load_reminders():
    if not os.path.exists(REMINDER_FILE):
        return []

    with open(REMINDER_FILE, "r") as f:
        return json.load(f)


def save_reminders(reminders):
    with open(REMINDER_FILE, "w") as f:
        json.dump(reminders, f, indent=4)


def handle_whatsapp_reply():
    data = request.get_json()

    print("📩 Incoming WhatsApp Reply:")
    print(data)

    try:
        message = (
            data["entry"][0]
            ["changes"][0]
            ["value"]["messages"][0]
            ["text"]["body"]
            .strip()
            .upper()
        )

        sender = (
            data["entry"][0]
            ["changes"][0]
            ["value"]["messages"][0]
            ["from"]
        )

        print(f"📨 Message from {sender}: {message}")

        if message == "DONE":

            reminders = load_reminders()

            updated = False

            for reminder in reminders:
                if (
                    reminder.get("completed") == False
                ):
                    reminder["completed"] = True
                    updated = True

            save_reminders(reminders)

            if updated:
                print("✅ Task marked completed")
            else:
                print("⚠️ No active task found")

    except Exception as e:
        print("❌ Webhook Error:", e)

    return jsonify({"status": "success"})