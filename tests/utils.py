import os
import json
import pathlib

from contextlib import contextmanager
from tempfile import TemporaryDirectory

from transpose import DEFAULT_CACHE_FILENAME, version


STORE_DIR = "store"
STORED_DIR = "my_app"  # Directory already in storage
SYMLINK_DIR = "symlink_test"
TARGET_DIR = "source"

CACHE_FILE_CONTENTS = {"version": version, "original_path": TARGET_DIR}


@contextmanager
def setup_apply():
    """
    Create the following directory structure:
        temp/
        ├── target/
        │   └── .transpose.json # contains {"version": version, "original_path": "source/"}
        └── symlink_test/ -> source/
    """
    old_dir = os.getcwd()
    with TemporaryDirectory("tests-temp") as td:
        try:
            os.chdir(td)

            os.mkdir(STORE_DIR)
            os.symlink(STORE_DIR, SYMLINK_DIR)

            target_cache_path = pathlib.Path(STORE_DIR).joinpath(DEFAULT_CACHE_FILENAME)
            with open(str(target_cache_path), "w") as f:
                json.dump(CACHE_FILE_CONTENTS, f)

            yield
        finally:
            os.chdir(old_dir)


@contextmanager
def setup_restore():
    """
    Create the following directory structure:
        temp/
        ├── source/
        └── store/
            └── my_app/
                └── .transpose.json # contains {"version": version, "original_path": "source/"}
    """
    old_dir = os.getcwd()
    with TemporaryDirectory("tests-temp") as td:
        try:
            os.chdir(td)

            os.mkdir(TARGET_DIR)
            os.mkdir(STORE_DIR)
            os.mkdir(f"{STORE_DIR}/{STORED_DIR}")

            target_cache_path = pathlib.Path(f"{STORE_DIR}/{STORED_DIR}").joinpath(
                DEFAULT_CACHE_FILENAME
            )
            with open(str(target_cache_path), "w") as f:
                json.dump(CACHE_FILE_CONTENTS, f)

            yield
        finally:
            os.chdir(old_dir)


@contextmanager
def setup_store():
    """
    Create the following directory structure:
        temp/
        ├── source/
        │   └── .transpose.json # contains {"version": version, "original_path": "source/"}
        └── store/
    """
    old_dir = os.getcwd()
    with TemporaryDirectory("tests-temp") as td:
        try:
            os.chdir(td)

            os.mkdir(TARGET_DIR)
            os.mkdir(STORE_DIR)
            os.symlink(TARGET_DIR, SYMLINK_DIR)

            target_cache_path = pathlib.Path(TARGET_DIR).joinpath(
                DEFAULT_CACHE_FILENAME
            )
            with open(str(target_cache_path), "w") as f:
                json.dump(CACHE_FILE_CONTENTS, f)

            yield
        finally:
            os.chdir(old_dir)
