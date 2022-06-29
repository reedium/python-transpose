from os import environ
from pydantic import BaseSettings

default_xdg_path = environ.get("XDG_DATA_HOME", f"{environ['HOME']}/.local/share")


class Config(BaseSettings):
    store_path: str = f"{default_xdg_path}/transpose"
    cache_filename: str = ".transpose.json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        env_prefix = "TRANSPOSE_"
