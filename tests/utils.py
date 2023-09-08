import json

from contextlib import contextmanager
from pathlib import Path
from shutil import rmtree
from tempfile import TemporaryDirectory

from transpose import version


ENTRY_NAME = "MyName"
TESTS_PATH = Path("tests-temp")
STORE_PATH = TESTS_PATH.joinpath("store")
TARGET_PATH = TESTS_PATH.joinpath("source")
SYMLINK_TEST_PATH = TESTS_PATH.joinpath("symlink_test")

ENTRY_STORE_PATH = STORE_PATH.joinpath(ENTRY_NAME)
TRANSPOSE_CONFIG_PATH = STORE_PATH.joinpath("transpose.json")

TRANSPOSE_CONFIG = {
    "version": version,
    "entries": {ENTRY_NAME: {"name": ENTRY_NAME, "path": str(TARGET_PATH)}},
}


@contextmanager
def setup_apply():
    """
    Create the following directory structure:
        tests-temp/
        ├── store/
        │   ├── transpose.json
        │   └── MyName/
        └── symlink_test/ -> source/
    """
    try:
        with TemporaryDirectory(str(TESTS_PATH)):
            STORE_PATH.mkdir(parents=True, exist_ok=True)
            ENTRY_STORE_PATH.mkdir(parents=True, exist_ok=True)
            SYMLINK_TEST_PATH.symlink_to(TARGET_PATH.resolve())

            with open(str(TRANSPOSE_CONFIG_PATH), "w") as f:
                json.dump(TRANSPOSE_CONFIG, f)

            yield
    finally:
        # This shouldn't be necessary but is for some reason
        rmtree(TESTS_PATH)


@contextmanager
def setup_restore():
    """
    Create the following directory structure:
        tests-temp/
        ├── store/
        │   ├── MyName/
        │   └── transpose.json
        └── symlink_test -> store/MyName
    """
    try:
        with TemporaryDirectory(str(TESTS_PATH)):
            ENTRY_STORE_PATH.mkdir(parents=True, exist_ok=True)
            SYMLINK_TEST_PATH.symlink_to(TARGET_PATH)

            with open(str(TRANSPOSE_CONFIG_PATH), "w") as f:
                json.dump(TRANSPOSE_CONFIG, f)

            yield
    finally:
        # This shouldn't be necessary but is for some reason
        rmtree(TESTS_PATH)


@contextmanager
def setup_store():
    """
    Create the following directory structure:
        tests-temp/
        ├── source/
        └── store/
        │   ├── transpose-bad.json
        │   ├── transpose-invalid.json
            └── transpose.json
    """
    try:
        with TemporaryDirectory(str(TESTS_PATH)):
            TARGET_PATH.mkdir(parents=True, exist_ok=True)
            STORE_PATH.mkdir(parents=True, exist_ok=True)

            with open(str(TRANSPOSE_CONFIG_PATH), "w") as f:
                json.dump(TRANSPOSE_CONFIG, f)

            bad_config_path = STORE_PATH.joinpath("transpose-bad.json")
            bad_config = '{"version": "1.0.0"}'  # Missing entries
            with open(str(bad_config_path), "w") as f:
                f.write(bad_config)
            assert bad_config_path.exists()

            invalid_config_path = STORE_PATH.joinpath("transpose-invalid.json")
            invalid_config = "[{'invalidJSONFormat'}]"
            with open(str(invalid_config_path), "w") as f:
                f.write(invalid_config)
            assert invalid_config_path.exists()

            yield
    finally:
        # This shouldn't be necessary but is for some reason
        rmtree(TESTS_PATH)
