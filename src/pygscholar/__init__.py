from importlib.metadata import metadata

from . import author
from . import department
from . import publication
from . import config
from . import api
from . import cache
from .author import Author, AuthorInfo
from .department import Department

# from .publication import FullPublication
from .publication import Publication

meta = metadata("pygscholar")
__version__ = meta["Version"]
__author__ = meta["Author-email"]
__license__ = meta["License"]
__email__ = meta["Author-email"]
__program_name__ = meta["Name"]


__all__ = [
    "Author",
    "Publication",
    "AuthorInfo",
    "Department",
    "author",
    "publication",
    "department",
    "utils",
    "config",
    "api",
    "cache",
]
