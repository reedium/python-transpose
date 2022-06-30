import argparse
import os

from pydantic import BaseSettings

from transpose import Transpose, version

default_xdg_path = os.environ.get("XDG_DATA_HOME", f"{os.environ['HOME']}/.local/share")


class Config(BaseSettings):
    store_path: str = f"{default_xdg_path}/transpose"
    cache_filename: str = ".transpose.json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        env_prefix = "TRANSPOSE_"


def entry_point() -> None:
    config = Config()
    args = parse_arguments()

    t = Transpose(
        target_path=args.target_path,
        store_path=config.store_path,
        cache_filename=config.cache_filename,
    )

    if args.action == "restore":
        t.restore()
    elif args.action == "store":
        t.store(name=args.name)


def parse_arguments():
    base_parser = argparse.ArgumentParser(add_help=False)
    parser = argparse.ArgumentParser(
        parents=[base_parser],
        description="""
        Move and symlink a path for easier management
        """,
    )
    parser.add_argument("--version", action="version", version=f"Transpose {version}")

    subparsers = parser.add_subparsers(
        help="Transpose Action", dest="action", required=True
    )

    restore_parser = subparsers.add_parser(
        "restore",
        help="Move a transposed directory back to it's original location",
        parents=[base_parser],
    )
    restore_parser.add_argument(
        "target_path",
        help="The path to the directory to restore",
    )

    store_parser = subparsers.add_parser(
        "store", help="Move target and create symlink in place", parents=[base_parser]
    )
    store_parser.add_argument(
        "name",
        help="The name of the directory that will be created in the store path",
    )
    store_parser.add_argument(
        "target_path",
        help="The path to the directory to be stored",
    )

    return parser.parse_args()


if __name__ == "__main__":
    entry_point()
