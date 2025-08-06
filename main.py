import os
from dotenv import load_dotenv
load_dotenv()  # <<< ЭТОГО НЕ БЫЛО

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import telegram
import time

# Telegram config
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = telegram.Bot(token=TOKEN)

# Constants
URL_BASE = "https://www.oddsmath.com/football/"
HEADERS = {"User-Agent": "Mozilla/5.0"}
THRESHOLD = 100  # Евро

# Helpers
def log(message):
    print(f"[{datetime.now().isoformat()}] {message}")

def send_message(text):
    bot.send_message(chat_id=CHAT_ID, text=text)

# Main logic
def check_matches():
    response = requests.get(URL_BASE, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    matches = soup.find_all("tr", class_="match")
    for match in matches:
        back = match.find("td", class_="back")
        if back and back.text:
            try:
                amount = int(back.text.replace("€", "").replace(",", "").strip())
                if amount >= THRESHOLD:
                    log(f"Найдена ставка: {amount}€")
                    send_message(f"🔔 Найдена ставка: {amount}€\n{match.text.strip()}")
            except:
                pass

while True:
    try:
        check_matches()
    except Exception as e:
        log(f"Ошибка: {e}")
    time.sleep(300)  # каждые 5 минут
