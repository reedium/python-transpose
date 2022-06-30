import argparse
import os

from config import Config
from transpose import Transpose, version

config = Config()


def main() -> None:
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
    main()