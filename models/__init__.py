import sqlite3
import json
import os
from collections import deque
from dataclasses import dataclass
from typing import List, Optional
from config import DB_PATH, MAX_QUEUE_SIZE

@dataclass
class Track:
    title: str
    url: str
    duration: int
    requester: str

class _Database:
    def __init__(self, path: str):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        # Otimizações SQLite para baixo consumo
        self.conn.execute("PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL; PRAGMA cache_size=-2000;")
        self._init_db()

    def _init_db(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS playlists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    tracks_json TEXT NOT NULL
                )
            """)

    def save_playlist(self, user_id: int, name: str, tracks: List[dict]):
        with self.conn:
            self.conn.execute(
                "INSERT INTO playlists (user_id, name, tracks_json) VALUES (?, ?, ?)",
                (user_id, name, json.dumps(tracks, ensure_ascii=False))
            )

    def get_user_playlists(self, user_id: int) -> List[tuple]:
        return self.conn.execute("SELECT id, name FROM playlists WHERE user_id = ?", (user_id,)).fetchall()

    def get_playlist_tracks(self, playlist_id: int) -> List[dict]:
        row = self.conn.execute("SELECT tracks_json FROM playlists WHERE id = ?", (playlist_id,)).fetchone()
        return json.loads(row[0]) if row else []

    def remove_track_from_playlist(self, playlist_id: int, track_index: int) -> bool:
        tracks = self.get_playlist_tracks(playlist_id)
        if 0 <= track_index < len(tracks):
            tracks.pop(track_index)
            with self.conn:
                self.conn.execute("UPDATE playlists SET tracks_json = ? WHERE id = ?", (json.dumps(tracks, ensure_ascii=False), playlist_id))
            return True
        return False

    def close(self):
        self.conn.close()

class _Queue:
    def __init__(self, maxsize: int = MAX_QUEUE_SIZE):
        self.queue = deque(maxlen=maxsize)
        self.current: Optional[Track] = None

    def add(self, track: Track):
        self.queue.append(track)

    def get_next(self) -> Optional[Track]:
        return self.queue.popleft() if self.queue else None

    def save_to_db(self, user_id: int, name: str, db: _Database):
        tracks = []
        if self.current:
            tracks.append(self.current.__dict__)
        tracks.extend([t.__dict__ for t in self.queue])
        if not tracks:
            raise ValueError("Fila vazia")
        db.save_playlist(user_id, name, tracks)

    def clear(self):
        self.queue.clear()
        self.current = None

db = _Database(DB_PATH)
queue = _Queue()