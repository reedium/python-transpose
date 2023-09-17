import shutil

from pathlib import Path


def move(source: Path, destination: Path) -> None:
    """
    Move a file using pathlib
    """
    shutil.move(source.expanduser(), destination.expanduser())


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
    symlink_path.symlink_to(target_path.resolve())
