import json
import pathlib
import pytest

from transpose import Transpose, TransposeConfig, TransposeEntry
from transpose.exceptions import TransposeError

from .utils import (
    ENTRY_NAME,
    ENTRY_STORE_PATH,
    STORE_PATH,
    TARGET_PATH,
    TRANSPOSE_CONFIG,
    TRANSPOSE_CONFIG_PATH,
    setup_restore,
    setup_store,
    setup_apply,
)


@setup_store()
def test_init():
    t = Transpose(config_path=TRANSPOSE_CONFIG_PATH)
    assert t.config.entries.get(ENTRY_NAME)
    assert t.config_path == TRANSPOSE_CONFIG_PATH
    assert t.store_path == TRANSPOSE_CONFIG_PATH.parent


@setup_apply()
def test_apply():
    t = Transpose(config_path=TRANSPOSE_CONFIG_PATH)

    # Success
    t.apply(ENTRY_NAME)
    assert TARGET_PATH.is_symlink()
    assert ENTRY_STORE_PATH.is_dir()

    with pytest.raises(TransposeError, match="Entry does not exist"):
        t.apply("BadName")

    # Target already exists, force not set
    TARGET_PATH.unlink()
    TARGET_PATH.mkdir()
    with pytest.raises(TransposeError, match="Entry path already exists"):
        t.apply(ENTRY_NAME)

    # Target already exists, force set (Create backup of original path)
    t.apply(ENTRY_NAME, force=True)
    backup_path = TARGET_PATH.with_suffix(".backup")

    assert backup_path.is_dir()
    assert TARGET_PATH.is_symlink()
    assert ENTRY_STORE_PATH.is_dir()

    # Target is disabled in the config
    t.config.entries[ENTRY_NAME].enabled = False
    with pytest.raises(
        TransposeError, match=f"Entry '{ENTRY_NAME}' is not enabled in the config"
    ):
        t.apply(ENTRY_NAME)


@setup_restore()
def test_restore():
    t = Transpose(config_path=TRANSPOSE_CONFIG_PATH)

    # Target is disabled in the config
    t.config.entries[ENTRY_NAME].enabled = False
    with pytest.raises(
        TransposeError, match=f"Entry '{ENTRY_NAME}' is not enabled in the config"
    ):
        t.restore(ENTRY_NAME)
    t.config.entries[ENTRY_NAME].enabled = True

    # Success
    t.restore(ENTRY_NAME)
    assert TARGET_PATH.is_dir()
    assert not TARGET_PATH.is_symlink()
    assert not ENTRY_STORE_PATH.exists()

    with pytest.raises(TransposeError, match="Could not locate entry by name"):
        t.restore("BadName")


@setup_restore()
def test_restore_path_conflicts():
    t = Transpose(config_path=TRANSPOSE_CONFIG_PATH)

    # Target already exists, force not set
    TARGET_PATH.mkdir()
    with pytest.raises(TransposeError, match="Entry path already exists"):
        t.restore(ENTRY_NAME)

    t.restore(ENTRY_NAME, force=True)
    backup_path = TARGET_PATH.with_suffix(".backup")

    assert backup_path.is_dir()
    assert TARGET_PATH.is_dir()
    assert not TARGET_PATH.is_symlink()
    assert not ENTRY_STORE_PATH.exists()
    assert not t.config.entries.get(ENTRY_NAME)


@setup_store()
def test_store():
    t = Transpose(config_path=TRANSPOSE_CONFIG_PATH)

    # Success
    t.store("TestEntry", TARGET_PATH)
    assert TARGET_PATH.is_symlink()
    assert STORE_PATH.joinpath("TestEntry").is_dir()
    assert t.config.entries["TestEntry"].path == str(TARGET_PATH)


@setup_store()
def test_store_conflicts():
    t = Transpose(config_path=TRANSPOSE_CONFIG_PATH)

    with pytest.raises(TransposeError, match="Entry already exists"):
        t.store(ENTRY_NAME, TARGET_PATH)

    with pytest.raises(TransposeError, match="Source path does not exist"):
        t.store("TestEntry", "UnknownPath/")

    STORE_PATH.joinpath("TestEntry").mkdir()
    with pytest.raises(TransposeError, match="Store path already exists"):
        t.store("TestEntry", TARGET_PATH)
    STORE_PATH.joinpath("TestEntry").rmdir()


