from pathlib import Path

from .exceptions import TransposeError
from .utils import check_path, create_cache, get_cache, move, remove, symlink


class Transpose:
    def __init__(
        self,
        target_path: str,
        store_path: str,
        cache_filename: str = None,
        force: bool = False,
    ) -> None:
        self.target_path = Path(target_path)
        self.store_path = Path(store_path)

        if not cache_filename:
            cache_filename = ".transpose.json"
        self.cache_filename = cache_filename
        self.cache_path = Path(self.target_path).joinpath(cache_filename)

        self.force = force

    def restore(self) -> None:
        """
        Restores a previously Transpose managed directory to it's previous location.
        """
        if not self.cache_path.exists():
            raise TransposeError(
                f"Cache file does not exist indicating target is not managed by Transpose: {self.cache_path}"
            )
        if not self.target_path.exists():
            raise TransposeError(f"Target path does not exist: {self.target_path}")

        cache = get_cache(self.cache_path)
        original_path = Path(cache["original_path"])

        if original_path.is_symlink():
            remove(original_path)
        elif original_path.exists():
            raise TransposeError(
                f"Original path in cache file already exists: {original_path}"
            )

        if not original_path.parent.exists() and self.force:
            original_path.parent.mkdir(parents=True)

        try:
            move(source=self.target_path, destination=original_path)
        except FileNotFoundError:
            raise TransposeError(
                f"Original path, {original_path}, does not exist. Use '-f' to create the path"
            )

        new_cache_path = Path(original_path).joinpath(self.cache_filename)
        remove(new_cache_path)

    def store(self, name: str) -> None:
        """
        Moves a directory to a central location and creates a symlink to the old path.
        """
        new_location = Path(self.store_path).joinpath(name)

        if not check_path(path=self.target_path):
            raise TransposeError(
                f"Target path, {self.target_path}, does not exist. Cannot continue."
            )
        if check_path(path=new_location):
            raise TransposeError(
                f"Store path, {new_location}, already exists. Cannot continue."
            )

        create_cache(
            cache_path=self.cache_path,
            original_path=self.target_path,
        )

        move(source=self.target_path, destination=new_location)
        symlink(target_path=new_location, symlink_path=self.target_path)
