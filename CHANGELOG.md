# Change Log

## 1.1.0 (2022-07-26)

### Breaking Changes
* Moving store_path to only the store action

Note: I know I said this shouldn't happen again but I couldn't help myself. This time....for sure.

### Features
* Allow for short -s for --store-path

### Documentation
* Add Quick Reference section

### Tests
* Updating tests to support moving store_path to store action


## 1.0.2 (2022-07-17)

### Added
* The `name` argument is now optional when using the `transpose store`

### Changed
* Moved `name` argument to end of `transpose store`

Note: I'm abusing the versioning a bit as I'm the only user of this tool. Normally, this would be considered a breaking change due to the change in argument order. Shouldn't happen again.


## 1.0.1 (2022-07-16)

### Fixed

* Utilize `expanduser` and `~` in cache files to allow for more portable restorations


## 1.0.0 (2022-07-12)

Initial release
