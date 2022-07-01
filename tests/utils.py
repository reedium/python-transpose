import os
import json

from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from transpose import DEFAULT_CACHE_FILENAME, version
from transpose.exceptions import TransposeError


TARGET_DIR = "source"
STORE_DIR = "store"
SYMLINK_DIR = "symlink_test"

CACHE_FILE_CONTENTS = {"version": version, "original_path": TARGET_DIR}


@contextmanager
def setup_env():
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
