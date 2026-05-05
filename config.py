import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ ERRO CRÍTICO: DISCORD_TOKEN não encontrado nas variáveis de ambiente!")
    print("💡 Vá em Settings → Environment Variables no Render e adicione DISCORD_TOKEN")
    raise ValueError("DISCORD_TOKEN ausente")

DB_PATH = os.getenv("DB_PATH", "data/bot.db")
MAX_QUEUE_SIZE = 50
GC_INTERVAL = 180
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")