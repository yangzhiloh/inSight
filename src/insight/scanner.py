"""Discover image files on disk for ingestion."""

from pathlib import Path

def find_images(root: str | Path):
    """Return all JPEG and PNG files under root, recursively, sorted by path.

    Extensions are matched case-insensitively, so IMG_001.JPG is included.
    """

