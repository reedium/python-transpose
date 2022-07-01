import json
import os
import pytest

from pathlib import Path

from contextlib import contextmanager
from tempfile import TemporaryDirectory

from transpose import Transpose, version, DEFAULT_CACHE_FILENAME
from transpose.exceptions import TransposeError
from transpose.utils import check_path, create_cache, get_cache, move, remove, symlink


TARGET_DIR = "source"
STORE_DIR = "store"
SYMLINK_DIR = "symlink_test"

CACHE_FILE_CONTENTS = {"version": version, "original_path": TARGET_DIR}


@contextmanager
def setup():
    old_dir = os.getcwd()
    with TemporaryDirectory("tests-temp") as td:
        try:
            os.chdir(td)

            os.mkdir(TARGET_DIR)
            os.mkdir(STORE_DIR)
            os.symlink(TARGET_DIR, SYMLINK_DIR)

            cache_path = Path(TARGET_DIR).joinpath(DEFAULT_CACHE_FILENAME)
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

    cache_path = Path(TARGET_DIR).joinpath(DEFAULT_CACHE_FILENAME)

    assert check_path(existing_dir) is True
    assert check_path(nonexisting_dir) is False
    assert check_path(symlink_dir, is_symlink=True) is True
    assert check_path(cache_path) is False


@setup()
def test_cache_create():
    cache_file = "test_cache_file.json"

    cache_path = Path(TARGET_DIR).joinpath(cache_file)
    original_path = Path("/tmp/some/random/path")

    create_cache(cache_path=cache_path, original_path=original_path)

    cache = json.load(open(cache_path, "r"))

    assert cache_path.exists()
    assert cache["original_path"] == str(original_path)
    assert cache["version"] == version


@setup()
def test_cache_get():
    cache_path = Path(TARGET_DIR).joinpath(DEFAULT_CACHE_FILENAME)
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
    cache_path = Path(TARGET_DIR).joinpath(DEFAULT_CACHE_FILENAME)
    symlink_filepath = Path(TARGET_DIR).joinpath(SYMLINK_DIR)
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


@setup()
def test_transpose_init():
    t = Transpose(
        target_path=TARGET_DIR,
        store_path=STORE_DIR,
    )
    assert t.cache_filename == ".transpose.json"
    assert t.cache_path == Path(TARGET_DIR).joinpath(".transpose.json")

    t = Transpose(
        target_path=TARGET_DIR, store_path=STORE_DIR, cache_filename=".transpose.txt"
    )
    assert t.cache_filename == ".transpose.txt"
    assert t.cache_path == Path(TARGET_DIR).joinpath(".transpose.txt")


@setup()
def test_transpose_store_restore():
    t = Transpose(
        target_path=TARGET_DIR,
        store_path=STORE_DIR,
    )
    t.store("TestStore")

    target_path = Path(TARGET_DIR)
    store_path = Path(STORE_DIR).joinpath("TestStore")

    assert store_path.is_dir() and not store_path.is_symlink()
    assert target_path.is_dir() and target_path.is_symlink()
    assert t.cache_path.is_file()

    t = Transpose(
        target_path=str(store_path),
        store_path=STORE_DIR,
    )
    t.restore()

    assert not store_path.exists()
    assert target_path.is_dir() and not target_path.is_symlink()
    assert not t.cache_path.exists()


@setup()
def test_transpose_restore_force():
    nonexistent_path = Path(STORE_DIR).joinpath("long/path")

    # Overwrite cache file with nonexistent directory
    cache_path = Path(TARGET_DIR).joinpath(DEFAULT_CACHE_FILENAME)
    cache = {"version": version, "original_path": str(nonexistent_path)}
    with open(str(cache_path), "w") as f:
        json.dump(cache, f)

    # Force not enabled, should raise exception
    t = Transpose(target_path=TARGET_DIR, store_path=STORE_DIR)
    with pytest.raises(TransposeError):
        t.restore()
    assert not nonexistent_path.exists()

    # Force enabled, should create directory tree
    t = Transpose(target_path=TARGET_DIR, store_path=STORE_DIR, force=True)
    t.restore()
    assert nonexistent_path.exists()
