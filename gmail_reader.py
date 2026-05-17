from bs4 import BeautifulSoup
import os
import base64
import requests
import json
import time
import re

from datetime import datetime, timedelta
from email import message_from_bytes

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

print("🚀 Bot Started Successfully")
print("🤖 Google AI Guardian Running...")
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
        json.dump(reminders, f, indent=4)

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

    try:

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

    except Exception as e:

        print("\n❌ WhatsApp Error")
        print(str(e))

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
    "demo session",
    "google",
    "gemini"

]

# =========================
# EXTRACT MEETING TIME
# =========================

def extract_meeting_time(text):

    patterns = [

        r'(\d{1,2}:\d{2}\s?(AM|PM))',
        r'(\d{1,2}\s?(AM|PM))'

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return match.group(1)

    return None

# =========================
# EXTRACT DAY
# =========================

def extract_day(text):

    days = [

        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday"

    ]

    text_lower = text.lower()

    for day in days:

        if day in text_lower:
            return day.capitalize()

    return None

# =========================
# MAIN LOOP
# =========================

while True:

    try:

        print("\n🔎 Checking Inbox...")

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

            try:

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

                                if content_type == "text/plain":

                                    body += decoded_payload

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
                    # SKIP DUPLICATES
                    # =========================

                    if message_id in reminders:
                        continue

                    print("\n🔥 IMPORTANT AMBASSADOR EMAIL FOUND")

                    # =========================
                    # EXTRACT MEETING INFO
                    # =========================

                    meeting_time = extract_meeting_time(
                        body
                    )

                    meeting_day = extract_day(
                        body
                    )

                    # =========================
                    # WHATSAPP MESSAGE
                    # =========================

                    whatsapp_message = f"""
🚨 IMPORTANT AMBASSADOR UPDATE

📌 Subject:
{subject}

👤 From:
{sender}

📅 Meeting Day:
{meeting_day if meeting_day else "Not detected"}

⏰ Meeting Time:
{meeting_time if meeting_time else "Not detected"}

📝 Details:
{body[:400]}

🔔 Reminder every 30 mins

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

                        "meeting_day": meeting_day,

                        "meeting_time": meeting_time,

                        "created_at":
                        datetime.now().isoformat(),

                        "last_sent":
                        datetime.now().isoformat(),

                        "count": 1,

                        "meeting_reminder_sent": False
                    }

                    save_reminders()

            except Exception as email_error:

                print("\n❌ EMAIL PROCESSING ERROR")
                print(str(email_error))

        # =========================
        # SEND REMINDERS
        # =========================

        current_time = datetime.now()

        for message_id in list(reminders.keys()):

            try:

                reminder = reminders[message_id]

                created_at = datetime.fromisoformat(
                    reminder["created_at"]
                )

                last_sent = datetime.fromisoformat(
                    reminder["last_sent"]
                )

                reminder_count = reminder["count"]

                # =========================
                # AUTO STOP
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
                # NORMAL REMINDER
                # =========================

                minutes_since_last = (
                    current_time - last_sent
                ).total_seconds() / 60

                if minutes_since_last >= 30:

                    reminder_message = f"""
⏰ AMBASSADOR REMINDER

📌 Subject:
{reminder['subject']}

📅 Day:
{reminder['meeting_day']}

⏰ Time:
{reminder['meeting_time']}

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

                # =========================
                # 30 MIN MEETING ALERT
                # =========================

                if (
                    reminder["meeting_time"]
                    and not reminder["meeting_reminder_sent"]
                ):

                    try:

                        meeting_datetime = datetime.strptime(
                            reminder["meeting_time"],
                            "%I:%M %p"
                        )

                        meeting_today = current_time.replace(
                            hour=meeting_datetime.hour,
                            minute=meeting_datetime.minute,
                            second=0
                        )

                        minutes_left = (
                            meeting_today - current_time
                        ).total_seconds() / 60

                        if 0 <= minutes_left <= 30:

                            meeting_alert = f"""
⏰ MEETING STARTS SOON

📌 {reminder['subject']}

📅 {reminder['meeting_day']}

🕒 {reminder['meeting_time']}

⚡ Starts in less than 30 minutes.

🤖 Google AI Guardian
"""

                            send_whatsapp_alert(
                                meeting_alert
                            )

                            reminders[message_id][
                                "meeting_reminder_sent"
                            ] = True

                            save_reminders()

                            print(
                                "\n📅 Meeting reminder sent."
                            )

                    except Exception as meeting_error:

                        print(
                            "\n❌ Meeting Reminder Error"
                        )

                        print(str(meeting_error))

            except Exception as reminder_error:

                print("\n❌ Reminder Error")
                print(str(reminder_error))

    except Exception as main_error:

        print("\n❌ MAIN LOOP ERROR")
        print(str(main_error))

    # =========================
    # WAIT 5 MINS
    # =========================

    print("\n⏳ Waiting 5 mins...\n")

    time.sleep(300)