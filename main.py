import os
from dotenv import load_dotenv

load_dotenv()

print("TOKEN:", os.getenv("TOKEN"))
print("CHAT_ID:", os.getenv("CHAT_ID"))
