from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

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


def get_publications(args):
    name, scholar_id = args
    logger.info(f"Get publication for {name} with id {scholar_id}")
    query = scholarly.search_author(name)
    for item in query:
        if item["scholar_id"] == scholar_id:

            info = scholarly.fill(item)
            return name, scholar_id, info["publications"]
    return name, scholar_id, []


def extract_scholar_publications(people):

    people_with_scholar_id = {
        name: scholar_id for name, scholar_id in people.items() if scholar_id != ""
    }
    authors = []
    with ThreadPoolExecutor() as executor:
        for name, scholar_id, info in executor.map(
            get_publications,
            people_with_scholar_id.items(),
        ):
            authors.append(Author(name=name, scholar_id=scholar_id, publications=info))

    return Department(authors=authors)
