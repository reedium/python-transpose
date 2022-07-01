import json
import pytest

from pathlib import Path

from transpose import Transpose, version, DEFAULT_CACHE_FILENAME
from transpose.exceptions import TransposeError

from .utils import STORE_DIR, TARGET_DIR, setup_env


@setup_env()
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


@setup_env()
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


@setup_env()
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
