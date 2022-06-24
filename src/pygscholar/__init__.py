from importlib.metadata import metadata

from . import author
from . import department
from . import publication
from . import scholar_api
from . import utils
from .author import Author
from .department import Department
from .publication import FullPublication
from .publication import Publication

meta = metadata("pygscholar")
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
