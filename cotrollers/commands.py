import discord
import asyncio
import io
import yt_dlp
from discord.ext import commands
import discord.app_commands as app_commands
from models import queue, db, Track
from views import embeds as v
from utils import helpers

# yt-dlp otimizado: sem download, timeout baixo, sem cache pesado
ytdl = yt_dlp.YoutubeDL({
    'quiet': True, 'no_warnings': True, 'skip_download': True,
    'socket_timeout': 10, 'default_search': 'ytsearch',
    'no_overwrites': True, 'playlist_items': '1:50'
})

class Commands(app_commands.Group):
    def __init__(self, bot: commands.Bot):
        super().__init__(name="music", description="Controle de música")
        self.bot = bot

    @app_commands.command(name="ping", description="Verifica latência")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🏓 Pong! `{self.bot.latency*1000:.2f}ms`")

    @app_commands.command(name="ajuda", description="Mostra comandos")
    async def ajuda(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=v.help_embed())

    @app_commands.command(name="play", description="Adiciona link à fila")
    async def play(self, interaction: discord.Interaction, link: str):
        if not helpers.validate_url(link):
            return await interaction.response.send_message("❌ Link inválido.", ephemeral=True)
        
        await interaction.response.defer()
        try:
            info = ytdl.extract_info(link, download=False)
            entries = info.get('entries', [info]) if 'entries' in info else [info]
            
            added = 0
            for e in entries:
                if not e: continue
                url = e.get('url') or f"https://youtu.be/{e['id']}"
                queue.add(Track(
                    title=e.get('title', 'Desconhecida'),
                    url=url,
                    duration=int(e.get('duration', 0)),
                    requester=interaction.user.name
                ))
                added += 1

            await interaction.followup.send(f"✅ `{added}` faixa(s) adicionada(s) à fila.")
            
            if not self.bot.voice_client:
                if interaction.user.voice:
                    self.bot.voice_client = await interaction.user.voice.channel.connect()
                else:
                    return await interaction.followup.send("❌ Entre em um canal de voz primeiro.", ephemeral=True)
            
            if not self.bot.is_playing:
                asyncio.create_task(self._play_loop())
                
        except Exception as ex:
            await interaction.followup.send(f"❌ Erro ao processar: {ex}")
            helpers.force_gc()

    @app_commands.command(name="save_queue", description="Salva fila atual como playlist")
    async def save_queue(self, interaction: discord.Interaction, nome: str):
        try:
            queue.save_to_db(interaction.user.id, nome, db)
            await interaction.response.send_message(f"✅ Fila salva como `{nome}`.")
            helpers.force_gc()
        except Exception as e:
            await interaction.response.send_message(f"❌ {e}", ephemeral=True)

    @app_commands.command(name="playlist", description="Gerenciar playlists")
    @app_commands.choices(action=[app_commands.Choice(name="lista", value="lista"), app_commands.Choice(name="remove", value="remove")])
    async def playlist(self, interaction: discord.Interaction, action: app_commands.Choice, playlist_id: int = None, indice: int = None):
        if action.value == "lista":
            res = db.get_user_playlists(interaction.user.id)
            await interaction.response.send_message(embed=v.playlist_list_embed(res))
        elif action.value == "remove":
            if playlist_id is None or indice is None:
                return await interaction.response.send_message("❌ Uso: `/playlist remove playlist_id <ID> indice <NÚMERO>`", ephemeral=True)
            ok = db.remove_track_from_playlist(playlist_id, indice)
            await interaction.response.send_message("✅ Música removida." if ok else "❌ Índice ou ID inválido.")

    @app_commands.command(name="export", description="Exporta playlist em .txt")
    async def export(self, interaction: discord.Interaction, playlist_id: int):
        tracks = db.get_playlist_tracks(playlist_id)
        if not tracks:
            return await interaction.response.send_message("❌ Playlist vazia ou inexistente.", ephemeral=True)
        
        txt = v.export_content(tracks)
        f = discord.File(io.BytesIO(txt.encode("utf-8")), filename=f"playlist_{playlist_id}.txt")
        await interaction.response.send_message("📥 Playlist exportada:", file=f)
        helpers.force_gc()

    async def _play_loop(self):
        while True:
            if not self.bot.voice_client or not self.bot.voice_client.is_connected():
                self.bot.is_playing = False
                break
                
            if not self.bot.voice_client.is_playing():
                nxt = queue.get_next()
                if nxt:
                    queue.current = nxt
                    self.bot.is_playing = True
                    # before_options otimiza reconexão e uso de CPU
                    source = discord.FFmpegPCMAudio(nxt.url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")
                    self.bot.voice_client.play(source, after=lambda e: self._after_play())
                else:
                    self.bot.is_playing = False
                    queue.clear()
                    break
            await asyncio.sleep(2)
            helpers.force_gc()

    def _after_play(self):
        queue.current = None
        self.bot.loop.create_task(self._play_loop())