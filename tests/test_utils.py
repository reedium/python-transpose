import json
import pathlib

from transpose import version
from transpose.utils import move, remove, symlink


from .utils import (
    TARGET_PATH,
    ENTRY_STORE_PATH,
    STORE_PATH,
    SYMLINK_TEST_PATH,
    setup_store,
)


@setup_store()
def test_file_move():
    destination = STORE_PATH.joinpath("test_move")
    move(source=TARGET_PATH.absolute(), destination=destination.absolute())
    assert not TARGET_PATH.exists()
    assert destination.exists()


@setup_store()
def test_file_remove():
    SYMLINK_TEST_PATH.symlink_to(ENTRY_STORE_PATH)
    remove(path=TARGET_PATH)
    remove(path=SYMLINK_TEST_PATH)

    assert TARGET_PATH.exists()  # Should not be able to remove directories
    assert not ENTRY_STORE_PATH.exists()  # Should be able to remove symlinks


@setup_store()
def test_file_symlink():
    symlink(target_path=TARGET_PATH, symlink_path=SYMLINK_TEST_PATH)

    assert TARGET_PATH.exists()
    assert SYMLINK_TEST_PATH.is_symlink()
    assert SYMLINK_TEST_PATH.readlink() == TARGET_PATH.resolve()
