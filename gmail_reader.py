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

service = build("gmail", "v1", credentials=creds)

# ============================================
# WHATSAPP FUNCTION
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

    response = requests.post(url, headers=headers, json=data)

    print("\n📲 WhatsApp Sent")
    print("Status:", response.status_code)
    print(response.text)

# ============================================
# OPENROUTER AI ANALYSIS
# ============================================

def analyze_email_with_ai(subject, body):

    try:

        api_key = os.environ["OPENROUTER_API_KEY"]

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        prompt = f"""
Analyze this email.

Return ONLY in this format:

SUMMARY:
<short summary>

PRIORITY:
HIGH / MEDIUM / LOW

MEETING:
<meeting date and time if exists otherwise N/A>

DEADLINE:
<deadline if exists otherwise N/A>

EMAIL:

Subject:
{subject}

Body:
{body[:3000]}
"""

        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )

        result = response.json()

        ai_text = result["choices"][0]["message"]["content"]

        return ai_text

    except Exception as e:

        print("❌ AI ERROR:", e)

        return """
SUMMARY:
Could not analyze email

PRIORITY:
MEDIUM

MEETING:
N/A

DEADLINE:
N/A
"""

# ============================================
# IMPORTANT FILTERS
# ============================================

TRUSTED_SENDERS = [

    "google",
    "pingnetwork",
    "ambassador",
    "gemini",
    "gdg",
    "developer",
    "tensorflow",
    "github",
    "google for developers"

]

IMPORTANT_SUBJECTS = [

    "mandatory demo session",
    "task 1",
    "google student ambassador",
    "career glow-up",
    "nano banana",
    "ambassador",
    "demo session",
    "google",
    "gemini",
    "pixel phone",
    "submission",
    "task expectations",
    "event flow",
    "session",
    "career",
    "glow-up",
    "task",
    "may task",
    "google ambassador"

]

# ============================================
# REMINDER STORAGE
# ============================================

REMINDER_FILE = "sent_emails.json"

if not os.path.exists(REMINDER_FILE):

    with open(REMINDER_FILE, "w") as f:
        json.dump({}, f)

with open(REMINDER_FILE, "r") as f:
    sent_emails = json.load(f)

# ============================================
# EXTRACT MEETING TIME
# ============================================

def extract_meeting_time(text):

    patterns = [

        r'(\d{1,2}:\d{2}\s?(AM|PM|am|pm))',
        r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
        r'(\d{1,2}\s?(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec))'

    ]

    found = []

    for pattern in patterns:

        matches = re.findall(pattern, text, re.IGNORECASE)

        if matches:
            found.extend(matches)

    return found

# ============================================
# MAIN LOOP
# ============================================

while True:

    try:

        print("\n🔎 Checking Inbox...")

        results = service.users().messages().list(
            userId="me",
            maxResults=10,
            labelIds=["INBOX"]
        ).execute()

        messages = results.get("messages", [])

        for msg in messages:

            msg_id = msg["id"]

            txt = service.users().messages().get(
                userId="me",
                id=msg_id,
                format="raw"
            ).execute()

            raw_data = base64.urlsafe_b64decode(txt["raw"])

            email_message = message_from_bytes(raw_data)

            subject = email_message["subject"] or ""
            sender = email_message["from"] or ""

            body = ""

            if email_message.is_multipart():

                for part in email_message.walk():

                    content_type = part.get_content_type()

                    try:

                        payload = part.get_payload(decode=True)

                        if payload:

                            decoded = payload.decode(errors="ignore")

                            if content_type == "text/plain":
                                body += decoded

                            elif content_type == "text/html":

                                soup = BeautifulSoup(decoded, "html.parser")

                                clean_text = soup.get_text(separator=" ")

                                body += clean_text

                    except:
                        pass

            else:

                try:

                    payload = email_message.get_payload(decode=True)

                    if payload:
                        body += payload.decode(errors="ignore")

                except:
                    pass

            full_text = f"{subject} {body}".lower()

            trusted_sender = any(
                keyword.lower() in sender.lower()
                for keyword in TRUSTED_SENDERS
            )

            important_subject = any(
                keyword.lower() in full_text
                for keyword in IMPORTANT_SUBJECTS
            )

            # ============================================
            # DEBUG LOGS
            # ============================================

            print("\n-------------------------")
            print("📌 SUBJECT:", subject)
            print("👤 SENDER:", sender)
            print("✅ Trusted Sender:", trusted_sender)
            print("🔥 Important Subject:", important_subject)
            print("-------------------------")

            # ============================================
            # MATCH FILTER
            # ============================================

            if trusted_sender and important_subject:

                if msg_id not in sent_emails:

                    print("✅ IMPORTANT EMAIL DETECTED")

                    ai_analysis = analyze_email_with_ai(
                        subject,
                        body[:3000]
                    )

                    # ============================================
                    # MEETING EXTRACTION
                    # ============================================

                    detected_times = extract_meeting_time(body)

                    meeting_text = ""

                    if detected_times:

                        meeting_text = "\n📅 Meeting Time Detected:\n"

                        for t in detected_times:
                            meeting_text += f"{t}\n"

                        meeting_text += "\n⏰ Reminder scheduled"

                    # ============================================
                    # FINAL WHATSAPP MESSAGE
                    # ============================================

                    whatsapp_message = f"""
🚨 IMPORTANT GOOGLE UPDATE

📌 Subject:
{subject}

👤 From:
{sender}

🧠 AI Analysis:
{ai_analysis}

{meeting_text}

🤖 Google AI Guardian

Reply DONE after completing task.
"""

                    print("\n" + "=" * 60)
                    print(whatsapp_message)
                    print("=" * 60)

                    send_whatsapp_alert(whatsapp_message)

                    # ============================================
                    # SAVE SENT EMAIL
                    # ============================================

                    sent_emails[msg_id] = {
                        "subject": subject,
                        "time": str(datetime.now())
                    }

                    with open(REMINDER_FILE, "w") as f:
                        json.dump(sent_emails, f, indent=4)

                else:

                    print("⏭ Already alerted before")

        print("\n⏳ Waiting 5 mins...")
        time.sleep(300)

    except Exception as e:

        print("❌ ERROR:", e)

        time.sleep(60)