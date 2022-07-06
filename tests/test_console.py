import pytest

from transpose.console import parse_arguments


def test_parse_arguments():
    # Missing required argument - action
    with pytest.raises(SystemExit):
        parse_arguments()

    args = parse_arguments(
        [
            "store",
            "--cache-filename",
            "test-cache-file.json",
            "--store-path",
            "/mnt/store",
            "MyTarget",
            "/tmp/some/path",
        ]
    )
    assert args.cache_filename == "test-cache-file.json"
    assert args.store_path == "/mnt/store"


def test_parse_arguments_apply():
    # Missing required argument - target_path (Apply)
    with pytest.raises(SystemExit):
        args = parse_arguments(["apply"])

    args = parse_arguments(["apply", "/tmp/some/path"])
    assert args.action == "apply"
    assert args.target_path == "/tmp/some/path"


def test_parse_arguments_store():
    # Missing required argument - name (Store)
    with pytest.raises(SystemExit):
        args = parse_arguments(["store"])

    # Missing required argument - target_path (Store)
    with pytest.raises(SystemExit):
        args = parse_arguments(["store", "My Name"])

    args = parse_arguments(["store", "My Name", "/tmp/some/path"])
    assert args.action == "store"
    assert args.name == "My Name"
    assert args.target_path == "/tmp/some/path"


def test_parse_arguments_restore():
    # Missing required argument - target_path (Restore)
    with pytest.raises(SystemExit):
        args = parse_arguments(["restore"])

    args = parse_arguments(["restore", "/tmp/some/path"])
    assert args.action == "restore"
    assert args.target_path == "/tmp/some/path"
