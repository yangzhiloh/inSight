"""Discover image files on disk for ingestion."""

from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

def find_images(root: str | Path) -> list[Path]:
    """Return all JPEG and PNG files under root, recursively, sorted by path.

    Extensions are matched case-insensitively, so IMG_001.JPG is included.
    Raises NotADirectoryError if root is not a directory.
    """

    root = Path(root)
    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {root}")

    images = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            images.append(path)

    return sorted(images)


