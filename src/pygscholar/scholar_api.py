from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any
from typing import Dict

from scholarly import scholarly
from structlog import get_logger

from .author import Author
from .department import Department
from .publication import FullPublication


logger = get_logger()


def find_publicaton(title: str) -> FullPublication:
    query = scholarly.search_pubs(title)
    result = next(query)
    if result["bib"]["title"] != title:
        raise RuntimeError(f"Could not find publication '{title}'")
    result = scholarly.fill(result)
    return FullPublication(**result)


def _get_author(name: str, scholar_id: str = "", fill: bool = True) -> Dict[str, Any]:
    logger.info(f"Get author info for {name}")
    query = scholarly.search_author(name)

    item = None
    if scholar_id != "":
        for item in query:
            if item["scholar_id"] == scholar_id:
                break
    else:
        item = next(query)

    if item is None:
        return {}

    if fill:
        return scholarly.fill(item)
    else:
        return item


def get_author(name: str, scholar_id: str = "", fill: bool = True) -> Author:
    return Author(**_get_author(name, scholar_id=scholar_id, fill=fill))


def _get_author_publications(name: str, scholar_id: str) -> Dict[str, Any]:
    logger.info(f"Get publication for {name} with id {scholar_id}")
    author = _get_author(name, scholar_id=scholar_id)
    return author.get("publications", [])


def _get_publications(args):
    name, scholar_id = args

    publications = _get_author_publications(name, scholar_id=scholar_id)
    return name, scholar_id, publications


def extract_scholar_publications(people: Dict[str, str]) -> Department:

    people_with_scholar_id = {
        name: scholar_id for name, scholar_id in people.items() if scholar_id != ""
    }
    authors = []
    with ThreadPoolExecutor() as executor:
        for name, scholar_id, info in executor.map(
            _get_publications,
            people_with_scholar_id.items(),
        ):
            authors.append(Author(name=name, scholar_id=scholar_id, publications=info))

    return Department(authors=authors)
