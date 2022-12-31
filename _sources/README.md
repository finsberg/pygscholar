[![pre-commit](https://github.com/finsberg/pygscholar/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/finsberg/pygscholar/actions/workflows/pre-commit.yml)
[![PyPI version](https://badge.fury.io/py/pygscholar.svg)](https://badge.fury.io/py/pygscholar)
[![CI](https://github.com/finsberg/pygscholar/actions/workflows/main.yml/badge.svg)](https://github.com/finsberg/pygscholar/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/finsberg/pygscholar/branch/main/graph/badge.svg?token=IUZ9HMIBFA)](https://codecov.io/gh/finsberg/pygscholar)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
# pygcholar

Tool for extracting statistics from Google scholar built upon [`scholarly`](https://scholarly.readthedocs.io)

Imagine you have a department full of researchers and you want to keep track of the most recent or most cited papers in the department, or that you simply want to track yourself, then this package might be what you need.

- Documentation: https://finsberg.github.io/pygscholar
- Source code: https://github.com/finsberg/pygscholar

## Install
`pygscolar` is primarily a command line tool which makes it very suitable to install with [`pipx`](https://pypa.github.io/pipx/)
```
pipx install pygscholar
```

You can of course also install it with regular `pip`
```
python -m pip install pygscholar
```

Once installed you should get access to the `scholar` command. See [the tutorial](https://finsberg.github.io/pygscholar/docs/tutorial.html) for a guide on how to use this command.


## Contributing
See https://finsberg.github.io/pygscholar/docs/CONTRIBUTING.html

## License
MIT
