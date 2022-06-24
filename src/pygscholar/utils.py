from __future__ import annotations

import json
from pathlib import Path


def load_json(fname):

    d = {}
    if Path(fname).is_file():
        with open(fname, "r") as f:
            d = json.load(f)

    return d


def dump_json(data, fname):
    with open(fname, "w") as f:
        json.dump(data, f, indent=2)
