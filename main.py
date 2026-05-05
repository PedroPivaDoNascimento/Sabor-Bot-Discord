import discord
from discord.ext import commands
import asyncio
from config import TOKEN, GC_INTERVAL
from utils import helpers
from controllers import commands as cmd_ctrl, events as evt_ctrl

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
    helpers.setup_logger().info("✅ Comandos sincronizados e bot inicializado.")

if __name__ == "__main__":
    helpers.setup_logger()
    bot.run(TOKEN)