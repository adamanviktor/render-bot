import os
import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
from telegram import Bot
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
THRESHOLD = int(os.getenv("THRESHOLD", "100"))  # по умолчанию 100

bot = Bot(token=TOKEN)
URL_BASE = "https://www.oddsmath.com/matches/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0 Safari/537.36"
}

checked_urls = set()

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def fetch_matches_for_date(date_str):
    url = URL_BASE + date_str + "/"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            log(f"Ошибка загрузки {url}")
            return []
        soup = BeautifulSoup(response.text, "html.parser")
        match_links = soup.select(".event-table tr a[href]")
        full_urls = ["https://www.oddsmath.com" + link["href"] for link in match_links if '/match/' in link["href"]]
        return list(set(full_urls))
    except Exception as e:
        log(f"Ошибка: {e}")
        return []

def check_match(url):
    if url in checked_urls:
        return
    checked_urls.add(url)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return
        soup = BeautifulSoup(resp.text, "html.parser")
        bets = soup.select("div.market-line")
        for bet in bets:
            back = bet.select_one("div.back div.value")
            if back:
                value = back.text.replace("€", "").replace(",", "").strip()
                if value.isdigit() and int(value) >= THRESHOLD:
                    msg = f"💰 BACK: {value} €\n{url}"
                    bot.send_message(chat_id=CHAT_ID, text=msg)
                    log(f"Отправлено: {msg}")
                    return
    except Exception as e:
        log(f"Ошибка при проверке {url}: {e}")

# Main
if __name__ == "__main__":
    while True:
        today = datetime.now().strftime("%Y-%m-%d")
        matches = fetch_matches_for_date(today)
        log(f"Найдено матчей: {len(matches)}")
        for match_url in matches:
            check_match(match_url)
            time.sleep(1)
        time.sleep(1800)  # каждые 30 минут
