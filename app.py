from flask import Flask
from gmail_reader import start_monitoring
import threading

app = Flask(__name__)

threading.Thread(target=start_monitoring).start()

@app.route("/")
def home():
    return "AI Meeting Guardian Running!"