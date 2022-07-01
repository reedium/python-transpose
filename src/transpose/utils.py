from pathlib import Path
from typing import Dict

import json

from . import version


def check_path(path: Path, is_symlink: bool = False) -> bool:
    """
    Checks whether a path exists and is a directory (doesn't support single files)

    Args:
        path: The location to the path being verified
        is_symlink: Should this path be a symlink?

    Returns:
        bool
    """
    if is_symlink and not path.is_symlink():
        return False
    if not is_symlink and path.is_symlink():
        return False
    if not path.exists():
        return False
    if not path.is_dir():
        return False

    return True


def create_cache(cache_path: Path, original_path: Path) -> None:
    """
    Create a cache file for transpose settings in the stored directory

    Args:
        cache_path: Path to store the cache file
        original_path: Path where the stored directory originated

    Returns:
        None
    """
    template = {"version": version, "original_path": str(original_path)}
    with open(str(cache_path), "w") as f:
        json.dump(template, f)


def get_cache(cache_path: Path) -> Dict:
    """
    Read a JSON cache file

    Args:
        cache_path: Path to the Transpose cache file

    Returns:
        dict: Cache file contents
    """
    return json.load(open(cache_path, "r"))


def move(source: Path, destination: Path) -> None:
    """
    Move a file using pathlib
    """
    source.rename(destination)


def remove(path: Path) -> None:
    """
    Remove a file or symlink
    """
    if not path.is_symlink() and not path.is_file():
        return

    path.unlink()


def symlink(target_path: Path, symlink_path: Path) -> None:
    """
    Symlink a file or directory
    """
    symlink_path.symlink_to(target_path)
