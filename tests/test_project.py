import json
import os

from pathlib import Path, PurePath

from contextlib import contextmanager
from tempfile import TemporaryDirectory

from config import Config
from transpose import version
from transpose.utils import check_path, create_cache, get_cache, move, remove, symlink


TARGET_DIR = "source"
STORE_DIR = "destination"
SYMLINK_DIR = "symlink_test"

CACHE_FILE_CONTENTS = {"version": version, "original_path": TARGET_DIR}

config = Config()


@contextmanager
def setup():
    old_dir = os.getcwd()
    with TemporaryDirectory("tests-temp") as td:
        try:
            os.chdir(td)

            os.mkdir(TARGET_DIR)
            os.mkdir(STORE_DIR)
            os.symlink(TARGET_DIR, SYMLINK_DIR)

            cache_path = Path(PurePath(TARGET_DIR, config.cache_filename))
            with open(str(cache_path), "w") as f:
                json.dump(CACHE_FILE_CONTENTS, f)
            yield
        finally:
            os.chdir(old_dir)


@setup()
def test_check_path():
    existing_dir = Path(TARGET_DIR)
    nonexisting_dir = Path("nonexistent")
    symlink_dir = Path(SYMLINK_DIR)

    cache_path = Path(PurePath(TARGET_DIR, config.cache_filename))

    assert check_path(existing_dir) is True
    assert check_path(nonexisting_dir) is False
    assert check_path(symlink_dir, is_symlink=True) is True
    assert check_path(cache_path) is False


@setup()
def test_cache_create():
    cache_file = "test_cache_file.json"

    cache_path = Path(PurePath(TARGET_DIR, cache_file))
    original_path = Path("/tmp/some/random/path")

    create_cache(cache_path=cache_path, original_path=original_path)

    cache = json.load(open(cache_path, "r"))

    assert cache_path.exists()
    assert cache["original_path"] == str(original_path)
    assert cache["version"] == version


@setup()
def test_cache_get():
    cache_path = Path(PurePath(TARGET_DIR, config.cache_filename))
    cache = get_cache(cache_path)

    assert cache["version"] == CACHE_FILE_CONTENTS["version"]
    assert cache["original_path"] == CACHE_FILE_CONTENTS["original_path"]


@setup()
def test_file_move():
    source_path = Path(TARGET_DIR)
    destination_path = Path(STORE_DIR)

    move(source=source_path.absolute(), destination=destination_path.absolute())
    assert not source_path.exists()
    assert destination_path.exists()


@setup()
def test_file_remove():
    cache_path = Path(PurePath(TARGET_DIR, config.cache_filename))
    symlink_filepath = Path(PurePath(TARGET_DIR, SYMLINK_DIR))
    target_filepath = Path(TARGET_DIR)

    remove(path=cache_path)
    remove(path=symlink_filepath)
    remove(path=target_filepath)

    assert not cache_path.exists()  # Should be able to remove files
    assert not symlink_filepath.exists()  # Should be able to remove symlinks
    assert target_filepath.exists()  # Should not be able to remove directories


@setup()
def test_file_symlink():
    symlink_name = "test_link"
    symlink_filepath = Path(symlink_name)
    target_filepath = Path(TARGET_DIR)

    symlink(target_path=target_filepath, symlink_path=symlink_filepath)

    assert target_filepath.exists()
    assert symlink_filepath.is_symlink()
    assert symlink_filepath.readlink() == target_filepath
