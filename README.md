# Python Hardware Wrappers

[![Build Status](https://travis-ci.org/jondoesntgit/hardware.svg?branch=master)](https://travis-ci.org/jondoesntgit/hardware)
[![Codecov](https://img.shields.io/codecov/c/github/jondoesntgit/hardware.svg)](https://codecov.io/gh/jondoesntgit/hardware)

This repository contains python wrappers that can be used to access hardware
commonly used inside of the Digonnet lab at Stanford. For more documentation,
visit [http://github.jamwheeler.com/hardware](http://github.jamwheeler.com/hardware)

This changelog follows the recommendations put forth at [keepachangelong.com](http://keepachangelog.com/en/0.3.0/)

## [Unreleased]
### Added
- Gyro objects now can have their properties accessed as if they were a dictionary. For example: `fog['name']`, `fog['pitch']`.
- Gyro objects can be autoloaded from the `__init__.py` script by setting an environment variable `DEFAULT_GYRO`, which contains the absolute path to the desired gyros JSON file.
- Gyros objects can now be returned via the `__repr__` function in `print(fog)`. This will be handy when showing them in a `Tombstone` object.

### Changed
- Gyro scale factor code now uses sensitivity and pitch from either parameter arguments or JSON file values.

### FAQ
- When passing values to setter functions, the units must be specified. Units must come from the same pint.UnitRegistry() as that used by hardware

## [0.1.0] - [2017-12-10]

This version merely contains all of the code developed up until this point.
