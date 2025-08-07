import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import telegram

# === Настройки ===
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
THRESHOLD = 20  # 💰 Порог ставки в евро

bot = telegram.Bot(token=TOKEN)

# === Логирование ===
def log(message):
    now = datetime.now().strftime("[%H:%M:%S]")
    print(f"{now} {message}")

# === Получение HTML по ссылке ===
def fetch_html(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        log(f"Ошибка загрузки {url}: {e}")
        return None

# === Проверка страницы матча ===
def check_match(match_url):
    html = fetch_html(match_url)
    if not html:
        return

    soup = BeautifulSoup(html, "html.parser")

    markets = soup.select("tr[onclick]")
    for market in markets:
        onclick = market.get("onclick", "")
        if "back" not in onclick.lower():
            continue

        cells = market.find_all("td")
        if len(cells) < 5:
            continue

        try:
            amount_str = cells[-1].text.strip().replace("€", "").replace(",", "").split(".")[0]
            amount = int(amount_str)
        except Exception:
            continue

        if amount >= THRESHOLD:
            message = f"💸 Найдена ставка {amount}€\n🔗 {match_url}"
            bot.send_message(chat_id=CHAT_ID, text=message)
            log(f"Отправлено уведомление: {amount}€ — {match_url}")
            break

# === Главный цикл ===
if __name__ == "__main__":
    while True:
        date_str = datetime.now().strftime("%Y-%m-%d")
        url = f"https://www.oddsmath.com/football/matches/{date_str}/"
        html = fetch_html(url)

        if not html:
            time.sleep(1800)
            continue

        soup = BeautifulSoup(html, "html.parser")
        links = [
            "https://www.oddsmath.com" + a["href"]
            for a in soup.select("a[href^='/football/match/']")
        ]
        unique_links = list(set(links))

        log(f"Найдено матчей: {len(unique_links)}")

        for link in unique_links:
            check_match(link)
            time.sleep(1)

        time.sleep(1800)  # Проверка каждые 30 минут
