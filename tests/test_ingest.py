"""Tests for the ingest pipeline: add, skip, re-run, and update."""

import os

import pytest
from PIL import Image

from insight.db import connect, init_schema
from insight.ingest import ingest


@pytest.fixture
def conn(tmp_path):
    """A fresh catalog database with the schema created."""
    conn = connect(tmp_path / "catalog.db")   
    init_schema(conn)
    yield conn                                # test runs here, then cleanup
    conn.close()                              


@pytest.fixture
def photo_dir(tmp_path):
    """A folder with two real images and one corrupt file."""
    folder = tmp_path / "photos"
    folder.mkdir()
    Image.new("RGB", (40, 30)).save(folder / "a.jpg")
    Image.new("RGB", (20, 10)).save(folder / "b.png")
    (folder / "broken.jpg").write_text("not an image")
    return folder


def count_rows(conn):
    return conn.execute("SELECT COUNT(*) FROM photos").fetchone()[0]


def test_first_run_adds_images_and_skips_corrupt(conn, photo_dir):
    stats = ingest(conn, photo_dir)
    assert (stats.added, stats.skipped) == (2, 1)
    assert count_rows(conn) == 2


def test_second_run_is_idempotent(conn, photo_dir):
    ingest(conn, photo_dir)
    stats = ingest(conn, photo_dir)
    assert (stats.unchanged, stats.added, stats.updated) == (2, 0, 0)
    assert count_rows(conn) == 2


def test_changed_file_is_updated(conn, photo_dir):
    ingest(conn, photo_dir)
    path = photo_dir / "a.jpg"
    Image.new("RGB", (80, 60)).save(path)   # replaces the 40x30 a.jpg
    os.utime(path, ns=(1, 1))               # force a different mtime
    stats = ingest(conn, photo_dir)
    assert stats.updated == 1
    row = conn.execute(
        "SELECT width FROM photos WHERE path = ?", (str(path.resolve()),)
    ).fetchone()
    assert row["width"] == 80
