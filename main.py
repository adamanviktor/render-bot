import os
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telegram import Bot

# Загрузка переменных из .env
load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
THRESHOLD = 20  # Минимальная сумма ставки BACK

bot = Bot(token=TOKEN)

URL_BASE = "https://www.oddsmath.com/matches"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def send_message(chat_id, text):
    try:
        bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        log(f"Ошибка при отправке: {e}")

def fetch_match_links(date_str):
    url = f"{URL_BASE}/{date_str}/"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            log(f"Ошибка загрузки {url}")
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        match_links = soup.select(".event-table tr a[href]")
        return ["https://www.oddsmath.com" + link['href'] for link in match_links]
    except Exception as e:
        log(f"Ошибка: {e}")
        return []

def check_match(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return
        soup = BeautifulSoup(resp.text, "html.parser")
        rows = soup.select("table tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 5:
                continue
            for cell in cells:
                text = cell.get_text(strip=True).replace("€", "").replace(",", ".")
                if text.replace(".", "").isdigit():
                    value = float(text)
                    if value >= THRESHOLD:
                        log(f"Найдена ставка {value}€: {url}")
                        send_message(CHAT_ID, f"💰 Ставка BACK: {value}€\n{url}")
                        return  # достаточно первой
    except Exception as e:
        log(f"Ошибка матча: {e}")

def main():
    date_str = datetime.now().strftime("%Y-%m-%d")
    links = fetch_match_links(date_str)
    if not links:
        log("Матчей не найдено.")
        return
    log(f"Найдено матчей: {len(links)}")
    for url in links:
        check_match(url)
        time.sleep(1)

if __name__ == "__main__":
    main()
