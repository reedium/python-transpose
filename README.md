# Transpose

A tool for moving and symlinking directories to a central location


## Introduction

I've been using linux as my main machine for a while and wanted a central directory to backup as backing up my entire `HOME` directory was a mess. I found moving directories and symlinking worked great. I created a simple project when learning python (I called symlinker) and used it for a while but found it annoying to configure and work with.

I recently found I could use a tool like this for a SteamDeck and decided to start from scratch with better code and easier to use.

This is the current result, although it still needs a lot of work as I'm sure I'm not doing things particularly well.


## Installation

Can be installed via pip. For instance, from within a virtualenv:

```
python -m venv .venv
. .venv/bin/activate
pip install .
```


## Configuration

There are a few environment variables that can be defined to override defaults

```
TRANSPOSE_STORE_PATH="$XDG_DATA_HOME/transpose"
TRANSPOSE_CACHE_FILENAME=".transpose.json"
```


## Usage

### Storing a Directory

Storing a directory will:

1. Move a `target` to `$STORE_PATH/{name}`
2. Symlink `target` to `$STORE_PATH/{name}`
3. Create a cache file at `$STORE_PATH/{name}/.transpose.json` to store the original target path

```
transpose store "My Documents" /home/user/Documents
```

The above will (assuming using all the defaults):

1. Move `/home/user/Documents` to `$XDG_DATA_HOME/transpose/My Documents`
2. Symlink `/home/user/Documents` to `$XDG_DATA_HOME/transpose/My Documents`



### Restoring a Store Directory

Restoring a directory will:

1. Remove the old symlink in the `original_path` of the cache file, `$STORE_PATH/{name}/.transpose.json`
2. Move the stored directory to the `original_path`

```
transpose restore "$XDG_DATA_HOME/transpose/My Documents"
```

The above will (assuming all the defaults):

1. Remove the symlink at `/home/user/Documents` (from cache file)
2. Move `$XDG_DATA_HOME/transpose/My Documents` to `/home/user/Documents`
