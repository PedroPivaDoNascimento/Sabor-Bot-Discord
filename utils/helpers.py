import gc
import logging
import os
import re
import sys

logger = logging.getLogger("MusicBot")

def setup_logger():
    logging.basicConfig(
        level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
        format='%(asctime)s | %(levelname)s | %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger("MusicBot")

def force_gc():
    gc.collect()
    # Limpa cache interno do yt-dlp se existir
    try:
        import yt_dlp
        yt_dlp.cache.cleanup()
    except:
        pass

def validate_url(url: str) -> bool:
    pattern = re.compile(r'^(https?://)?(www\.)?(youtube\.com|youtu\.be|open\.spotify\.com|tidal\.com|soundcloud\.com)/')
    return bool(pattern.match(url.strip()))

def format_time(seconds: int) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m}:{s:02d}"