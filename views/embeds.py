import discord
from models import queue
from utils import helpers

def help_embed() -> discord.Embed:
    emb = discord.Embed(title="🎵 Comandos Disponíveis", color=0x00ff88)
    emb.description = (
        "```diff\n"
        "+ /ping\n"
        "+ /ajuda\n"
        "+ /play <link>\n"
        "+ /save_queue <nome>\n"
        "+ /playlist lista\n"
        "+ /playlist remove <id> <index>\n"
        "+ /export <id>\n```"
    )
    emb.set_footer(text="MVC | Otimizado para 100MB RAM")
    return emb

def queue_status_embed() -> discord.Embed:
    emb = discord.Embed(title="🎧 Status da Fila", color=0x3498db)
    curr = queue.current
    if curr:
        emb.add_field(name="Tocando", value=f"[{curr.title}]({curr.url}) ({helpers.format_time(curr.duration)})")
    
    q = queue.queue
    if q:
        lines = [f"{i+1}. {t.title}" for i, t in enumerate(q[:5])]
        emb.add_field(name=f"Próximas ({len(q)})", value="\n".join(lines), inline=False)
    else:
        emb.add_field(name="Fila", value="Vazia")
    return emb

def playlist_list_embed(playlists: list) -> discord.Embed:
    emb = discord.Embed(title="📚 Suas Playlists", color=0xf39c12)
    emb.description = "\n".join([f"`{pid}` • {name}" for pid, name in playlists]) if playlists else "Nenhuma playlist salva."
    return emb

def export_content(tracks: list) -> str:
    return "\n".join([f"{t['url']} | {t['title']}" for t in tracks])