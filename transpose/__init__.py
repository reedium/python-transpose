from .logger import create_logger
import os

DEFAULT_XDG_PATH = os.environ.get("XDG_DATA_HOME", f"{os.environ['HOME']}/.local/share")
DEFAULT_CACHE_FILENAME = ".transpose.json"
DEFAULT_STORE_PATH = f"{DEFAULT_XDG_PATH}/transpose"

version_info = (0, 9, 0)
version = ".".join(str(c) for c in version_info)

logger = create_logger(__package__)

from .transpose import Transpose  # noqa: E402
