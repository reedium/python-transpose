import argparse
import os

from transpose import Transpose, version, DEFAULT_STORE_PATH, DEFAULT_CACHE_FILENAME


def entry_point() -> None:
    args = parse_arguments()

    t = Transpose(
        target_path=args.target_path,
        store_path=args.store_path,
        cache_filename=args.cache_filename,
    )

    if args.action == "apply":
        t.apply()
    elif args.action == "create":
        t.create(stored_path=args.stored_path)
    elif args.action == "restore":
        t.restore()
    elif args.action == "store":
        t.store(name=args.name)


def parse_arguments(args=None):
    cache_filename = os.environ.get("TRANSPOSE_CACHE_FILENAME", DEFAULT_CACHE_FILENAME)
    store_path = os.environ.get("TRANSPOSE_STORE_PATH", DEFAULT_STORE_PATH)

    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument(
        "--cache-filename",
        dest="cache_filename",
        nargs="?",
        default=cache_filename,
        help="The name of the cache file added to the target directory (default: %(default)s)",
    )

    parser = argparse.ArgumentParser(
        parents=[base_parser],
        description="""
        Move and symlink a path for easier management
        """,
    )
    parser.add_argument("--version", action="version", version=f"Transpose {version}")
    parser.add_argument(
        "--store-path",
        dest="store_path",
        nargs="?",
        default=store_path,
        help="The path to where the targets should be stored (default: %(default)s)",
    )

    subparsers = parser.add_subparsers(
        help="Transpose Action", dest="action", required=True
    )

    apply_parser = subparsers.add_parser(
        "apply",
        help="Recreate the symlink from the cache file (useful after moving store loction)",
        parents=[base_parser],
    )
    apply_parser.add_argument(
        "target_path",
        help="The path to the directory to locate the cache file",
    )

    create_parser = subparsers.add_parser(
        "create",
        help="Create the cache file from an already stored path. Only creates the cache file.",
        parents=[base_parser],
    )
    create_parser.add_argument(
        "target_path",
        help="The path to the directory that should by a symlink",
    )
    create_parser.add_argument(
        "stored_path",
        help="The path that is currently stored (the target of the symlink)",
    )

    restore_parser = subparsers.add_parser(
        "restore",
        help="Move a transposed directory back to it's original location, based on the cachefile",
        parents=[base_parser],
    )
    restore_parser.add_argument(
        "target_path",
        help="The path to the directory to restore",
    )

    store_parser = subparsers.add_parser(
        "store",
        help="Move target and create symlink in place",
        parents=[base_parser],
    )
    store_parser.add_argument(
        "target_path",
        help="The path to the directory that should be moved to storage",
    )
    store_parser.add_argument(
        "name",
        nargs="?",
        default=None,
        help="The name of the directory that will be created in the store path (default: target_path)",
    )

    return parser.parse_args(args)


if __name__ == "__main__":
    entry_point()
