"""Read file hashes and image metadata for the photo catalog."""

import hashlib
from datetime import datetime
from pathlib import Path

from PIL import Image

EXIF_IFD = 0x8769
DATETIME_ORIGINAL = 36867


def sha256_file(path: str | Path) -> str:
    """Return the SHA-256 of a file's contents as a 64-character hex string.

    Streams the file, so memory use is constant regardless of file size.
    """
    with open(path, "rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def read_image_info(path: str | Path) -> tuple[int, int, str | None]:
    """Return (width, height, taken_at) for an image file.

    taken_at is the EXIF capture time in ISO 8601 (e.g. "2024-05-01T14:30:00"),
    or None if the image has no valid capture time.
    Raises PIL.UnidentifiedImageError if the file is not a readable image.
    """
    with Image.open(path) as img:
        width, height = img.size
        raw = img.getexif().get_ifd(EXIF_IFD).get(DATETIME_ORIGINAL)
        return width, height, _parse_exif_datetime(raw)


def _parse_exif_datetime(raw: str | None) -> str | None:
    """Convert an EXIF date like "2024:05:01 14:30:00" to ISO 8601.

    Returns None if raw is missing or malformed.
    """
    if raw is None:
        return None

    try:
        return datetime.strptime(raw, "%Y:%m:%d %H:%M:%S").isoformat()
    except (ValueError, TypeError):
        return None