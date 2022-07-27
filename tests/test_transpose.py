import json
import pathlib
import pytest

from transpose import Transpose
from transpose.exceptions import TransposeError

from .utils import (
    STORE_DIR,
    STORED_DIR,
    TARGET_DIR,
    setup_restore,
    setup_store,
    setup_apply,
)


def test_init():
    t = Transpose(target_path=TARGET_DIR)
    assert t.cache_filename == ".transpose.json"
    assert t.cache_path == pathlib.Path(TARGET_DIR).joinpath(".transpose.json")

    t = Transpose(target_path=TARGET_DIR, cache_filename=".transpose.txt")
    assert t.cache_filename == ".transpose.txt"
    assert t.cache_path == pathlib.Path(TARGET_DIR).joinpath(".transpose.txt")


@setup_apply()
def test_apply():
    store_path = pathlib.Path(STORE_DIR)
    target_path = pathlib.Path(TARGET_DIR)

    t = Transpose(target_path=STORE_DIR)

    with open(t.cache_path, "r") as f:
        cache = json.load(f)

    # Test cache doesn't exist
    t.cache_path.unlink()
    with pytest.raises(TransposeError):
        t.apply()

    with open(t.cache_path, "w") as f:
        json.dump(cache, f)

    pathlib.Path(cache["original_path"]).symlink_to("bad/path")

    # Success
    t.apply()

    assert store_path.is_dir() and not store_path.is_symlink()
    assert target_path.is_dir() and target_path.is_symlink()


@setup_restore()
def test_create():
    target_path = pathlib.Path(TARGET_DIR)
    stored_path = pathlib.Path(STORE_DIR).joinpath(STORED_DIR)

    t = Transpose(target_path=str(target_path))

    # Missing stored path
    stored_path.rename("tmp")
    with pytest.raises(TransposeError):
        t.create(stored_path=stored_path)
    pathlib.Path("tmp").rename(stored_path)

    cache_path = stored_path.joinpath(t.cache_filename)

    # Successful Create
    t.create(stored_path=stored_path)
    assert t.cache_path == cache_path
    assert cache_path.exists()

    with open(t.cache_path, "r") as f:
        cache = json.load(f)

    assert cache["original_path"] == str(target_path.absolute())


@setup_store()
def test_store():
    t = Transpose(target_path=TARGET_DIR)
    t.store(store_path=STORE_DIR)

    target_path = pathlib.Path(TARGET_DIR)
    store_path = pathlib.Path(STORE_DIR).joinpath(target_path.name)

    # Successful Store
    assert store_path.is_dir() and not store_path.is_symlink()
    assert target_path.is_dir() and target_path.is_symlink()
    assert t.cache_path.is_file()


@setup_store()
def test_store_named():
    t = Transpose(target_path=TARGET_DIR)
    t.store(store_path=STORE_DIR, name="TestStore")

    target_path = pathlib.Path(TARGET_DIR)
    store_path = pathlib.Path(STORE_DIR).joinpath("TestStore")

    # Successful Store
    assert store_path.is_dir() and not store_path.is_symlink()
    assert target_path.is_dir() and target_path.is_symlink()
    assert t.cache_path.is_file()


@setup_restore()
def test_restore():
    target_path = pathlib.Path(TARGET_DIR)
    stored_path = pathlib.Path(STORE_DIR).joinpath(STORED_DIR)

    t = Transpose(target_path=str(stored_path))

    # Missing Cache File
    cache = t.cache_path.read_text()
    t.cache_path.unlink()
    with pytest.raises(TransposeError):
        t.restore()
    t.cache_path.write_text(cache)
    cache = json.loads(cache)

    # Missing Target Path (original path)
    t.target_path.rename("newpath")
    with pytest.raises(TransposeError):
        t.restore()
    pathlib.Path("newpath").rename(t.target_path)

    # Original Path is a symlink - Should be removed and successfully restore
    original_path = pathlib.Path(cache["original_path"])
    original_path.rename("newpath")
    original_path.symlink_to("newpath")

    # Successful
    t.restore()

    assert target_path.is_dir() and not target_path.is_symlink()
    assert not stored_path.exists()
    assert not t.cache_path.exists()
