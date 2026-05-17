import os
import json
import base64
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
# CHECK GMAIL
# =========================

def check_emails():

    print("🔎 Checking Inbox...")

    results = service.users().messages().list(
        userId='me',
        maxResults=5,
        labelIds=['INBOX']
    ).execute()

    messages = results.get('messages', [])

    if not messages:
        print("No messages found.")
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

        print(f"\n📩 New Email Found")
        print(f"From: {sender}")
        print(f"Subject: {subject}")

        whatsapp_text = f"""
📩 *New Important Email*

👤 From:
{sender}

📌 Subject:
{subject}

Reply DONE after completing task.
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