import os

from importlib.metadata import version

from .logger import create_logger

DEFAULT_XDG_PATH = os.environ.get("XDG_DATA_HOME", f"{os.environ['HOME']}/.local/share")
STORE_PATH = f"{DEFAULT_XDG_PATH}/transpose"
DEFAULT_STORE_PATH = os.environ.get("TRANSPOSE_STORE_PATH", STORE_PATH)

version = version("transpose")

logger = create_logger(__package__)

from .transpose import Transpose, TransposeConfig, TransposeEntry  # noqa: E402
