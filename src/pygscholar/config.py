import os
from pathlib import Path

DEFAULT_CACHE_DIR = os.getenv(
    "PYSCHOLAR_CACHE_DIR",
    Path.home().joinpath(".pygscholar").as_posix(),
)
CONFIG_PATH = os.getenv("PYSCHOLAR_CONFIG_PATH", (Path.home() / ".pygscholarrc").as_posix())
