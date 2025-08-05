import time
import requests
from bs4 import BeautifulSoup
import re
import logging
import os

import telegram

TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

bot = telegram.Bot(token=TOKEN)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

BASE_URL = "https://oddsmath.com"
START_URL = BASE_URL + "/"


def get_first_event_page():
    r = requests.get(START_URL, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    link = soup.select_one(".menu_events_by_date a")
    if link:
        return BASE_URL + link.get("href")
    return None


def get_all_match_links(event_url):
    r = requests.get(event_url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.select("a.event-name")
    return [BASE_URL + l.get("href") for l in links]


def find_big_back_bets(match_url):
    r = requests.get(match_url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    alerts = []
    for row in soup.select(".odd_block_line"):
        if "BACK" in row.text.upper():
            stake_tag = row.select_one(".stake")
            if stake_tag:
                stake_text = stake_tag.text.strip()
                stake_num = re.sub(r"[^0-9]", "", stake_text)
                if stake_num and int(stake_num) >= 100:
                    alerts.append(f"{match_url}\n{row.text.strip()}")
    return alerts


def main():
    sent = set()
    while True:
        try:
            event_url = get_first_event_page()
            if not event_url:
                time.sleep(60)
                continue
            matches = get_all_match_links(event_url)
            for url in matches:
                alerts = find_big_back_bets(url)
                for a in alerts:
                    if a not in sent:
                        bot.send_message(chat_id=CHAT_ID, text=a)
                        sent.add(a)
                time.sleep(2)
        except Exception as e:
            logging.exception("Error in main loop")
        time.sleep(120)


if __name__ == "__main__":
    main()
