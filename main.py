import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from dotenv import load_dotenv

# Загружаем токен и chat_id из .env
load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TOKEN)

# Страница со списком матчей на день
MAIN_URL = "https://www.oddsmath.com/football/matches/2025-08-07/"

# Заголовки для обхода блокировки
HEADERS = {
    "Host": "www.oddsmath.com",
    "Connection": "Keep-Alive",
    "User-Agent": "Mozilla/5.0",
    "X-Online-Host": "www.oddsmath.com"
}

def extract_match_links():
    try:
        response = requests.get(MAIN_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[Ошибка] Не удалось загрузить список матчей: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/football/match/") and "odds" not in href:
            full_url = "https://www.oddsmath.com" + href
            if full_url not in links:
                links.append(full_url)

    return links

def check_stakes(link):
    try:
        response = requests.get(link, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[Ошибка] {link}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Ищем большие BACK ставки
    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 4:
            continue
        try:
            stake_text = cells[3].text.strip().replace(",", "").replace("€", "")
            if stake_text and float(stake_text) >= 20_000:
                return stake_text
        except:
            continue
    return None

def main():
    links = extract_match_links()
    print(f"Найдено матчей: {len(links)}")

    for link in links:
        stake = check_stakes(link)
        if stake:
            text = f"🔔 Найдена ставка BACK: {stake} €\n{link}"
            print(text)
            try:
                bot.send_message(chat_id=CHAT_ID, text=text)
            except Exception as e:
                print(f"[Ошибка Telegram] {e}")

if __name__ == "__main__":
    main()
