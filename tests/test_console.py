import pytest

from transpose.console import parse_arguments


def test_parse_arguments():
    with pytest.raises(SystemExit):  # Missing required args: action
        parse_arguments()

    args = parse_arguments(
        [
            "--store-path",
            "/mnt/store",
            "store",
            "/tmp/some/path",
            "MyTarget",
        ]
    )
    assert args.store_path == "/mnt/store"


def test_parse_arguments_apply():
    with pytest.raises(SystemExit):  # Missing required args: name
        args = parse_arguments(["apply"])

    args = parse_arguments(["apply", "SomeName"])
    assert args.action == "apply"
    assert args.name == "SomeName"
    assert args.force is False

    args = parse_arguments(["apply", "SomeName", "--force"])
    assert args.force is True


def test_parse_arguments_config():
    with pytest.raises(SystemExit):  # Missing required args: config_action
        parse_arguments(["config"])


def test_parse_arguments_config_add():
    with pytest.raises(SystemExit):  # Missing required args: name, path
        args = parse_arguments(["config", "add"])

    with pytest.raises(SystemExit):  # Missing required args: path
        args = parse_arguments(["config", "add", "SomeName"])

    args = parse_arguments(["config", "add", "SomeName", "/var/tmp/something"])
    assert args.config_action == "add"
    assert args.name == "SomeName"
    assert args.path == "/var/tmp/something"


def test_parse_arguments_config_get():
    with pytest.raises(SystemExit):  # Missing required args: name
        args = parse_arguments(["config", "get"])

    args = parse_arguments(["config", "get", "SomeName"])
    assert args.config_action == "get"
    assert args.name == "SomeName"


def test_parse_arguments_config_list():
    args = parse_arguments(["config", "list"])
    assert args.config_action == "list"


def test_parse_arguments_config_remove():
    with pytest.raises(SystemExit):  # Missing required args: name
        args = parse_arguments(["config", "remove"])

    args = parse_arguments(["config", "remove", "SomeName"])
    assert args.config_action == "remove"
    assert args.name == "SomeName"


def test_parse_arguments_store():
    with pytest.raises(SystemExit):  # Missing required args: target_path
        args = parse_arguments(["store"])

    args = parse_arguments(["store", "/tmp/some/path"])
    assert args.name is None

    args = parse_arguments(["store", "/tmp/some/path", "My Name"])
    assert args.action == "store"
    assert args.name == "My Name"
    assert args.target_path == "/tmp/some/path"


def test_parse_arguments_restore():
    with pytest.raises(SystemExit):  # Missing required args: name
        args = parse_arguments(["restore"])

    args = parse_arguments(["restore", "SomeName"])
    assert args.action == "restore"
    assert args.name == "SomeName"

    args = parse_arguments(["restore", "SomeName", "--force"])
    assert args.force is True
