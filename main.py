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
THRESHOLD = 100

bot = Bot(token=TOKEN)
seen_urls = set()
bad_urls = set()

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# Получение всех страниц с датами
def fetch_date_pages():
    try:
        url = "https://www.oddsmath.com/matches/"
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            log(f"Ошибка загрузки главной страницы")
            return []
        soup = BeautifulSoup(r.text, "html.parser")
        date_links = []
        for a in soup.select(".calendar a"):
            href = a.get("href", "")
            if "/matches/" in href:
                full = "https://www.oddsmath.com" + href
                date_links.append(full)
        return list(set(date_links))
    except Exception as e:
        log(f"Ошибка при загрузке дат: {e}")
        return []

# Получение матчей с одной даты
def fetch_match_links(date_url):
    try:
        r = requests.get(date_url, timeout=15)
        if r.status_code != 200:
            log(f"Ошибка загрузки {date_url}")
            return []
        soup = BeautifulSoup(r.text, "html.parser")
        links = []
        for a in soup.select(".event-table a"):
            href = a.get("href", "")
            if "/match/" in href:
                full = "https://www.oddsmath.com" + href
                links.append(full)
        return list(set(links))
    except Exception as e:
        log(f"Ошибка в дате {date_url}: {e}")
        return []

# Проверка одного матча
def check_match(url):
    if url in seen_urls or url in bad_urls:
        return
    seen_urls.add(url)
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return
        soup = BeautifulSoup(r.text, "html.parser")
        bet = soup.select_one("div.back div.value")
        if not bet:
            bad_urls.add(url)
            return
        value = bet.text.replace("€", "").replace(",", "").strip()
        if value.isdigit() and int(value) >= THRESHOLD:
            msg = f"💰 BACK: {value} €\n{url}"
            bot.send_message(chat_id=CHAT_ID, text=msg)
            log(f"Отправлено: {msg}")
    except Exception as e:
        log(f"Ошибка при проверке {url}: {e}")

# Основной цикл
if __name__ == "__main__":
    while True:
        date_pages = fetch_date_pages()
        log(f"Найдено дат: {len(date_pages)}")
        for date_url in date_pages:
            matches = fetch_match_links(date_url)
            log(f"Дата: {date_url} — матчей: {len(matches)}")
            for url in matches:
                check_match(url)
                time.sleep(1)
        time.sleep(1800)
