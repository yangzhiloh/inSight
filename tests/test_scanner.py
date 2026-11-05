import pytest

from insight.scanner import find_images


@pytest.fixture
def photo_dir(tmp_path):
    """A small folder tree with images, non-images, and a tricky folder name."""
    (tmp_path / "beach.jpg").touch()
    (tmp_path / "IMG_0001.JPG").touch()
    (tmp_path / "notes.txt").touch()
    (tmp_path / "fake.jpg").mkdir()

    trip = tmp_path / "trips" / "japan"
    trip.mkdir(parents=True)
    (trip / "temple.jpeg").touch()
    (trip / "map.png").touch()
    return tmp_path


def test_finds_images_recursively_and_case_insensitively(photo_dir):
    images = find_images(photo_dir)

    assert images == sorted([
        photo_dir / "beach.jpg",
        photo_dir / "IMG_0001.JPG",
        photo_dir / "trips" / "japan" / "temple.jpeg",
        photo_dir / "trips" / "japan" / "map.png",
    ])


def test_ignores_non_images_and_folders(photo_dir):
    images = find_images(photo_dir)

    assert photo_dir / "notes.txt" not in images
    assert photo_dir / "fake.jpg" not in images


def test_accepts_string_path(photo_dir):
    assert find_images(str(photo_dir)) == find_images(photo_dir)


def test_empty_directory_returns_empty_list(tmp_path):
    assert find_images(tmp_path) == []


def test_missing_directory_raises(tmp_path):
    with pytest.raises(NotADirectoryError):
        find_images(tmp_path / "does_not_exist")