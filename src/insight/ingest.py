"""Ingest a folder of photos into the SQLite catalog."""

import logging
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

from insight.metadata import read_image_info, sha256_file
from insight.scanner import find_images

log = logging.getLogger(__name__)

UPSERT = """
INSERT INTO photos (path, size_bytes, mtime_ns, sha256, width, height, taken_at, indexed_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(path) DO UPDATE SET
    size_bytes = excluded.size_bytes,
    mtime_ns   = excluded.mtime_ns,
    sha256     = excluded.sha256,
    width      = excluded.width,
    height     = excluded.height,
    taken_at   = excluded.taken_at,
    indexed_at = excluded.indexed_at
"""


@dataclass
class IngestStats:
    """Counts of what happened during one ingest run."""

    added: int = 0
    updated: int = 0
    unchanged: int = 0
    skipped: int = 0


def ingest(conn: sqlite3.Connection, root: str | Path) -> IngestStats:
    """Scan root for images and add new or changed ones to the catalog.

    Unchanged files (same size and mtime) are not re-hashed.
    Unreadable files are logged and skipped. Safe to run repeatedly.
    """
    stats = IngestStats()
    now = int(time.time())
    with conn:
        for path in find_images(root):
            key = str(path.resolve())
            st = path.stat()
            row = conn.execute(
                "SELECT size_bytes, mtime_ns FROM photos WHERE path = ?", (key,)
            ).fetchone()

            if (
                row is not None
                and row["size_bytes"] == st.st_size
                and row["mtime_ns"] == st.st_mtime_ns
            ):
                conn.execute(
                    "UPDATE photos SET indexed_at = ? WHERE path = ?", (now, key)
                )
                stats.unchanged += 1
                continue

            try:
                digest = sha256_file(path)
                width, height, taken_at = read_image_info(path)
            except OSError as e:
                log.warning("Skipping %s: %s", path, e)
                stats.skipped += 1
                continue

            conn.execute(
                UPSERT,
                (key, st.st_size, st.st_mtime_ns, digest, width, height, taken_at, now),
            )
            if row is None:
                stats.added += 1
            else:
                stats.updated += 1
    return stats