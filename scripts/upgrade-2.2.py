"""
Loop through entries and ensure using the latest 2.2 entities

This means adding the following new fields to each entry:
    * created (2.1)
    * enabled (2.2)
"""
import json

from transpose import DEFAULT_STORE_PATH, TransposeConfig


def main() -> None:
    config_file = f"{DEFAULT_STORE_PATH}/transpose.json"
    with open(config_file, "r") as f:
        d = json.load(f)

    config = TransposeConfig()
    for entry_name in d["entries"]:
        config.add(entry_name, d["entries"][entry_name]["path"])

    config.save(config_file)


if __name__ == "__main__":
    main()
