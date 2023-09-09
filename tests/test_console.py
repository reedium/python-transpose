import pytest

from pathlib import Path

from transpose import TransposeConfig
from transpose.console import parse_arguments, run as run_console

from .utils import (
    setup_restore,
    setup_store,
    setup_apply,
    STORE_PATH,
    TARGET_PATH,
    TRANSPOSE_CONFIG_PATH,
)


class RunArgs:
    name: str = "MyName"
    action: str = "config"
    forced: bool = False
    path: str = str(TARGET_PATH)
    config_action: str

    def __init__(self, config_action: str) -> None:
        self.config_action = config_action


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


def test_run_apply():
    pass


def test_run_restore():
    pass


def test_run_store():
    pass


@setup_restore()
def test_run_config_add():
    args = RunArgs("add")
    args.name = "MyName2"

    run_console(args, TRANSPOSE_CONFIG_PATH)
    config = TransposeConfig().load(TRANSPOSE_CONFIG_PATH)

    assert config.entries.get(args.name)


@setup_restore()
def test_run_config_get(capsys):
    args = RunArgs("get")

    run_console(args, TRANSPOSE_CONFIG_PATH)
    captured = capsys.readouterr()

    assert str(TARGET_PATH) in captured.out


@setup_restore()
def test_run_config_list(capsys):
    args = RunArgs("list")

    run_console(args, TRANSPOSE_CONFIG_PATH)
    captured = capsys.readouterr()

    assert f"-> {TARGET_PATH}" in captured.out


@setup_restore()
def test_run_config_remove():
    args = RunArgs("remove")

    run_console(args, TRANSPOSE_CONFIG_PATH)
    config = TransposeConfig().load(TRANSPOSE_CONFIG_PATH)

    assert not config.entries.get(args.name)


@setup_restore()
def test_run_config_update():
    args = RunArgs("update")
    args.path = "/var/tmp/something"

    run_console(args, TRANSPOSE_CONFIG_PATH)
    config = TransposeConfig().load(TRANSPOSE_CONFIG_PATH)

    assert config.entries[args.name].path == args.path
