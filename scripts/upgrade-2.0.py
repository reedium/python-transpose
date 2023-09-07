"""
Loops through STORE_PATH, looking for */.transpose files, create new transpose config file

    Note: This does not remove the v1 */.transpose files, just in case. Must be done if desired.
"""
from pathlib import Path

import json

from transpose import TransposeConfig, DEFAULT_STORE_PATH


def main() -> None:
    store_path = Path(DEFAULT_STORE_PATH)

    config = TransposeConfig()

    entries = store_path.glob("*/*.transpose.json")
    for entry in entries:
        with open(entry, "r") as f:
            d = json.load(f)
            config.add(Path(entry).parent.parts[-1], d["original_path"])

    config.save(store_path.joinpath("transpose.json"))


if __name__ == "__main__":
    main()
