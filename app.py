from flask import Flask
import threading
from gmail_reader import start_monitoring

app = Flask(__name__)

@app.route("/")
def home():
    return "AI Meeting Guardian Running"

# START EMAIL MONITOR IN BACKGROUND
threading.Thread(
    target=start_monitoring,
    daemon=True
).start()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080
    )