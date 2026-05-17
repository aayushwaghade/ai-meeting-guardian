import os
import time
import requests

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
YOUR_PHONE_NUMBER = os.getenv("YOUR_PHONE_NUMBER")

KEYWORDS = [
    "google student ambassador",
    "google ambassador",
    "google ai",
    "gemini",
    "mandatory",
    "meeting",
    "orientation",
    "bootcamp",
    "session",
    "deadline",
    "selection",
    "interview",
]

processed_emails = set()


def authenticate_gmail():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def send_whatsapp_message(message_text):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": YOUR_PHONE_NUMBER,
        "type": "text",
        "text": {
            "body": message_text
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=data
    )

    print("📤 WhatsApp Response:")
    print(response.text)


def is_google_related(subject, sender):
    text = f"{subject} {sender}".lower()

    for keyword in KEYWORDS:
        if keyword in text:
            return True

    return False


def check_inbox():
    try:
        print("🔎 Checking Inbox...")

        service = authenticate_gmail()

        results = service.users().messages().list(
            userId="me",
            maxResults=10,
            labelIds=["INBOX"]
        ).execute()

        messages = results.get("messages", [])

        if not messages:
            print("📭 No emails found.")
            return

        for msg in messages:

            if msg["id"] in processed_emails:
                continue

            message = service.users().messages().get(
                userId="me",
                id=msg["id"]
            ).execute()

            payload = message.get("payload", {})
            headers = payload.get("headers", [])

            subject = "No Subject"
            sender = "Unknown Sender"

            for header in headers:
                name = header.get("name", "")
                value = header.get("value", "")

                if name == "Subject":
                    subject = value

                if name == "From":
                    sender = value

            print("----------------------")
            print(f"📌 SUBJECT: {subject}")
            print(f"👤 SENDER: {sender}")

            if is_google_related(subject, sender):

                whatsapp_text = f"""
🚨 GOOGLE AMBASSADOR UPDATE

📌 Subject:
{subject}

👤 Sender:
{sender}
"""

                send_whatsapp_message(whatsapp_text)

            processed_emails.add(msg["id"])

    except Exception as e:
        print("❌ ERROR:")
        print(e)


def start_monitoring():
    while True:
        check_inbox()
        print("⏳ Waiting 5 mins...")
        time.sleep(300)