@setup_store()
def test_config_add():
    config = TransposeConfig.load(TRANSPOSE_CONFIG_PATH)

    with pytest.raises(TransposeError, match=f"'{ENTRY_NAME}' already exists"):
        config.add(ENTRY_NAME, TARGET_PATH)

    config.add("NewEntry", TARGET_PATH)
    assert config.entries.get("NewEntry")
    assert config.entries["NewEntry"].path == str(TARGET_PATH)


@setup_store()
def test_config_disable():
    config = TransposeConfig.load(TRANSPOSE_CONFIG_PATH)

    with pytest.raises(TransposeError, match="'UnknownEntry' does not exist"):
        config.disable("UnknownEntry")

    config.disable(ENTRY_NAME)
    assert config.entries[ENTRY_NAME].enabled is False


@setup_store()
def test_config_enable():
    config = TransposeConfig.load(TRANSPOSE_CONFIG_PATH)

    with pytest.raises(TransposeError, match="'UnknownEntry' does not exist"):
        config.enable("UnknownEntry")

    config.enable(ENTRY_NAME)
    assert config.entries[ENTRY_NAME].enabled is True


@setup_store()
def test_config_get():
    config = TransposeConfig.load(TRANSPOSE_CONFIG_PATH)

    with pytest.raises(
        TransposeError, match="does not exist in Transpose config entries"
    ):
        config.get("UnknownEntry")

    assert config.get(ENTRY_NAME).path == str(TARGET_PATH)


@setup_store()
def test_config_remove():
    config = TransposeConfig.load(TRANSPOSE_CONFIG_PATH)

    with pytest.raises(
        TransposeError, match="does not exist in Transpose config entries"
    ):
        config.remove("UnknownEntry")

    config.remove(ENTRY_NAME)
    assert not config.entries.get(ENTRY_NAME)


@setup_store()
def test_config_update():
    config = TransposeConfig.load(TRANSPOSE_CONFIG_PATH)

    with pytest.raises(
        TransposeError, match="does not exist in Transpose config entries"
    ):
        config.update("UnknownEntry", "path", "/some/new/path")

    with pytest.raises(TransposeError, match="Unknown TransposeEntry field"):
        config.update(ENTRY_NAME, "UnknownField", "Some Value")

    config.update(ENTRY_NAME, "path", "/some/new/path")
    assert config.entries[ENTRY_NAME].path == "/some/new/path"


@setup_store()
def test_config_save():
    config = TransposeConfig.load(TRANSPOSE_CONFIG_PATH)
    config.save(STORE_PATH.joinpath("test.json"))

    with open(STORE_PATH.joinpath("test.json"), "r") as f:
        saved_config = json.load(f)

    assert (
        config.entries[ENTRY_NAME].path == saved_config["entries"][ENTRY_NAME]["path"]
    )


@setup_store()
def test_config_save_fresh():
    """
    Verify creation of transpose config when doesn't initially exist
    """
    TRANSPOSE_CONFIG_PATH.unlink()
    config = TransposeConfig.load(TRANSPOSE_CONFIG_PATH)
    assert len(config.entries) == 0

    config.add("TestEntry", TARGET_PATH)
    config.save(TRANSPOSE_CONFIG_PATH)

    config = TransposeConfig.load(TRANSPOSE_CONFIG_PATH)
    assert config.entries.get("TestEntry")


@setup_store()
def test_config_load():
    config = TransposeConfig.load(TRANSPOSE_CONFIG_PATH)

    assert config.entries.get(ENTRY_NAME)
    assert (
        config.entries[ENTRY_NAME].path
        == TRANSPOSE_CONFIG["entries"][ENTRY_NAME]["path"]
    )

    with pytest.raises(
        TransposeError, match="Unrecognized Transpose config file format"
    ):
        config = TransposeConfig.load(STORE_PATH.joinpath("transpose-bad.json"))

    with pytest.raises(TransposeError, match="Invalid JSON format"):
        config = TransposeConfig.load(STORE_PATH.joinpath("transpose-invalid.json"))
