from bs4 import BeautifulSoup
import os
import base64
import requests
import json
import time

from datetime import datetime
from email import message_from_bytes

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

print("🚀 Google AI Guardian Running...")
print("📩 Monitoring Ambassador Updates...")

# =========================
# REMINDER FILE
# =========================

REMINDER_FILE = "reminders.json"

# =========================
# LOAD REMINDERS
# =========================

if os.path.exists(REMINDER_FILE):

    with open(REMINDER_FILE, "r") as f:
        reminders = json.load(f)

else:
    reminders = {}

# =========================
# SAVE REMINDERS
# =========================

def save_reminders():

    with open(REMINDER_FILE, "w") as f:
        json.dump(reminders, f)

# =========================
# GOOGLE CREDENTIALS
# =========================

google_credentials = json.loads(
    os.environ["GOOGLE_CREDENTIALS"]
)

# =========================
# GOOGLE AUTH
# =========================

creds = Credentials(
    None,
    refresh_token=google_credentials["refresh_token"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=google_credentials["client_id"],
    client_secret=google_credentials["client_secret"],
    scopes=[
        "https://www.googleapis.com/auth/gmail.readonly"
    ]
)

creds.refresh(Request())

# =========================
# GMAIL SERVICE
# =========================

service = build(
    "gmail",
    "v1",
    credentials=creds
)

# =========================
# WHATSAPP FUNCTION
# =========================

def send_whatsapp_alert(message):

    token = os.environ["WHATSAPP_TOKEN"]
    phone_number_id = os.environ["PHONE_NUMBER_ID"]
    recipient = os.environ["WHATSAPP_TO"]

    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=data
    )

    print("\n📲 WhatsApp Sent")
    print("Status:", response.status_code)
    print("Response:", response.text)

# =========================
# TRUSTED SENDERS
# =========================

TRUSTED_SENDERS = [

    "pingnetwork.in",
    "google.com",
    "google.dev",
    "developers.google.com"

]

# =========================
# IMPORTANT KEYWORDS
# =========================

IMPORTANT_SUBJECTS = [

    "mandatory demo session",
    "task 1",
    "google student ambassador",
    "career glow-up",
    "nano banana",
    "ambassador",
    "demo session"

]

# =========================
# MAIN LOOP
# =========================

while True:

    print("\n🔎 Checking Inbox...")

    try:

        # =========================
        # FETCH EMAILS
        # =========================

        results = service.users().messages().list(
            userId="me",
            maxResults=10,
            labelIds=["INBOX"]
        ).execute()

        messages = results.get("messages", [])

        # =========================
        # PROCESS EMAILS
        # =========================

        for msg in messages:

            message_id = msg["id"]

            txt = service.users().messages().get(
                userId="me",
                id=message_id,
                format="raw"
            ).execute()

            raw_data = base64.urlsafe_b64decode(
                txt["raw"]
            )

            email_message = message_from_bytes(
                raw_data
            )

            subject = email_message["subject"] or ""
            sender = email_message["from"] or ""

            body = ""

            # =========================
            # EXTRACT BODY
            # =========================

            if email_message.is_multipart():

                for part in email_message.walk():

                    content_type = part.get_content_type()

                    try:

                        payload = part.get_payload(
                            decode=True
                        )

                        if payload:

                            decoded_payload = payload.decode(
                                errors="ignore"
                            )

                            # TEXT
                            if content_type == "text/plain":

                                body += decoded_payload

                            # HTML
                            elif content_type == "text/html":

                                soup = BeautifulSoup(
                                    decoded_payload,
                                    "html.parser"
                                )

                                body += soup.get_text(
                                    separator=" "
                                )

                    except:
                        pass

            else:

                try:

                    payload = email_message.get_payload(
                        decode=True
                    )

                    if payload:

                        decoded_payload = payload.decode(
                            errors="ignore"
                        )

                        soup = BeautifulSoup(
                            decoded_payload,
                            "html.parser"
                        )

                        body += soup.get_text(
                            separator=" "
                        )

                except:
                    pass

            # =========================
            # CLEAN BODY
            # =========================

            body = " ".join(body.split())

            sender_lower = sender.lower()

            full_content = f"""
            {subject}
            {body}
            """.lower()

            # =========================
            # DETECT IMPORTANT EMAILS
            # =========================

            trusted_sender = any(
                domain in sender_lower
                for domain in TRUSTED_SENDERS
            )

            important_subject = any(
                keyword in full_content
                for keyword in IMPORTANT_SUBJECTS
            )

            if trusted_sender and important_subject:

                # =========================
                # SKIP OLD PROCESSED EMAILS
                # =========================

                if message_id in reminders:
                    continue

                print("\n🔥 IMPORTANT AMBASSADOR EMAIL FOUND")

                # =========================
                # WHATSAPP MESSAGE
                # =========================

                whatsapp_message = f"""
🚨 IMPORTANT AMBASSADOR UPDATE

📌 Subject:
{subject}

👤 From:
{sender}

📝 Details:
{body[:500]}

⏰ Reminder every 30 mins
🛑 Stops automatically after few reminders

🤖 Google AI Guardian
"""

                print("=" * 60)
                print(whatsapp_message)
                print("=" * 60)

                # =========================
                # SEND WHATSAPP
                # =========================

                send_whatsapp_alert(
                    whatsapp_message
                )

                # =========================
                # SAVE REMINDER
                # =========================

                reminders[message_id] = {

                    "subject": subject,

                    "sender": sender,

                    "body": body[:500],

                    "created_at":
                    datetime.now().isoformat(),

                    "last_sent":
                    datetime.now().isoformat(),

                    "count": 1
                }

                save_reminders()

        # =========================
        # SEND REMINDERS
        # =========================

        current_time = datetime.now()

        for message_id in list(reminders.keys()):

            reminder = reminders[message_id]

            created_at = datetime.fromisoformat(
                reminder["created_at"]
            )

            last_sent = datetime.fromisoformat(
                reminder["last_sent"]
            )

            reminder_count = reminder["count"]

            # =========================
            # STOP CONDITIONS
            # =========================

            hours_passed = (
                current_time - created_at
            ).total_seconds() / 3600

            if (
                reminder_count >= 6
                or hours_passed >= 24
            ):

                print(
                    f"\n✅ Stopped reminders for: {reminder['subject']}"
                )

                del reminders[message_id]

                save_reminders()

                continue

            # =========================
            # SEND EVERY 30 MINS
            # =========================

            minutes_since_last = (
                current_time - last_sent
            ).total_seconds() / 60

            if minutes_since_last >= 30:

                reminder_message = f"""
⏰ AMBASSADOR REMINDER

📌 Subject:
{reminder['subject']}

⚡ Please check this important update.

🔔 Reminder:
{reminder_count}/6

🤖 Google AI Guardian
"""

                print("\n⏰ Sending Reminder")

                send_whatsapp_alert(
                    reminder_message
                )

                reminders[message_id][
                    "last_sent"
                ] = current_time.isoformat()

                reminders[message_id][
                    "count"
                ] += 1

                save_reminders()

    except Exception as e:

        print("\n❌ ERROR:")
        print(str(e))

    # =========================
    # WAIT 5 MINS
    # =========================

    print("\n⏳ Waiting 5 mins...\n")

    time.sleep(300)