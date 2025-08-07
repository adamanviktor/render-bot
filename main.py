import os
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telegram import Bot

# === НАСТРОЙКИ ===
load_dotenv()
TOKEN = os.getenv("TOKEN")              # Telegram Bot Token
CHAT_ID = os.getenv("CHAT_ID")          # Telegram Chat ID
MATCH_LIST_URL = os.getenv("MATCH_LIST_URL")  # Ссылка на страницу с матчами
THRESHOLD = int(os.getenv("THRESHOLD", 20))   # Минимальная ставка (евро)

# === ТЕЛЕГРАМ-БОТ ===
bot = Bot(token=TOKEN)

# === HTTP HEADERS ===
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# === ЛОГ ===
def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# === ОТПРАВКА СООБЩЕНИЯ ===
def send_message(chat_id, text):
    try:
        bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        log(f"Ошибка отправки: {e}")

# === ЗАГРУЗКА СПИСКА МАТЧЕЙ ===
def fetch_match_links():
    try:
        response = requests.get(MATCH_LIST_URL, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            log(f"Ошибка загрузки {MATCH_LIST_URL}")
            return []
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.select(".event-table tr a[href]")
        full_links = ["https://www.oddsmath.com" + link['href'] for link in links]
        return full_links
    except Exception as e:
        log(f"Ошибка: {e}")
        return []

# === ПРОВЕРКА ОТДЕЛЬНОГО МАТЧА ===
def check_match(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return
        soup = BeautifulSoup(resp.text, "html.parser")
        for row in soup.select("table tr"):
            cols = row.find_all("td")
            if len(cols) >= 7:
                try:
                    back_value = float(cols[6].get_text().replace("€", "").strip())
                    if back_value >= THRESHOLD:
                        send_message(CHAT_ID, f"Найдена ставка: {back_value}€\n{url}")
                        break
                except:
                    continue
    except:
        pass

# === ОСНОВНАЯ ФУНКЦИЯ ===
def main():
    log("Сканирование...")
    links = fetch_match_links()
    log(f"Найдено матчей: {len(links)}")
    for link in links:
        check_match(link)

if __name__ == "__main__":
    main()
