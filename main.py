import os
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from telegram import Bot
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
THRESHOLD = 100  # Пороговая сумма ставки

bot = Bot(token=TOKEN)

URL_BASE = "https://www.oddsmath.com/matches"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def send_message(text):
    try:
        bot.send_message(chat_id=CHAT_ID, text=text)
        log(f"Отправлено: {text}")
    except Exception as e:
        log(f"Ошибка отправки сообщения: {e}")

def fetch_matches_for_date(date_str):
    url = f"{URL_BASE}/{date_str}/"
    log(f"Загружаем список матчей: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        log(f"Код ответа: {response.status_code}")
        if response.status_code != 200:
            log(f"Ошибка загрузки страницы: {response.status_code}")
            return []
        soup = BeautifulSoup(response.text, "html.parser")
        match_links = soup.select(".event-table tr a[href*='/match/']")
        links = ["https://www.oddsmath.com" + a["href"] for a in match_links if "/match/" in a["href"]]
        log(f"Найдено ссылок: {len(links)}")
        return links
    except Exception as e:
        log(f"Ошибка при загрузке списка матчей: {e}")
        return []

def check_match(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            log(f"Не удалось загрузить матч: {url}")
            return False

        soup = BeautifulSoup(resp.text, "html.parser")
        bets = soup.select("div.market-line")
        for bet in bets:
            back = bet.select_one("div.back div.value")
            if back:
                value = back.text.replace("€", "").replace(",", "").strip()
                if value.isdigit() and int(value) >= THRESHOLD:
                    msg = f"💰 BACK: {value} €\n{url}"
                    send_message(msg)
                    return True
        return False
    except Exception as e:
        log(f"Ошибка при проверке матча {url}: {e}")
        return False

if __name__ == "__main__":
    seen = set()
    while True:
        today = datetime.now().strftime("%Y-%m-%d")
        matches = fetch_matches_for_date(today)
        for match_url in matches:
            if match_url not in seen:
                seen.add(match_url)
                check_match(match_url)
                time.sleep(1)
        time.sleep(1800)  # Каждые 30 минут
