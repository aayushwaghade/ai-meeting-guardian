import time
import schedule
import os

def run_guardian():

    print("\n🚀 AI Meeting Guardian Checking Gmail...\n")

    os.system("python gmail_reader.py")

# Run immediately
run_guardian()

# Run every 5 minutes
schedule.every(5).minutes.do(run_guardian)

print("🤖 AI Meeting Guardian Running 24/7...\n")

while True:

    schedule.run_pending()

    time.sleep(1)