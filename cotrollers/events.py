import discord
import logging
from discord.ext import commands
import discord.app_commands as app_commands
from utils import helpers

logger = helpers.setup_logger()

class EventController:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def setup(self):
        @self.bot.event
        async def on_ready():
            logger.info(f"✅ {self.bot.user} online. Latência: {self.bot.latency*1000:.2f}ms")
            self.bot.voice_client = None
            self.bot.is_playing = False

        @self.bot.tree.error
        async def on_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
            logger.error(f"Erro comando: {error}")
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Erro: {str(error)}", ephemeral=True)
            helpers.force_gc()

        @self.bot.event
        async def on_voice_state_update(member, before, after):
            # Auto-desconecta se o canal ficar vazio
            if after.channel is None and self.bot.voice_client:
                if len(before.channel.members) == 1:
                    await self.bot.voice_client.disconnect()
                    self.bot.voice_client = None
                    self.bot.is_playing = False
                    logger.info("🔇 Canal vazio. Desconectado.")