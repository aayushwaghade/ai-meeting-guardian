import os
import os.path
import pickle
import asyncio
import json

from telegram import Bot

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# ==========================================
# GOOGLE CLOUD CREDENTIALS
# ==========================================

google_credentials = json.loads(
    os.environ["GOOGLE_CREDENTIALS"]
)

# ==========================================
# TELEGRAM SETTINGS
# ==========================================

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# ==========================================
# GMAIL SETTINGS
# ==========================================

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# ==========================================
# CREATE CREDS FROM ENV
# ==========================================

creds = Credentials(
    None,
    refresh_token=google_credentials["refresh_token"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=google_credentials["client_id"],
    client_secret=google_credentials["client_secret"],
    scopes=SCOPES
)

# ==========================================
# REFRESH TOKEN
# ==========================================

creds.refresh(Request())

# ==========================================
# CONNECT GMAIL API
# ==========================================

service = build('gmail', 'v1', credentials=creds)

# ==========================================
# FETCH EMAILS
# ==========================================

results = service.users().messages().list(
    userId='me',
    maxResults=20,
    labelIds=['INBOX']
).execute()

messages = results.get('messages', [])

# ==========================================
# PROCESSED EMAIL TRACKING
# ==========================================

processed_file = "processed_emails.txt"

if os.path.exists(processed_file):

    with open(processed_file, "r") as f:
        processed_ids = f.read().splitlines()

else:

    processed_ids = []

# ==========================================
# FILTER SETTINGS
# ==========================================

important_senders = [
    "google",
    "gemini",
    "pingnetwork",
    "gdg",
    "developers.google",
    "googlecloud",
    "student ambassador"
]

meeting_keywords = [
    "meeting",
    "session",
    "webinar",
    "workshop",
    "event",
    "join",
    "meet",
    "zoom",
    "gmeet",
    "registration",
    "demo session",
    "orientation",
    "live session",
    "mandatory",
    "task"
]

ignore_keywords = [
    "security alert",
    "password",
    "account access",
    "privacy",
    "verification code",
    "otp",
    "signin",
    "sign in",
    "login",
    "suspicious activity"
]

print("\n🔍 Checking Important Emails...\n")

important_found = False

# ==========================================
# TELEGRAM FUNCTION
# ==========================================

async def send_telegram_message(text):

    bot = Bot(token=BOT_TOKEN)

    await bot.send_message(
        chat_id=CHAT_ID,
        text=text
    )

# ==========================================
# EMAIL CHECK LOOP
# ==========================================

for msg in messages:

    email_id = msg['id']

    # Skip already processed emails
    if email_id in processed_ids:
        continue

    # Get full email data
    message = service.users().messages().get(
        userId='me',
        id=email_id
    ).execute()

    headers = message['payload']['headers']

    subject = ""
    sender = ""

    # Extract subject + sender
    for header in headers:

        if header['name'] == 'Subject':
            subject = header['value']

        if header['name'] == 'From':
            sender = header['value']

    # Email preview
    snippet = message.get('snippet', '')

    # Combine all text
    full_text = f"{subject} {sender} {snippet}".lower()

    # ==========================================
    # SMART FILTERING
    # ==========================================

    sender_match = any(
        word in sender.lower()
        for word in important_senders
    )

    meeting_match = any(
        word in full_text
        for word in meeting_keywords
    )

    ignore_match = any(
        word in full_text
        for word in ignore_keywords
    )

    # ==========================================
    # FINAL DETECTION
    # ==========================================

    if sender_match and meeting_match and not ignore_match:

        important_found = True

        print("🔥 IMPORTANT EMAIL FOUND")
        print("=" * 60)

        print(f"📌 SUBJECT : {subject}")
        print(f"📩 FROM    : {sender}")
        print(f"📝 SNIPPET : {snippet}")

        print("=" * 60)
        print()

        # ==========================================
        # TELEGRAM ALERT
        # ==========================================

        telegram_message = f"""
🚨 IMPORTANT EMAIL FOUND

📌 SUBJECT:
{subject}

📩 FROM:
{sender}

📝 SNIPPET:
{snippet[:200]}

🔥 CHECK GMAIL NOW
"""

        print("📲 Sending Telegram Alert...")

        asyncio.run(
            send_telegram_message(
                telegram_message
            )
        )

        # Save processed email ID
        with open(processed_file, "a") as f:
            f.write(email_id + "\n")

# ==========================================
# NO IMPORTANT EMAILS
# ==========================================

if not important_found:

    print("❌ No important emails found.")