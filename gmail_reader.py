import os
import json
import time

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from whatsapp_sender import send_whatsapp_message


# =========================
# GOOGLE AUTH FROM RAILWAY ENV
# =========================

credentials_data = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
token_data = json.loads(os.getenv("GOOGLE_TOKEN"))

creds = Credentials.from_authorized_user_info(
    token_data,
    ['https://www.googleapis.com/auth/gmail.readonly']
)

service = build('gmail', 'v1', credentials=creds)


# =========================
# LOAD PROCESSED EMAILS
# =========================

PROCESSED_FILE = "processed_emails.txt"

if not os.path.exists(PROCESSED_FILE):
    open(PROCESSED_FILE, "w").close()

with open(PROCESSED_FILE, "r") as f:
    processed_emails = set(f.read().splitlines())


# =========================
# GOOGLE AMBASSADOR KEYWORDS
# =========================

KEYWORDS = [
    "google student ambassador",
    "ambassador program",
    "google ambassador",
    "career glow-up",
    "nano banana",
    "mandatory demo session",
    "pingnetwork",
    "google student",
    "task 1",
]


# =========================
# CHECK GMAIL
# =========================

def check_emails():

    print("🔎 Checking Inbox...")

    results = service.users().messages().list(
        userId='me',
        maxResults=10,
        labelIds=['INBOX'],
        q="is:unread"
    ).execute()

    messages = results.get('messages', [])

    if not messages:
        print("No new unread messages.")
        return

    for msg in messages:

        msg_id = msg['id']

        if msg_id in processed_emails:
            continue

        message = service.users().messages().get(
            userId='me',
            id=msg_id
        ).execute()

        headers = message["payload"]["headers"]

        subject = "No Subject"
        sender = "Unknown Sender"

        for header in headers:

            if header["name"] == "Subject":
                subject = header["value"]

            if header["name"] == "From":
                sender = header["value"]

        # =========================
        # FILTER ONLY GOOGLE AMBASSADOR EMAILS
        # =========================

        email_text = f"{subject} {sender}".lower()

        if not any(keyword in email_text for keyword in KEYWORDS):
            print(f"⏭ Skipped: {subject}")
            continue

        print(f"\n📩 Google Ambassador Email Found")
        print(f"From: {sender}")
        print(f"Subject: {subject}")

        whatsapp_text = f"""
🔥 *Google Student Ambassador Alert*

👤 From:
{sender}

📌 Subject:
{subject}

🚀 Check Gmail now.
"""

        send_whatsapp_message(whatsapp_text)

        processed_emails.add(msg_id)

        with open(PROCESSED_FILE, "a") as f:
            f.write(msg_id + "\n")


# =========================
# LOOP
# =========================

while True:

    try:
        check_emails()

    except Exception as e:
        print("\n❌ ERROR:")
        print(e)

    print("⏳ Waiting 5 mins...\n")

    time.sleep(300)