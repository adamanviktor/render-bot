import requests
from bs4 import BeautifulSoup
import telegram
import time
from datetime import datetime
import pytz

# === Настройки ===
TOKEN = "ВСТАВЬ_СВОЙ_ТОКЕН"
CHAT_ID = 6328751132
BASE_URL = "https://www.oddsmath.com"
HEADERS = {"User-Agent": "Mozilla/5.0"}
MIN_BACK_BET = 100  # Тестовая сумма

bot = telegram.Bot(token=TOKEN)

def get_today_url():
    berlin = pytz.timezone('Europe/Berlin')
    today = datetime.now(berlin).strftime("%Y-%m-%d")
    r = requests.get(f"{BASE_URL}/football/matches/today/", headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    for a in soup.select("ul.list-dates a"):
        if today in a.get("href", ""):
            return BASE_URL + a["href"]
    return None

def get_match_links(day_url):
    r = requests.get(day_url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    links = []
    for a in soup.select("a[href^='/football/']"):
        href = a["href"]
        if href.count("/") > 3 and "vs" in href and href not in links:
            links.append(BASE_URL + href)
    return links

def check_match_for_big_back(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup.find_all(string=lambda text: "Back" in text or "BACK" in text):
            parent = tag.find_parent("tr")
            if parent and "€" in parent.text:
                parts = parent.get_text().replace("€", "").replace(",", "").split()
                for part in parts:
                    if part.isdigit() and int(part) >= MIN_BACK_BET:
                        return f"💰 {url}\nНайдена ставка: {part} €"
    except Exception as e:
        print("Ошибка:", e)
    return None

def main():
    print("▶️ Старт сканирования...")
    sent = set()
    while True:
        day_url = get_today_url()
        if not day_url:
            print("❌ Не найдена ссылка на сегодняшнюю дату")
            time.sleep(300)
            continue
        matches = get_match_links(day_url)
        print(f"🔍 Найдено матчей: {len(matches)}")
        for match_url in matches:
            if match_url in sent:
                continue
            alert = check_match_for_big_back(match_url)
            if alert:
                bot.send_message(chat_id=CHAT_ID, text=alert)
                sent.add(match_url)
        time.sleep(600)  # Повторять каждые 10 мин

if __name__ == "__main__":
    main()
