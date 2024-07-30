from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any
from typing import Dict

from scholarly import scholarly
from structlog import get_logger

from ..author import Author, AuthorInfo
from ..publication import Publication


logger = get_logger()


def to_publication(item: Dict[str, Any], full: bool = False) -> Publication:
    if full:
        item = scholarly.fill(item)
    kwargs = {
        "title": item.get("bib", {}).get("title", ""),
        "year": item.get("bib", {}).get("pub_year", 0),
        "num_citations": item.get("num_citations", 0),
        "abstract": item.get("bib", {}).get("abstract", ""),
        "authors": item.get("bib", {}).get("author", ""),
        "journal": item.get("bib", {}).get("journal", ""),
        "volume": item.get("bib", {}).get("volume", ""),
        "issue": item.get("bib", {}).get("issue", ""),
        "pages": item.get("bib", {}).get("pages", ""),
        "publisher": item.get("bib", {}).get("publisher", ""),
        "pdf_url": item.get("bib", {}).get("pub_url", ""),
    }
    if kwargs["journal"] == "":
        kwargs["journal"] = item.get("bib", {}).get("citation", "")

    return Publication(**kwargs)


def to_author_info(item: Dict[str, Any]) -> AuthorInfo:
    return AuthorInfo(
        name=item.get("name", ""),
        scholar_id=item.get("scholar_id", ""),
        link=item.get("url_picture", ""),
        affiliation=item.get("affiliation", ""),
        email=item.get("email", ""),
        cited_by=item.get("citedby", 0),
        data=item,
    )


def get_author(name: str, scholar_id: str = "") -> AuthorInfo | None:
    logger.info(f"Get author info for {name}")
    authors = search_author(name)

    if len(authors) == 0:
        return None

    if scholar_id == "":
        return authors[0]

    for author in authors:
        if author.scholar_id == scholar_id:
            return author
    return None


def search_author_with_publications(name: str, scholar_id: str = "", full: bool = True) -> Author:
    author = get_author(name, scholar_id)

    if author is None:
        raise RuntimeError(f"Could not find author '{name}' with id '{scholar_id}'")

    author_data = scholarly.fill(author.data)

    results = []
    with ThreadPoolExecutor() as executor:
        for item in author_data["publications"]:
            results.append(executor.submit(to_publication, item, full))

    publications: list[Publication] = [result.result() for result in results]
    return Author(info=author, publications=publications)


# def extract_scholar_publications(people: Dict[str, str]) -> Department:
#     people_with_scholar_id = {
#         name: scholar_id for name, scholar_id in people.items() if scholar_id != ""
#     }
#     authors = []
#     with ThreadPoolExecutor() as executor:
#         for name, scholar_id, info in executor.map(
#             _get_publications,
#             people_with_scholar_id.items(),
#         ):
#             authors.append(Author(name=name, scholar_id=scholar_id, publications=info))

#     return Department(authors=authors)


def fill_publication(publication: Publication) -> Publication:
    try:
        return to_publication(next(scholarly.search_pubs(publication.title)), full=True)
    except StopIteration:
        return publication


def search_author(name: str) -> list[AuthorInfo]:
    query = scholarly.search_author(name)
    authors = []
    for author in query:
        authors.append(to_author_info(author))
    return authors
