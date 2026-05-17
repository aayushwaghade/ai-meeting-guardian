from bs4 import BeautifulSoup
import os
import base64
import requests
import json
import re
import time
import dateparser

from datetime import datetime
from email import message_from_bytes

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

print("🚀 Google AI Guardian Running...")
print("📩 Monitoring Google Ambassador Updates...")

# ============================================
# GOOGLE CREDENTIALS
# ============================================

google_credentials = json.loads(
    os.environ["GOOGLE_CREDENTIALS"]
)

creds = Credentials(
    None,
    refresh_token=google_credentials["refresh_token"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=google_credentials["client_id"],
    client_secret=google_credentials["client_secret"],
    scopes=["https://www.googleapis.com/auth/gmail.readonly"]
)

creds.refresh(Request())

# ============================================
# GMAIL SERVICE
# ============================================

service = build(
    "gmail",
    "v1",
    credentials=creds
)

# ============================================
# REMINDER STORAGE
# ============================================

REMINDER_FILE = "reminders.json"

# ============================================
# LOAD REMINDERS
# ============================================

def load_reminders():

    if not os.path.exists(REMINDER_FILE):

        with open(REMINDER_FILE, "w") as f:
            json.dump({}, f)

    with open(REMINDER_FILE, "r") as f:
        return json.load(f)

# ============================================
# SAVE REMINDERS
# ============================================

def save_reminders(data):

    with open(REMINDER_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ============================================
# WHATSAPP ALERT FUNCTION
# ============================================

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

# ============================================
# GOOGLE STUDENT AMBASSADOR SENDERS
# ============================================

TRUSTED_SENDERS = [

    "google",
    "google.com",
    "developers.google.com",
    "googlecloud",
    "googlefordevelopers",
    "gdg",
    "gdsc",
    "women techmakers",
    "tensorflow",
    "startupschool",
    "no-reply@google.com",
    "@google.com"
]

# ============================================
# GOOGLE AMBASSADOR KEYWORDS
# ============================================

IMPORTANT_SUBJECT_KEYWORDS = [

    "google student ambassador",
    "gemini student ambassador",
    "google ambassador",
    "ambassador program",
    "ambassador task",
    "task submission",
    "submission deadline",
    "mandatory session",
    "mandatory meeting",
    "orientation session",
    "google developers",
    "google for developers",
    "gdg",
    "gdsc",
    "certificate",
    "selected",
    "congratulations",
    "welcome ambassador",
    "community lead",
    "career glow up",
    "gemini",
    "google ai",
    "google event",
    "bootcamp",
    "hackathon",
    "developer program",
    "developer student club"
]

# ============================================
# MEETING TIME EXTRACTION
# ============================================

def extract_meeting_datetime(text):

    patterns = [

        r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday).*?\d{1,2}:\d{2}\s?(AM|PM|am|pm)",

        r"\d{1,2}\s(January|February|March|April|May|June|July|August|September|October|November|December).*?\d{1,2}:\d{2}\s?(AM|PM|am|pm)",

        r"(tomorrow).*?\d{1,2}:\d{2}\s?(AM|PM|am|pm)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            detected_text = match.group(0)

            parsed_date = dateparser.parse(
                detected_text,
                settings={
                    "PREFER_DATES_FROM": "future"
                }
            )

            if parsed_date:
                return parsed_date

    return None

# ============================================
# CLEAN IMPORTANT EMAIL FILTER
# ============================================

def is_important_email(subject, sender, body):

    sender_lower = sender.lower()
    subject_lower = subject.lower()
    body_lower = body.lower()

    trusted_sender = any(
        keyword in sender_lower
        for keyword in TRUSTED_SENDERS
    )

    important_subject = any(
        keyword in subject_lower
        for keyword in IMPORTANT_SUBJECT_KEYWORDS
    )

    important_body = any(
        keyword in body_lower
        for keyword in IMPORTANT_SUBJECT_KEYWORDS
    )

    # STRICT FILTER
    is_important = (
        trusted_sender
        and
        (
            important_subject
            or important_body
        )
    )

    # ONLY PRINT IMPORTANT EMAILS
    if is_important:

        print("\n======================")
        print("🚨 IMPORTANT EMAIL DETECTED")
        print(f"📌 SUBJECT: {subject}")
        print(f"👤 SENDER: {sender}")
        print("======================")

    return is_important

# ============================================
# MAIN MONITOR LOOP
# ============================================

def start_monitoring():

    print("🚀 Bot Started Successfully")
    print("🤖 Google AI Guardian Running...")
    print("📬 Monitoring Google Ambassador Updates...")

    while True:

        try:

            print("\n🔎 Checking Inbox...")

            reminders = load_reminders()

            # ============================================
            # CHECK MEETING REMINDERS
            # ============================================

            for reminder_id in reminders:

                reminder = reminders[reminder_id]

                if reminder["completed"]:
                    continue

                if reminder["meeting_reminder_sent"]:
                    continue

                if reminder["meeting_time"] == "":
                    continue

                meeting_time = datetime.fromisoformat(
                    reminder["meeting_time"]
                )

                current_time = datetime.now()

                time_difference = (
                    meeting_time - current_time
                ).total_seconds()

                # ============================================
                # SEND 30 MIN REMINDER
                # ============================================

                if 0 < time_difference <= 1800:

                    reminder_message = f"""
⏰ GOOGLE AMBASSADOR MEETING REMINDER

📌 Subject:
{reminder['subject']}

🚀 Starts in less than 30 minutes

📅 Time:
{meeting_time.strftime('%d %B %Y, %I:%M %p')}

Reply DONE after attending meeting.

🤖 Google AI Guardian
"""

                    send_whatsapp_alert(
                        reminder_message
                    )

                    reminders[reminder_id][
                        "meeting_reminder_sent"
                    ] = True

                    save_reminders(reminders)

                    print(reminder_message)

            # ============================================
            # FETCH EMAILS
            # ============================================

            results = service.users().messages().list(
                userId="me",
                maxResults=10,
                labelIds=["INBOX"]
            ).execute()

            messages = results.get("messages", [])

            # ============================================
            # PROCESS EMAILS
            # ============================================

            for msg in messages:

                if msg["id"] in reminders:
                    continue

                txt = service.users().messages().get(
                    userId="me",
                    id=msg["id"],
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

                # ============================================
                # EXTRACT EMAIL BODY
                # ============================================

                if email_message.is_multipart():

                    for part in email_message.walk():

                        content_type = part.get_content_type()

                        try:

                            payload = part.get_payload(
                                decode=True
                            )

                            if payload:

                                decoded = payload.decode(
                                    errors="ignore"
                                )

                                if content_type == "text/plain":
                                    body += decoded

                                elif content_type == "text/html":

                                    soup = BeautifulSoup(
                                        decoded,
                                        "html.parser"
                                    )

                                    body += soup.get_text()

                        except:
                            pass

                else:

                    try:

                        payload = email_message.get_payload(
                            decode=True
                        )

                        if payload:

                            decoded = payload.decode(
                                errors="ignore"
                            )

                            body += decoded

                    except:
                        pass

                # ============================================
                # FILTER IMPORTANT EMAILS
                # ============================================

                if not is_important_email(
                    subject,
                    sender,
                    body
                ):
                    continue

                # ============================================
                # DETECT MEETING TIME
                # ============================================

                meeting_datetime = extract_meeting_datetime(
                    body
                )

                # ============================================
                # IF MEETING DETECTED
                # ============================================

                if meeting_datetime:

                    stored_meeting_time = (
                        meeting_datetime.isoformat()
                    )

                    reminders[msg["id"]] = {

                        "subject": subject,

                        "meeting_time": stored_meeting_time,

                        "meeting_reminder_sent": False,

                        "completed": False
                    }

                    save_reminders(reminders)

                    detected_message = f"""
📅 GOOGLE AMBASSADOR MEETING DETECTED

📌 Subject:
{subject}

👤 From:
{sender}

⏰ Meeting Time:
{meeting_datetime.strftime('%d %B %Y, %I:%M %p')}

✅ 30-minute reminder scheduled

Reply DONE after completing task.

🤖 Google AI Guardian
"""

                    print(detected_message)

                    send_whatsapp_alert(
                        detected_message
                    )

                # ============================================
                # NORMAL IMPORTANT UPDATE
                # ============================================

                else:

                    whatsapp_message = f"""
🚨 IMPORTANT GOOGLE AMBASSADOR UPDATE

📌 Subject:
{subject}

👤 From:
{sender}

📝 Details:
{body[:500]}

🤖 Google AI Guardian
"""

                    print(whatsapp_message)

                    send_whatsapp_alert(
                        whatsapp_message
                    )

                    reminders[msg["id"]] = {

                        "subject": subject,

                        "meeting_time": "",

                        "meeting_reminder_sent": False,

                        "completed": False
                    }

                    save_reminders(reminders)

        except Exception as e:

            print("\n❌ ERROR:")
            print(e)

        print("\n⏳ Waiting 5 mins...\n")

        time.sleep(300)