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
transpose store   ~/.config/zsh                 # Move ~/.config/zsh -> ~/.local/share/transpose/zsh, create symlink, create cache
transpose restore ~/.local/share/transpose/zsh  # Remove symlink, move ~/.local/share/transpose/zsh -> ~/.config/zsh, remove cache
transpose apply   ~/.local/share/transpose/zsh  # Recreate symlink in cache location
transpose create  ~/.config/zsh ~/.local/share/transpose/zsh  # Recreate cache file

transpose store ~/.config/zsh zsh_config -s /mnt/backups    # Move ~/.config/zsh -> /mnt/backups/zsh_config, create symlink, create cache
transpose --cache-filename .mycache.json restore /mnt/backups/zsh_config  # Use /mnt/backup/.zsh_config.json for restoring a stored directory
```


## Usage

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
transpose restore "/home/user/.local/share/transpose/My Documents"
```

The above will (assuming all the defaults):

1. Remove the symlink at `/home/user/Documents` (from cache file)
2. Move `$XDG_DATA_HOME/transpose/My Documents` to `/home/user/Documents`


### Applying a Previously Transpose Managed Directory

This will recreate the symlink based on the cache file within the directory.

This is most useful when moving the stored directory.

```
transpose apple "/home/user/.local/share/transpose/My Documents"
```
