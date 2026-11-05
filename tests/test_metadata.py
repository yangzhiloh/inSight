import hashlib

import pytest
from PIL import Image, UnidentifiedImageError

from insight.metadata import (
    DATETIME_ORIGINAL,
    EXIF_IFD,
    _parse_exif_datetime,
    read_image_info,
    sha256_file,
)


def make_image(path, size=(40, 30), taken_at=None):
    """Save a small JPEG, optionally with an EXIF capture time."""
    exif = Image.Exif()
    if taken_at is not None:
        exif.get_ifd(EXIF_IFD)[DATETIME_ORIGINAL] = taken_at
    Image.new("RGB", size).save(path, exif=exif)
    return path


def test_sha256_matches_hashlib(tmp_path):
    data = b"hello inSight"
    path = tmp_path / "file.bin"
    path.write_bytes(data)

    assert sha256_file(path) == hashlib.sha256(data).hexdigest()


def test_sha256_changes_when_content_changes(tmp_path):
    path = tmp_path / "file.bin"
    path.write_bytes(b"version 1")
    before = sha256_file(path)

    path.write_bytes(b"version 2")

    assert sha256_file(path) != before


def test_read_image_info_without_exif(tmp_path):
    path = make_image(tmp_path / "plain.jpg")

    assert read_image_info(path) == (40, 30, None)


def test_read_image_info_with_exif_date(tmp_path):
    path = make_image(tmp_path / "dated.jpg", taken_at="2024:05:01 14:30:00")

    assert read_image_info(path) == (40, 30, "2024-05-01T14:30:00")


def test_read_image_info_rejects_non_image(tmp_path):
    path = tmp_path / "fake.jpg"
    path.write_text("this is not an image")

    with pytest.raises(UnidentifiedImageError):
        read_image_info(path)


@pytest.mark.parametrize("raw", [None, "0000:00:00 00:00:00", "not a date", b"bytes"])
def test_parse_exif_datetime_returns_none_for_bad_input(raw):
    assert _parse_exif_datetime(raw) is None