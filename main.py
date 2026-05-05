import discord
from discord.ext import commands
import asyncio
import os
from flask import Flask
from threading import Thread
from config import TOKEN, GC_INTERVAL
from utils import helpers
from controllers import commands as cmd_ctrl, events as evt_ctrl

app = Flask(__name__)

@app.route('/')
def home():
    return '🤖 Bot está online!'

@app.route('/health')
def health():
    return 'OK', 200

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def gc_task():
    while True:
        await asyncio.sleep(GC_INTERVAL)
        helpers.force_gc()

@bot.event
async def setup_hook():
    bot.tree.add_command(cmd_ctrl.Commands(bot))
    evt_ctrl.EventController(bot).setup()
    asyncio.create_task(gc_task())
    await bot.tree.sync()
    helpers.setup_logger().info("✅ Comandos sincronizados")

if __name__ == "__main__":
    logger = helpers.setup_logger()
    keep_alive()
    logger.info("🌐 Servidor web iniciado")
    
    try:
        bot.run(TOKEN)
    except discord.LoginFailure as e:
        logger.error(f"❌ Falha no login: Token inválido? {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Erro crítico na inicialização: {e}", exc_info=True)
        raise