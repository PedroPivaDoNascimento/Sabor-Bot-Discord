import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_TOKEN não encontrado. Configure o .env")

DB_PATH = os.getenv("DB_PATH", "data/bot.db")
MAX_QUEUE_SIZE = 50
GC_INTERVAL = 180  # Segundos entre garbage collections
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")