# Python Hardware Wrappers

[![Build Status](https://travis-ci.org/jondoesntgit/hardware.svg?branch=master)](https://travis-ci.org/jondoesntgit/hardware)
[![Codecov](https://img.shields.io/codecov/c/github/jondoesntgit/hardware.svg)](https://codecov.io/gh/jondoesntgit/hardware)

This repository contains python wrappers that can be used to access hardware
commonly used inside of the Digonnet lab at Stanford. For more documentation,
visit [http://github.jamwheeler.com/hardware](http://github.jamwheeler.com/hardware)

This changelog follows the recommendations put forth at [keepachangelong.com](http://keepachangelog.com/en/0.3.0/)

## [0.3.0] - [2018-07-12]
### Added
- [Travis](https://travis-ci.org/) integration
- Code coverage integration through [codecov.io](https://codecov.io/)
- A test suite has been added. These tests are run via [pytest](https://docs.pytest.org/en/latest/). A few of these test cases haven't been properly implemented for the various
instruments, and Travis really can't handle any of the test cases yet.
- A windows [makefile](https://en.wikipedia.org/wiki/Makefile) has been created,
that can be run via `make help`, `make test`, `make upload`, etc...
- Units, provided via [pint](http://pint.readthedocs.io/en/latest/), are now
widely implemented in the repository. There are still a few places that they
haven't reached, but these will require some overhauling in the future.
- Most classes now provide automatic logging when parameters are changed.

## [0.2.0] - [2018-01-23]
### Added
- Gyro objects now can have their properties accessed as if they were a dictionary. For example: `fog['name']`, `fog['pitch']`.
- Gyro objects can be autoloaded from the `__init__.py` script by setting an environment variable `DEFAULT_GYRO`, which contains the absolute path to the desired gyros JSON file.
- Gyros objects can now be returned via the `__repr__` function in `print(fog)`. This will be handy when showing them in a `Tombstone` object.

### Changed
- Gyro scale factor code now uses sensitivity and pitch from either parameter arguments or JSON file values.

## [0.1.0] - [2017-12-10]

This version merely contains all of the code developed up until this point.
