# Transpose

A tool for moving and symlinking directories to a central location


## Table of Contents

<!-- vim-markdown-toc GFM -->

* [Introduction](#introduction)
* [Installation](#installation)
* [Quick Reference](#quick-reference)
* [Usage](#usage)
    * [Storing a Directory](#storing-a-directory)
    * [Restoring a Stored Directory](#restoring-a-stored-directory)
    * [Applying a Previously Transpose Managed Directory](#applying-a-previously-transpose-managed-directory)
    * [Modifying Transpose Config Directly](#modifying-transpose-config-directly)
* [Development](#development)

<!-- vim-markdown-toc -->


## Introduction

I've been using linux as my main machine for a while and wanted a central directory to backup as backing up my entire `HOME` directory was a mess. I found moving directories and symlinking worked great. I created a simple project when learning python (I called symlinker) and used it for a while but found it annoying to configure and work with.

I recently found I could use a tool like this for a SteamDeck and decided to start from scratch with better code and easier to use.

This is the current result, although it still needs a lot of work as I'm sure I'm not doing things particularly well.

Additionally, the name `transpose` was sort of chosen at random and has no particular meaning currently. I'd like to change it in the future but haven't really come up with any suitable replacement.



## Installation

Can be installed via pip. For instance, from within a virtualenv:

```
python -m venv .venv
. .venv/bin/activate
pip install .
```


## Quick Reference

```
transpose store ~/.config/zsh                   # Move ~/.config/zsh -> ~/.local/share/transpose/zsh, create symlink, create cache
transpose restore zsh                           # Remove symlink, move ~/.local/share/transpose/zsh_config -> ~/.config/zsh, remove cache
transpose apply zsh                             # Recreate symlink in store path (useful after moving Store Path location)

transpose store -s /mnt/backups ~/.config/zsh zsh_config    # Move ~/.config/zsh -> /mnt/backups/zsh_config, create symlink
```


## Usage

See `transpose --help` for more information on each comment


### Storing a Directory

Storing a directory will:

1. Move a `target` to `$STORE_PATH/{name}`
2. Symlink `target` to `$STORE_PATH/{name}`
3. Create a cache file at `$STORE_PATH/{name}/.transpose.json` to store the original target path

```
transpose store /home/user/Documents "My Documents"
```

The above will (assuming using all the defaults):

1. Move `/home/user/Documents` to `$XDG_DATA_HOME/transpose/My Documents`
2. Symlink `/home/user/Documents` to `$XDG_DATA_HOME/transpose/My Documents`

Note: The name on the end (`My Documents` above), can be ommitted. The stored name will use the target name (e.g. `Documents` above)


### Restoring a Stored Directory

Restoring a directory will:

1. Remove the old symlink in the `original_path` of the cache file, `$STORE_PATH/{name}/.transpose.json`
2. Move the stored directory to the `original_path`

```
transpose restore Game1
```

The above will (assuming all the defaults):

1. Remove the symlink at `/home/user/Documents/games/MyGame` (from settings file)
2. Move `$XDG_DATA_HOME/transpose/Game1` to `/home/user/Documents/games/MyGame`


### Applying a Previously Transpose Managed Directory

This will recreate the symlink based on the config file within the directory.

This is most useful when moving the stored directory.

```
transpose apply "Game1"
```


### Modifying Transpose Config Directly

It's possible to modify the transpose configuration file, `STORE_PATH/transpose.json`, using the console:

```
transpose config add "NewEntry" "/path/to/location"
transpose config get "NewEntry"
transpose config disable "NewEntry"
transpose config enable "NewEntry"
transpose config list
transpose config remove "NewEntry"
transpose config update "NewEntry" "path" "/path/to/new/location"
```


## Development

```
poetry install
poetry add --dev black
poetry update # Only to update to latest versions, update poetry.lock

poetry run python src/transpose/console.py
poetry run pytest --cov=transpose --cov-report html tests

poetry shell
```
