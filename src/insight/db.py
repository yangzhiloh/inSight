import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS photos (
    id          INTEGER PRIMARY KEY,
    path        TEXT    NOT NULL UNIQUE,
    size_bytes  INTEGER NOT NULL,
    mtime_ns    INTEGER NOT NULL,
    sha256      TEXT    NOT NULL,
    width       INTEGER NOT NULL,
    height      INTEGER NOT NULL,
    taken_at    TEXT,
    indexed_at  INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_photos_sha256 ON photos (sha256);
"""


def connect(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    with conn:
        conn.executescript(SCHEMA)