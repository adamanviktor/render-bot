import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
import telegram
import time

# Загружаем переменные окружения из .env
load_dotenv()

# Telegram config
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = telegram.Bot(token=TOKEN)

# Constants
URL_BASE = "https://www.oddsmath.com/football/"
HEADERS = {"User-Agent": "Mozilla/5.0"}
THRESHOLD = 100  # Евро

# Helpers
def send_telegram_message(message):
    bot.send_message(chat_id=CHAT_ID, text=message)

def check_odds():
    response = requests.get(URL_BASE, headers=HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")
    bets = soup.find_all("tr", class_="odd")

    for bet in bets:
        try:
            stake = bet.find("td", class_="stake").text.strip()
            stake_value = float(stake.replace("€", "").replace(",", ""))

            if stake_value >= THRESHOLD:
                match = bet.find("td", class_="match").text.strip()
                time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = f"⚠️ {time_str}\n{match}\nСтавка: €{stake_value}"
                send_telegram_message(message)
        except Exception as e:
            continue

# Main loop
while True:
    check_odds()
    time.sleep(60)
