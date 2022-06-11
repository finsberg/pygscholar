from . import author
from . import department
from . import publication
from . import scholar_api
from . import utils
from .author import Author
from .department import Department
from .publication import FullPublication
from .publication import Publication

try:
    from importlib.metadata import metadata
except ImportError:
    # python3.7 backport
    from importlib_metadata import metadata  # type: ignore

meta = metadata("pyscholar")
__version__ = meta["Version"]
__author__ = meta["Author"]
__license__ = meta["License"]
__email__ = meta["Author-email"]
__program_name__ = meta["Name"]


__all__ = [
    "Author",
    "Publication",
    "FullPublication",
    "Department",
    "author",
    "publication",
    "department",
    "scholar_api",
    "utils",
]
