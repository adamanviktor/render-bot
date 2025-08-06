import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
import telegram
import time

# Загрузка токена и chat_id из .env
load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = telegram.Bot(token=TOKEN)

# Константы
URL_BASE = "https://www.oddsmath.com/football/live/"
HEADERS = {"User-Agent": "Mozilla/5.0"}
THRESHOLD = 100  # €вро

# Вспомогательные функции
def get_html():
    try:
        response = requests.get(URL_BASE, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print("Ошибка загрузки страницы:", e)
        return ""

def parse_bets(html):
    soup = BeautifulSoup(html, "html.parser")
    bets = []

    for row in soup.select("tr"):
        try:
            stake_cell = row.find("td", class_="stake")
            if not stake_cell:
                continue

            stake_value = int(stake_cell.text.replace("€", "").replace(",", "").strip())

            if stake_value >= THRESHOLD:
                match = row.find("td", class_="match").text.strip()
                time_str = datetime.now().strftime("%d.%m %H:%M")
                bets.append(f"⚽ {match} — {stake_value} €\n⏰ {time_str}")
        except:
            continue

    return bets

# Основной цикл
def main():
    while True:
        html = get_html()
        bets = parse_bets(html)
        for bet in bets:
            bot.send_message(chat_id=CHAT_ID, text=bet)
        time.sleep(60)

if __name__ == "__main__":
    main()
