import os
import base64
import requests
import json
from email import message_from_bytes

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

print("🚀 AI Meeting Guardian Running 24/7...")
print("📩 Checking Important Emails...")

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
    scopes=["https://www.googleapis.com/auth/gmail.readonly"]
)

creds.refresh(Request())

# =========================
# GMAIL SERVICE
# =========================

service = build("gmail", "v1", credentials=creds)

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

    response = requests.post(url, headers=headers, json=data)

    print("📲 WhatsApp Response:")
    print(response.text)

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
    "exam"
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

                if payload and content_type == "text/plain":
                    body += payload.decode()

            except:
                pass

    else:

        try:
            payload = email_message.get_payload(decode=True)

            if payload:
                body += payload.decode()

        except:
            pass

    full_text = f"{subject} {body}".lower()

    # =========================
    # IMPORTANT EMAIL DETECTION
    # =========================

    if any(keyword in full_text for keyword in IMPORTANT_KEYWORDS):

        important_found = True

        whatsapp_message = f"""
🔥 IMPORTANT EMAIL FOUND

📌 SUBJECT:
{subject}

📩 FROM:
{sender}

📝 SNIPPET:
{body[:300]}

🤖 AI Meeting Guardian
"""

        print("=" * 60)
        print(whatsapp_message)
        print("=" * 60)

        send_whatsapp_alert(whatsapp_message)

# =========================
# NO IMPORTANT EMAILS
# =========================

if not important_found:
    print("❌ No important emails found.")