"""SQLite connection helper."""

import sqlite3
from pathlib import Path

from backend.config import BACKEND_DIR, DATABASE_PATH

DB_PATH = Path(DATABASE_PATH) if DATABASE_PATH else BACKEND_DIR / "app.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
