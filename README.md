[![pre-commit](https://github.com/finsberg/pygscholar/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/finsberg/pygscholar/actions/workflows/pre-commit.yml)
[![PyPI version](https://badge.fury.io/py/pygscholar.svg)](https://badge.fury.io/py/pygscholar)
[![CI](https://github.com/finsberg/pygscholar/actions/workflows/main.yml/badge.svg)](https://github.com/finsberg/pygscholar/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/finsberg/pygscholar/branch/main/graph/badge.svg?token=IUZ9HMIBFA)](https://codecov.io/gh/finsberg/pygscholar)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
# pygcholar

Tool for working extracting statistics from Google scholar built upon [`scholarly`](https://scholarly.readthedocs.io)

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

Once installed you should get access to the `scholar` command
```
$ scholar --help

 Usage: scholar [OPTIONS] COMMAND [ARGS]...

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --version                                            Show version            │
│ --license                                            Show license            │
│ --install-completion        [bash|zsh|fish|powershe  Install completion for  │
│                             ll|pwsh]                 the specified shell.    │
│                                                      [default: None]         │
│ --show-completion           [bash|zsh|fish|powershe  Show completion for the │
│                             ll|pwsh]                 specified shell, to     │
│                                                      copy it or customize    │
│                                                      the installation.       │
│                                                      [default: None]         │
│ --help                                               Show this message and   │
│                                                      exit.                   │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ add-author                       Add new author                              │
│ list-author-publications         List authors publications                   │
│ list-authors                     List all authors                            │
│ list-department-publications     List department publications                │
│ list-new-dep-publications        List new publications for the department    │
│ post-slack-new-dep-publications  Post new publications for the department to │
│                                  Slack                                       │
│ remove-author                    Remove author                               │
│ search-author                    Search for authors                          │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## Simple example

List authors
```
$ scholar list-authors
       Authors
┏━━━━━━┳━━━━━━━━━━━━┓
┃ Name ┃ Scholar ID ┃
┡━━━━━━╇━━━━━━━━━━━━┩
└──────┴────────────┘
```

Add author
```
$ scholar add-author 'Henrik Finsberg'
2022-12-30 21:47:29 [info     ] Get author info for Henrik Finsberg
Successfully added author with name Henrik Nicolay Finsberg and scholar id NDPIHoEAAAAJ
```

List authors again
```
$ scholar list-authors
Henrik Nicolay Finsberg
                 Authors
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃                    Name ┃ Scholar ID   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ Henrik Nicolay Finsberg │ NDPIHoEAAAAJ │
└─────────────────────────┴──────────────┘
```

Get the top three most cited papers
```
$ cholar list-author-publications 'Henrik Finsberg' --n=3
Could not find author with name 'Henrik Finsberg'. Will use 'Henrik Nicolay Finsberg' instead
2022-12-30 21:50:21 [info     ] Get author info for Henrik Nicolay Finsberg
         Publications for Henrik Nicolay Finsberg (Sorted by citations)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Title                                 ┃ Published year ┃ Number of citations ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ Efficient estimation of personalized  │ 2018           │ 33                  │
│ biventricular mechanical function     │                │                     │
│ employing gradient‐based optimization │                │                     │
│ Improved computational identification │ 2020           │ 31                  │
│ of drug response using optical        │                │                     │
│ measurements of human stem cell       │                │                     │
│ derived cardiomyocytes in             │                │                     │
│ microphysiological systems            │                │                     │
│ Estimating cardiac contraction        │ 2018           │ 23                  │
│ through high resolution data          │                │                     │
│ assimilation of a personalized        │                │                     │
│ mechanical model                      │                │                     │
└───────────────────────────────────────┴────────────────┴─────────────────────┘
```

Get the top three most cited papers not older than 2 years
```
$ scholar list-author-publications 'Henrik Finsberg' --n=3 --max-age=2
Could not find author with name 'Henrik Finsberg'. Will use 'Henrik Nicolay Finsberg' instead
2022-12-30 21:51:16 [info     ] Get author info for Henrik Nicolay Finsberg
         Publications for Henrik Nicolay Finsberg (Sorted by citations)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Title                                 ┃ Published year ┃ Number of citations ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ Improved computational identification │ 2020           │ 31                  │
│ of drug response using optical        │                │                     │
│ measurements of human stem cell       │                │                     │
│ derived cardiomyocytes in             │                │                     │
│ microphysiological systems            │                │                     │
│ In vitro safety “clinical trial” of   │ 2021           │ 8                   │
│ the cardiac liability of drug         │                │                     │
│ polytherapy                           │                │                     │
│ Heart muscle microphysiological       │ 2021           │ 7                   │
│ system for cardiac liability          │                │                     │
│ prediction of repurposed COVID-19     │                │                     │
│ therapeutics                          │                │                     │
└───────────────────────────────────────┴────────────────┴─────────────────────┘
```


## Contributing
See https://finsberg.github.io/pygscholar/CONTRIBUTING.html

## License
MIT
