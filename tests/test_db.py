import sqlite3

import pytest

from insight.db import connect, init_schema

def test_init_schema_creates_photos_table(tmp_path):
    conn = connect(tmp_path / "catalog.db")

    init_schema(conn)

    init_schema(conn) # Second call must not fail

    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'photos'"
    ).fetchone()
    assert row is not None
    conn.close()

INSERT = """
INSERT INTO photos (path, size_bytes, mtime_ns, sha256, width, height, indexed_at)
VALUES (?, ?, ?, ?, ?, ?, ?)
"""

def test_path_must_be_unique(tmp_path):
    conn = connect(tmp_path / "catalog.db")
    init_schema(conn)
    row = ("C:/photos/cat.jpg", 1000, 1, "abc123", 640, 480, 0)

    conn.execute(INSERT, row)

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(INSERT, row)
    conn.close()