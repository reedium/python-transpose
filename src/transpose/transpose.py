from dataclasses import asdict, dataclass, field
from pathlib import Path

# from typing import Self

import datetime
import json

from . import version as transpose_version
from .exceptions import TransposeError
from .utils import move, remove, symlink


@dataclass
class TransposeEntry:
    name: str
    path: str
    created: str  # Should be datetime.datetime but not really necessary here


@dataclass
class TransposeConfig:
    entries: dict = field(default_factory=dict)
    version: str = field(default=transpose_version)

    def add(self, name: str, path: str, created: str = None) -> None:
        """
        Add a new entry to the entries

        Args:
            name: The name of the entry (must not exist)
            path: The path where the entry originally exists
            created: The date in datetime.now().__str__() format

        Returns:
            None
        """
        if self.entries.get(name):
            raise TransposeError(f"'{name}' already exists")

        if not created:
            created = str(datetime.datetime.now())

        self.entries[name] = TransposeEntry(
            name=name,
            path=str(path),
            created=created,
        )

    def get(self, name: str) -> TransposeEntry:
        """
        Get an entry by the name

        Args:
            name: The name of the entry (must exist)

        Returns:
            TransposeEntry
        """
        try:
            return self.entries[name]
        except KeyError:
            raise TransposeError(f"'{name}' does not exist in Transpose config entries")

    def remove(self, name: str) -> None:
        """
        Remove an entry by name

        Args:
            name: The name of the entry (must exist)

        Returns:
            None
        """
        try:
            del self.entries[name]
        except KeyError:
            raise TransposeError(f"'{name}' does not exist in Transpose config entries")

    def update(self, name: str, path: str) -> None:
        """
        Update an entry by name

        Args:
            name: The name of the entry (must exist)
            path: The path where the entry originally exists

        Returns:
            None
        """
        try:
            self.entries[name].path = path
        except KeyError:
            raise TransposeError(f"'{name}' does not exist in Transpose config entries")

    @staticmethod
    def load(config_path: str):  # -> Self:
        try:
            in_config = json.load(open(config_path, "r"))
        except json.decoder.JSONDecodeError as e:
            raise TransposeError(f"Invalid JSON format for '{config_path}': {e}")

        config = TransposeConfig()
        try:
            for name in in_config["entries"]:
                config.add(
                    name,
                    in_config["entries"][name]["path"],
                    created=in_config["entries"].get("created"),
                )
        except (KeyError, TypeError) as e:
            raise TransposeError(f"Unrecognized Transpose config file format: {e}")

        return config

    def save(self, config_path: str) -> None:
        """
        Save the Config to a location in JSON format

        Args:
            path: The path to save the json file

        Returns:
            None
        """
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(str(config_path), "w") as f:
            json.dump(self.to_dict(), f, default=str)

    def to_dict(self) -> dict:
        return asdict(self)


class Transpose:
    config: TransposeConfig
    config_path: Path
    store_path: Path

    def __init__(self, config_path: str) -> None:
        self.config = TransposeConfig.load(config_path)
        self.config_path = Path(config_path)
        self.store_path = self.config_path.parent

        if not self.store_path.exists():
            self.store_path.mkdir(parents=True)

    def apply(self, name: str, force: bool = False) -> None:
        """
        Create/recreate the symlink to an existing entry

        Args:
            name: The name of the entry (must exist)
            force: If enabled and path already exists, move the path to '{path}-bak'

        Returns:
            None
        """
        if not self.config.entries.get(name):
            raise TransposeError(f"Entry does not exist: '{name}'")

        entry_path = Path(self.config.entries[name].path)
        if entry_path.exists():
            if entry_path.is_symlink():
                remove(entry_path)
            elif force:  # Backup the existing path
                move(entry_path, entry_path.with_suffix(".backup"))
            else:
                raise TransposeError(
                    f"Entry path already exists, cannot apply (force required): '{entry_path}'"
                )

        symlink(
            target_path=self.store_path.joinpath(name),
            symlink_path=entry_path,
        )

    def restore(self, name: str, force: bool = False) -> None:
        """
        Remove the symlink and move the stored entry back to it's original path

        Args:
            name: The name of the entry (must exist)
            force: If enabled and path already exists, move the path to '{path}-bak'

        Returns:
            None
        """
        if not self.config.entries.get(name):
            raise TransposeError(f"Could not locate entry by name: '{name}'")

        entry_path = Path(self.config.entries[name].path)
        if entry_path.exists():
            if entry_path.is_symlink():
                remove(entry_path)
            elif force:  # Backup the existing path
                move(entry_path, entry_path.with_suffix(".backup"))
            else:
                raise TransposeError(
                    f"Entry path already exists, cannot restore (force required): '{entry_path}'"
                )

        move(self.store_path.joinpath(name), entry_path)

        self.config.remove(name)
        self.config.save(self.config_path)

    def store(self, name: str, source_path: str) -> None:
        """
        Move the source path to the store path, create a symlink, and update the config

        Args:
            name: The name of the entry
            source_path: The directory or file to be stored

        Returns:
            None
        """
        if self.config.entries.get(name):
            raise TransposeError(
                f"Entry already exists: {name} -> {self.config.entries[name].path}"
            )

        storage_path = self.store_path.joinpath(name)
        if storage_path.exists():
            raise TransposeError(f"Store path already exists: '{storage_path}'")

        source_path = Path(source_path)
        if not source_path.exists():
            raise TransposeError(f"Source path does not exist: '{source_path}'")

        move(source=source_path, destination=storage_path)
        symlink(target_path=storage_path, symlink_path=source_path)

        self.config.add(name, source_path)
        self.config.save(self.config_path)
