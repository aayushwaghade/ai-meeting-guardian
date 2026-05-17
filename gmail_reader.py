import os
import json
import time
import base64

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

KEYWORDS = [
    "google student ambassador",
    "google ambassador",
    "gemini ambassador",
    "google campus ambassador",
    "student ambassador",
    "google developer student club",
    "gdsc",
    "google ai",
    "google community",
]

PROCESSED_FILE = "processed_emails.txt"


def load_credentials():
    token_json = os.getenv("GOOGLE_TOKEN")

    if not token_json:
        raise Exception("GOOGLE_TOKEN variable missing in Railway")

    token_data = json.loads(token_json)

    creds = Credentials.from_authorized_user_info(token_data, SCOPES)

    return creds


def get_service():
    creds = load_credentials()
    service = build("gmail", "v1", credentials=creds)
    return service


def load_processed():
    if not os.path.exists(PROCESSED_FILE):
        return set()

    with open(PROCESSED_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())


def save_processed(email_id):
    with open(PROCESSED_FILE, "a") as f:
        f.write(email_id + "\n")


def is_important(subject):
    subject = subject.lower()

    for keyword in KEYWORDS:
        if keyword.lower() in subject:
            return True

    return False


def check_inbox():
    try:
        print("🔎 Checking Inbox...")

        service = get_service()

        results = service.users().messages().list(
            userId="me",
            maxResults=10
        ).execute()

        messages = results.get("messages", [])

        processed = load_processed()

        for msg in messages:

            email_id = msg["id"]

            if email_id in processed:
                continue

            message = service.users().messages().get(
                userId="me",
                id=email_id
            ).execute()

            headers = message["payload"]["headers"]

            subject = "No Subject"
            sender = "Unknown Sender"

            for header in headers:

                if header["name"] == "Subject":
                    subject = header["value"]

                if header["name"] == "From":
                    sender = header["value"]

            important = is_important(subject)

            print("\n========================")
            print(f"📌 SUBJECT: {subject}")
            print(f"👤 SENDER: {sender}")
            print(f"🔥 Important Subject: {important}")
            print("========================\n")

            save_processed(email_id)

    except Exception as e:
        print("\n❌ ERROR:\n")
        print(e)


def start_monitoring():
    while True:
        check_inbox()
        print("⏳ Waiting 5 mins...\n")
        time.sleep(300)


print("🚀 Google AI Guardian Running...")
print("📬 Monitoring Google Ambassador Updates...")
print("🤖 Bot Started Successfully\n")

start_monitoring()