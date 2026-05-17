from bs4 import BeautifulSoup
import os
import base64
import requests
import json
from email import message_from_bytes
from datetime import datetime, timedelta

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from openai import OpenAI

print("🚀 AI Meeting Guardian Running 24/7...")
print("📩 Checking Important Emails...")

# =========================
# OPENROUTER AI
# =========================

client = OpenAI(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

# =========================
# GOOGLE CREDENTIALS
# =========================

google_credentials = json.loads(
    os.environ["GOOGLE_CREDENTIALS"]
)

creds = Credentials(
    None,
    refresh_token=google_credentials["refresh_token"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=google_credentials["client_id"],
    client_secret=google_credentials["client_secret"],
    scopes=[
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/calendar"
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

calendar_service = build(
    "calendar",
    "v3",
    credentials=creds
)

# =========================
# WHATSAPP ALERT FUNCTION
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

    print("\n📲 WhatsApp Debug Logs")
    print("WhatsApp Status:", response.status_code)
    print("WhatsApp Response:", response.text)

# =========================
# AI SUMMARY FUNCTION
# =========================

def generate_ai_summary(email_text):

    try:

        prompt = f"""
You are an AI executive assistant.

Analyze this email and provide:

1. Short summary
2. Priority (LOW, MEDIUM, HIGH)
3. Meeting information
4. Deadline information

Email:
{email_text}

Format EXACTLY like this:

SUMMARY:
...

PRIORITY:
...

MEETING:
...

DEADLINE:
...
"""

        completion = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return completion.choices[0].message.content

    except Exception as e:

        print("AI Error:", str(e))

        return """
SUMMARY:
AI summary unavailable

PRIORITY:
MEDIUM

MEETING:
None

DEADLINE:
None
"""

# =========================
# CALENDAR EXTRACTION
# =========================

def extract_calendar_event(email_text):

    try:

        prompt = f"""
Extract meeting/event information from this email.

Return ONLY valid JSON.

Format:

{{
  "title": "",
  "date": "",
  "time": "",
  "description": ""
}}

Use:
- date format: YYYY-MM-DD
- time format: HH:MM (24 hour)

If no meeting exists return:

{{
  "title": "NONE"
}}

Email:
{email_text}
"""

        completion = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response = completion.choices[0].message.content

        print("\n📅 Event Extraction:")
        print(response)

        return json.loads(response)

    except Exception as e:

        print("Calendar AI Error:", str(e))

        return {
            "title": "NONE"
        }

# =========================
# CREATE CALENDAR EVENT
# =========================

def create_calendar_event(
    title,
    date,
    time_text,
    description
):

    try:

        start_datetime = datetime.strptime(
            f"{date} {time_text}",
            "%Y-%m-%d %H:%M"
        )

        end_datetime = start_datetime + timedelta(hours=1)

        event = {
            "summary": title,
            "description": description,
            "start": {
                "dateTime": start_datetime.isoformat(),
                "timeZone": "Asia/Kolkata",
            },
            "end": {
                "dateTime": end_datetime.isoformat(),
                "timeZone": "Asia/Kolkata",
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {
                        "method": "popup",
                        "minutes": 30
                    }
                ],
            },
        }

        created_event = calendar_service.events().insert(
            calendarId="primary",
            body=event
        ).execute()

        print("📅 Calendar Event Created!")

        return created_event.get("htmlLink")

    except Exception as e:

        print("Calendar Error:", str(e))

        return None

# =========================
# KEYWORDS
# =========================

IMPORTANT_KEYWORDS = [
    "meeting",
    "interview",
    "deadline",
    "assignment",
    "zoom",
    "google meet",
    "task",
    "important",
    "urgent",
    "demo",
    "submission",
    "exam",
    "token",
    "security",
    "alert",
    "github",
    "session",
    "schedule"
]

# =========================
# FETCH EMAILS
# =========================

results = service.users().messages().list(
    userId="me",
    maxResults=10,
    labelIds=["INBOX"]
).execute()

messages = results.get("messages", [])

important_found = False

# =========================
# PROCESS EMAILS
# =========================

for msg in messages:

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
                        body += decoded_payload

            except:
                pass

    else:

        try:

            payload = email_message.get_payload(
                decode=True
            )

            if payload:
                body += payload.decode(
                    errors="ignore"
                )

        except:
            pass

    # =========================
    # CLEAN HTML
    # =========================

    clean_text = BeautifulSoup(
        body,
        "html.parser"
    ).get_text()

    clean_text = clean_text.replace("\n", " ")
    clean_text = clean_text.replace("\r", " ")
    clean_text = clean_text.replace("\t", " ")

    clean_text = " ".join(
        clean_text.split()
    )

    full_text = f"{subject} {clean_text}".lower()

    # =========================
    # IMPORTANT EMAIL CHECK
    # =========================

    if any(
        keyword in full_text
        for keyword in IMPORTANT_KEYWORDS
    ):

        important_found = True

        # =========================
        # AI ANALYSIS
        # =========================

        ai_response = generate_ai_summary(
            clean_text[:3000]
        )

        # =========================
        # EVENT EXTRACTION
        # =========================

        event_data = extract_calendar_event(
            clean_text[:3000]
        )

        calendar_message = ""

        if event_data.get("title") != "NONE":

            event_link = create_calendar_event(
                event_data["title"],
                event_data["date"],
                event_data["time"],
                event_data["description"]
            )

            if event_link:

                calendar_message = f"""

📅 Calendar Event Created

🗓 Title:
{event_data['title']}

⏰ Time:
{event_data['date']} {event_data['time']}

🔗 Event Link:
{event_link}
"""

        # =========================
        # FINAL WHATSAPP MESSAGE
        # =========================

        whatsapp_message = f"""
🚨 IMPORTANT EMAIL

📌 Subject:
{subject}

👤 From:
{sender}

🧠 AI Analysis:
{ai_response}

{calendar_message}

🤖 AI Meeting Guardian
"""

        print("\n" + "=" * 60)
        print(whatsapp_message)
        print("=" * 60)

        send_whatsapp_alert(
            whatsapp_message
        )

# =========================
# NO IMPORTANT EMAILS
# =========================

if not important_found:
    print("❌ No important emails found.")