from __future__ import annotations
import difflib
from typing import Iterable
from typing import Protocol
from typing import Sequence
from enum import Enum

from ..publication import Publication
from ..author import AuthorInfo, Author
from . import scholarly
from . import scraper

__all__ = ["search_author"]


def get_closest_name(name: str, names: Iterable[str]):
    try:
        closest_name = difflib.get_close_matches(name, names)[0]
    except IndexError as e:
        all_names = "\n".join(names)

        raise ValueError(
            f"Unable to find name '{name}'. Possible options are \n{all_names}",
        ) from e
    return closest_name


class PublicationObject(Protocol):
    def topk_cited(self, k: int) -> Sequence[Publication]: ...

    def topk_age(self, k: int) -> Sequence[Publication]: ...

    def topk_cited_not_older_than(self, k: int, age: int) -> Sequence[Publication]: ...

    def topk_age_not_older_than(self, k: int, age: int) -> Sequence[Publication]: ...


def extract_correct_publications(
    obj: PublicationObject,
    sort_by_citations: bool = True,
    max_age: int | None = None,
    n: int = 10,
) -> Sequence[Publication]:
    if sort_by_citations:
        if max_age is None:
            publications = obj.topk_cited(k=n)
        else:
            publications = obj.topk_cited_not_older_than(k=n, age=max_age)
    else:
        if max_age is None:
            publications = obj.topk_age(k=n)
        else:
            publications = obj.topk_age_not_older_than(k=n, age=max_age)

    return publications


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


def fill_publication(
    publication: Publication, backend: APIBackend = APIBackend.SCRAPER
) -> Publication:
    if backend == APIBackend.SCRAPER:
        return scraper.fill_publication(publication)
    elif backend == APIBackend.SCHOLARLY:
        return scholarly.fill_publication(publication)
    else:
        raise ValueError(f"Unknown backend {backend}")
