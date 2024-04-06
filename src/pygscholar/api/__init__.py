from enum import Enum


from ..author import AuthorInfo, Author
from . import scholarly
from . import scraper

__all__ = ["search_author"]


class APIBackend(str, Enum):
    SCRAPER = "scraper"
    SCHOLARLY = "scholarly"


def search_author(
    name: str, backend: APIBackend = APIBackend.SCRAPER, scholar_id: str = ""
) -> list[AuthorInfo]:
    if backend == APIBackend.SCRAPER:
        authors = scraper.search_author(name)
    elif backend == APIBackend.SCHOLARLY:
        authors = scholarly.search_author(name)
    else:
        raise ValueError(f"Unknown backend {backend}")

    if scholar_id == "":
        return authors

    authors = [author for author in authors if author.scholar_id == scholar_id]
    return authors


def search_author_with_publications(
    name: str,
    scholar_id: str,
    full: bool = False,
    backend: APIBackend = APIBackend.SCRAPER,
) -> Author:
    if backend == APIBackend.SCRAPER:
        author = scraper.search_author_with_publications(
            name,
            scholar_id,
            full=full,
        )
    elif backend == APIBackend.SCHOLARLY:
        author = scholarly.search_author_with_publications(
            name,
            scholar_id,
            full=full,
        )
    else:
        raise ValueError(f"Unknown backend {backend}")

    return author
