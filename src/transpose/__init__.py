from importlib.metadata import version
import os

from .logger import create_logger

DEFAULT_XDG_PATH = os.environ.get("XDG_DATA_HOME", f"{os.environ['HOME']}/.local/share")
DEFAULT_CACHE_FILENAME = ".transpose.json"
DEFAULT_STORE_PATH = f"{DEFAULT_XDG_PATH}/transpose"

version = version("transpose")

logger = create_logger(__package__)

from .transpose import Transpose  # noqa: E402
