import telegram
import time

# Данные с твоих скриншотов
TOKEN = '8392536867:AAFRsDEeM7zfV_t3sbvGHLkC4ZDUHGUujrg'
CHAT_ID = 6328751132  # @Adamian_Viktor

bot = telegram.Bot(token=TOKEN)

def send_message():
    try:
        bot.send_message(chat_id=CHAT_ID, text="🔔 Бот запущен и работает!")
        print("✅ Сообщение отправлено.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    send_message()
    while True:
        time.sleep(60)
