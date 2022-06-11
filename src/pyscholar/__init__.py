from importlib.metadata import version as _version

from . import author
from . import department
from . import publication
from . import scholar_api
from . import utils
from .author import Author
from .department import Department
from .publication import FullPublication
from .publication import Publication

__version__ = _version("pyscholar")

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
