import json
import pathlib
import pytest

from transpose import Transpose, version, DEFAULT_CACHE_FILENAME
from transpose.exceptions import TransposeError

from .utils import STORE_DIR, TARGET_DIR, setup_env


@setup_env()
def test_init():
    t = Transpose(
        target_path=TARGET_DIR,
        store_path=STORE_DIR,
    )
    assert t.cache_filename == ".transpose.json"
    assert t.cache_path == pathlib.Path(TARGET_DIR).joinpath(".transpose.json")

    t = Transpose(
        target_path=TARGET_DIR, store_path=STORE_DIR, cache_filename=".transpose.txt"
    )
    assert t.cache_filename == ".transpose.txt"
    assert t.cache_path == pathlib.Path(TARGET_DIR).joinpath(".transpose.txt")


@setup_env()
def test_apply():
    store_path = pathlib.Path(STORE_DIR)
    target_path = pathlib.Path(TARGET_DIR)
    store_path.rmdir()
    target_path.rename(store_path)

    t = Transpose(
        target_path=STORE_DIR,
        store_path=STORE_DIR,
    )

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


@setup_env()
def test_store_restore():
    t = Transpose(
        target_path=TARGET_DIR,
        store_path=STORE_DIR,
    )

    target_path = pathlib.Path(TARGET_DIR)
    store_path = pathlib.Path(STORE_DIR).joinpath("TestStore")
    t.store("TestStore")

    # STORE
    ## Successful Store
    assert store_path.is_dir() and not store_path.is_symlink()
    assert target_path.is_dir() and target_path.is_symlink()
    assert t.cache_path.is_file()

    t = Transpose(
        target_path=str(store_path),
        store_path=STORE_DIR,
    )

    # RESTORE
    ## Missing Cache File
    cache = t.cache_path.read_text()
    t.cache_path.unlink()
    with pytest.raises(TransposeError):
        t.restore()
    t.cache_path.write_text(cache)
    cache = json.loads(cache)

    ## Missing Target Path
    t.target_path.rename("newpath")
    with pytest.raises(TransposeError):
        t.restore()
    pathlib.Path("newpath").rename(t.target_path)

    ## Successful Restore
    t.restore()

    assert not store_path.exists()
    assert target_path.is_dir() and not target_path.is_symlink()
    assert not t.cache_path.exists()
