from pathlib import Path, PurePath

from .utils import check_path, create_cache, get_cache, move, remove, symlink


class Transpose:
    def __init__(
        self, target_path: str, store_path: str, cache_filename: str = None
    ) -> None:
        self.target_path = Path(target_path)
        self.store_path = Path(store_path)

        if not cache_filename:
            cache_filename = ".transpose.json"
        self.cache_filename = cache_filename
        self.cache_path = Path(PurePath(self.target_path, cache_filename))

    def restore(self) -> None:
        """
        Restores a previously Transpose managed directory to it's previous location.

        Performs:
            1. Verify `cache_file` exists
            2. Verify `target_path` exists
            3. Verify if `original_path` in cache is a symlink
                a. Remove if true
            4. Verify `original_path` doesn't exist
            5. Move `target_path` to `original_path` based on cache file settings

        Args:
            None

        Returns:
            None

        Raises:
            ValueError: Any paths not existing
            RuntimeError: Any error during the actual path changes
        """
        if not self.cache_path.exists():
            raise ValueError(
                f"Cache file does not exist indicating target is not managed by Transpose: {self.cache_path}"
            )
        if not self.target_path.exists():
            raise ValueError(f"Target path does not exist: {self.target_path}")

        cache = get_cache(self.cache_path)
        original_path = Path(cache["original_path"])

        if original_path.is_symlink():
            try:
                remove(original_path)
            except:  # noqa: E722 # TODO
                raise RuntimeError(
                    f"Failed to remove symlink in original path: {original_path}"
                )
        elif original_path.exists():
            raise ValueError(
                f"Original path in cache file already exists: {original_path}"
            )

        try:
            move(source=self.target_path, destination=original_path)
        except:  # noqa: E722 # TODO
            raise RuntimeError(
                f"Failed to move target to original location: {self.target_path} -> {original_path}"
            )

        new_cache_path = Path(PurePath(original_path, self.cache_filename))
        try:
            remove(new_cache_path)
        except:  # noqa: E722 # TODO
            raise RuntimeError(
                f"Failed to remove previous cache file: {new_cache_path}"
            )

    def store(self, name: str) -> None:
        """
        Moves a directory to a central location and creates a symlink to the old path.

        Performs:
            1. Verify `target_path` exists
            2. Verify `store_path` exists
            3. Create the cache file
            4. Move the `target_path` to `store_path/name`
            5. Create symlink `target_path` -> `store_path/name`

        Args:
            name: The directory name to give the new location

        Returns:
            None

        Raises
            ValueError: Any paths not existing
            RuntimeError: Any error during the actual path changes
        """
        new_location = Path(PurePath(self.store_path, name))

        if not check_path(path=self.target_path):
            raise ValueError(
                f"Target path, {self.target_path}, does not exist. Cannot continue."
            )
        if check_path(path=new_location):
            raise ValueError(
                f"Store path, {new_location}, already exists. Cannot continue."
            )

        try:
            create_cache(
                cache_path=self.cache_path,
                original_path=self.target_path,
            )
        except:  # noqa: E722 # TODO
            raise RuntimeError("Failed to create cache file: {self.cache_path}")

        try:
            move(source=self.target_path, destination=new_location)
        except:  # noqa: E722 # TODO
            raise RuntimeError(
                f"Failed to move target to store path: {self.target_path} -> {self.new_location}"
            )

        try:
            symlink(target_path=new_location, symlink_path=self.target_path)
        except:  # noqa: E722 # TODO
            raise RuntimeError(
                f"Failed to symlink store path to target: {new_location} -> {self.target_path}"
            )
