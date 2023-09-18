import argparse

from pathlib import Path

from transpose import Transpose, version, DEFAULT_STORE_PATH
from .exceptions import TransposeError


def entry_point() -> None:
    args = parse_arguments()
    config_path = f"{args.store_path}/transpose.json"

    try:
        run(args, config_path)
    except TransposeError as e:
        print(f"Transpose Error: {e}")


def run(args, config_path) -> None:
    t = Transpose(config_path)

    if args.action == "apply":
        t.apply(args.name, force=args.force)
    elif args.action == "apply-all":
        run_apply_all(t, force=args.force)
    elif args.action == "restore":
        t.restore(args.name, force=args.force)
    elif args.action == "store":
        if not args.name:
            target_path = Path(args.target_path)
            args.name = str(target_path.parts[-1])
        t.store(args.name, args.target_path)
    elif args.action == "config":
        if args.config_action == "add":
            t.config.add(args.name, args.path)
            t.config.save(config_path)
        elif args.config_action == "get":
            print(t.config.get(args.name))
        elif args.config_action == "list":
            for name in t.config.entries:
                print(f"\t{name:<30} -> {t.config.entries[name].path}")
        elif args.config_action == "remove":
            t.config.remove(args.name)
            t.config.save(config_path)
        elif args.config_action == "update":
            t.config.update(args.name, args.field_key, args.field_value)
            t.config.save(config_path)


def run_apply_all(t: Transpose, force: bool = False) -> None:
    """
    Loop over the entries and recreate the symlinks to the store location

    Useful after restoring a machine

    Args:
        t: An instance of Transpose
        force: If enabled and path already exists, move the path to '{path}.backup' first

    Returns:
        None
    """
    for entry_name in sorted(t.config.entries):
        try:
            t.apply(entry_name, force)
            print(f"\t{entry_name:<30}: success")
        except TransposeError as e:
            print(f"\t{entry_name:<30}: {e}")


def parse_arguments(args=None):
    base_parser = argparse.ArgumentParser(add_help=False)

    parser = argparse.ArgumentParser(
        parents=[base_parser],
        description="""
        Move and symlink a path for easy, central management
        """,
    )
    parser.add_argument("--version", action="version", version=f"Transpose {version}")
    parser.add_argument(
        "-s",
        "--store-path",
        dest="store_path",
        nargs="?",
        default=DEFAULT_STORE_PATH,
        help="The location to store the moved entities (default: %(default)s)",
    )

    subparsers = parser.add_subparsers(
        help="Transpose Action", dest="action", required=True
    )

    apply_parser = subparsers.add_parser(
        "apply",
        help="Recreate the symlink for an entity (useful after moving store locations)",
        parents=[base_parser],
    )
    apply_parser.add_argument(
        "name",
        help="The name of the stored entity to apply",
    )
    apply_parser.add_argument(
        "--force",
        dest="force",
        help="If original path already exists, existing path to <path>.backup and continue",
        action="store_true",
    )

    apply_all_parser = subparsers.add_parser(
        "apply-all",
        help="Recreate the symlink for all entities",
        parents=[base_parser],
    )
    apply_all_parser.add_argument(
        "--force",
        dest="force",
        help="If original path already exists, existing path to <path>.backup and continue",
        action="store_true",
    )

    restore_parser = subparsers.add_parser(
        "restore",
        help="Move a transposed directory back to it's original location, based on the cachefile",
        parents=[base_parser],
    )
    restore_parser.add_argument(
        "name",
        help="The name of the stored entity to restore",
    )
    restore_parser.add_argument("--force", dest="force", action="store_true")

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

    config_parser = subparsers.add_parser(
        "config",
        help="Modify the transpose config file without any filesystem changes",
        parents=[base_parser],
    )
    config_subparsers = config_parser.add_subparsers(
        help="Transpose Config Action", dest="config_action", required=True
    )

    config_add_parser = config_subparsers.add_parser(
        "add",
        help="Add an entry manually to the tranpose config",
        parents=[base_parser],
    )
    config_add_parser.add_argument(
        "name",
        help="The name of the entry in the store path",
    )
    config_add_parser.add_argument(
        "path",
        help="The path of the directory that should be symlinked to the store",
    )

    config_get_parser = config_subparsers.add_parser(
        "get",
        help="Retrieve the settings of a specific entity, such as the path",
        parents=[base_parser],
    )
    config_get_parser.add_argument(
        "name",
        help="The name of the entry in the store path",
    )

    config_subparsers.add_parser(
        "list",
        help="List the names of all entities in the transpose config",
        parents=[base_parser],
    )

    config_remove_parser = config_subparsers.add_parser(
        "remove",
        help="Remove an entry from the config",
        parents=[base_parser],
    )
    config_remove_parser.add_argument(
        "name",
        help="The name of the entry in the store path",
    )

    config_update_parser = config_subparsers.add_parser(
        "update",
        help="Update an entry of the transpose config",
        parents=[base_parser],
    )
    config_update_parser.add_argument(
        "name",
        help="The name of the entry in the store path",
    )
    config_update_parser.add_argument(
        "field_key",
        help="The config key to be updated",
    )
    config_update_parser.add_argument(
        "field_value",
        help="The value to updated in the config",
    )

    return parser.parse_args(args)


if __name__ == "__main__":
    entry_point()
