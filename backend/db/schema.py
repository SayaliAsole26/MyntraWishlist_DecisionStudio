"""Shared schema helper for offline jobs."""

from pathlib import Path

import sqlite3

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()
