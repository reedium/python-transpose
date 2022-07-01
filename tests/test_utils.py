import json

from pathlib import Path

from transpose import version, DEFAULT_CACHE_FILENAME
from transpose.utils import check_path, create_cache, get_cache, move, remove, symlink


from .utils import CACHE_FILE_CONTENTS, STORE_DIR, SYMLINK_DIR, TARGET_DIR, setup_env


@setup_env()
def test_check_path():
    existing_dir = Path(TARGET_DIR)
    nonexisting_dir = Path("nonexistent")
    symlink_dir = Path(SYMLINK_DIR)

    cache_path = Path(TARGET_DIR).joinpath(DEFAULT_CACHE_FILENAME)

    assert check_path(existing_dir) is True
    assert check_path(nonexisting_dir) is False
    assert check_path(symlink_dir, is_symlink=True) is True
    assert check_path(cache_path) is False


@setup_env()
def test_cache_create():
    cache_file = "test_cache_file.json"

    cache_path = Path(TARGET_DIR).joinpath(cache_file)
    original_path = Path("/tmp/some/random/path")

    create_cache(cache_path=cache_path, original_path=original_path)

    cache = json.load(open(cache_path, "r"))

    assert cache_path.exists()
    assert cache["original_path"] == str(original_path)
    assert cache["version"] == version


@setup_env()
def test_cache_get():
    cache_path = Path(TARGET_DIR).joinpath(DEFAULT_CACHE_FILENAME)
    cache = get_cache(cache_path)

    assert cache["version"] == CACHE_FILE_CONTENTS["version"]
    assert cache["original_path"] == CACHE_FILE_CONTENTS["original_path"]


@setup_env()
def test_file_move():
    source_path = Path(TARGET_DIR)
    destination_path = Path(STORE_DIR)

    move(source=source_path.absolute(), destination=destination_path.absolute())
    assert not source_path.exists()
    assert destination_path.exists()


@setup_env()
def test_file_remove():
    cache_path = Path(TARGET_DIR).joinpath(DEFAULT_CACHE_FILENAME)
    symlink_filepath = Path(TARGET_DIR).joinpath(SYMLINK_DIR)
    target_filepath = Path(TARGET_DIR)

    remove(path=cache_path)
    remove(path=symlink_filepath)
    remove(path=target_filepath)

    assert not cache_path.exists()  # Should be able to remove files
    assert not symlink_filepath.exists()  # Should be able to remove symlinks
    assert target_filepath.exists()  # Should not be able to remove directories


@setup_env()
def test_file_symlink():
    symlink_name = "test_link"
    symlink_filepath = Path(symlink_name)
    target_filepath = Path(TARGET_DIR)

    symlink(target_path=target_filepath, symlink_path=symlink_filepath)

    assert target_filepath.exists()
    assert symlink_filepath.is_symlink()
    assert symlink_filepath.readlink() == target_filepath
