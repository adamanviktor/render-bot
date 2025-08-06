import os
import time
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
THRESHOLD = int(os.getenv("THRESHOLD", "20"))

bot = Bot(token=TOKEN)
seen = set()

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def check_given_url(url):
    try:
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            log(f"Ошибка загрузки: {url} → {r.status_code}")
            return []

        soup = BeautifulSoup(r.text, "html.parser")
        match_links = []
        for a in soup.select("a"):
            href = a.get("href", "")
            if "/football/" in href and href not in seen:
                full = href if href.startswith("http") else "https://www.oddsmath.com" + href
                match_links.append(full)
                seen.add(href)
        return match_links
    except Exception as e:
        log(f"Ошибка разбора страницы {url}: {e}")
        return []

def check_back(url):
    try:
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return
        soup = BeautifulSoup(r.text, "html.parser")
        back = soup.select_one("div.back div.value")
        if back:
            val = back.text.replace("€","").replace(",","").strip()
            if val.isdigit() and int(val) >= THRESHOLD:
                msg = f"Найдена BACK‑ставка: {val} €\n{url}"
                bot.send_message(chat_id=CHAT_ID, text=msg)
                log(f"Уведомил: {msg}")
    except Exception as e:
        log(f"Ошибка в ссылке {url}: {e}")

if __name__ == "__main__":
    url = "https://www.oddsmath.com/football/matches/2025-08-07/"
    log(f"Запускаем бот. Проверяем: {url}")
    links = check_given_url(url)
    log(f"Найдено ссылок: {len(links)}")
    for link in links:
        log(f"Проверяем: {link}")
        check_back(link)
        time.sleep(1)
    log("Готово.")
