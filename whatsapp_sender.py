# whatsapp_sender.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

phone_number = "919404319706"
message = "🔥 AI Meeting Guardian Activated Successfully"

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install())
)

driver.get(f"https://web.whatsapp.com/send?phone={phone_number}&text={message}")

print("Scan QR Code if needed...")
time.sleep(25)

message_box = driver.find_element(
    By.XPATH,
    '//div[@contenteditable="true"][@data-tab="10"]'
)

message_box.send_keys(Keys.ENTER)

print("Message Sent Successfully ✅")

time.sleep(10)
driver.quit()