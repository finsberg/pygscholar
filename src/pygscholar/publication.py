from __future__ import annotations

import datetime
from functools import reduce
from typing import Sequence

from pydantic import BaseModel, ConfigDict
from structlog import get_logger


logger = get_logger()


class Publication(BaseModel):
    title: str
    year: int = 0
    num_citations: int = 0
    abstract: str = ""
    authors: str = ""
    journal: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    publisher: str = ""
    pdf_url: str = ""
    scholar_url: str = ""
    date: str = ""

    model_config = ConfigDict(frozen=True)

    @property
    def age(self) -> int:
        year = datetime.date.today().year
        return year - self.year

    def fill(self) -> "Publication":
        from .api import fill_publication

        return fill_publication(self)


def remove_duplicate_publications(
    publications: Sequence[Publication],
) -> tuple[Publication, ...]:
    uniqe_publications = []
    titles = []
    for pub in publications:
        if pub.title in titles:
            continue
        titles.append(pub.title)
        uniqe_publications.append(pub)

    return tuple(uniqe_publications)


def most_cited(publications: Sequence[Publication]) -> Publication:
    def func(pub1: Publication, pub2: Publication):
        if pub1.num_citations >= pub2.num_citations:
            return pub1
        return pub2

    return reduce(func, publications)


def topk_cited(publications: Sequence[Publication], k: int) -> tuple[Publication, ...]:
    sorted_publications = tuple(
        reversed(
            sorted(
                remove_duplicate_publications(publications),
                key=lambda p: p.num_citations,
            ),
        ),
    )
    return sorted_publications[:k]


def topk_age(publications: Sequence[Publication], k: int) -> tuple[Publication, ...]:
    publications_with_age = []
    for pub in publications:
        try:
            pub.age
        except ValueError:
            continue
        else:
            publications_with_age.append(pub)

    sorted_publications = tuple(
        sorted(
            remove_duplicate_publications(publications_with_age),
            key=lambda p: p.age,
        ),
    )
    return sorted_publications[:k]


def publications_not_older_than(
    publications: Sequence[Publication],
    age: int,
) -> tuple[Publication, ...]:
    pubs = []
    for pub in publications:
        try:
            if pub.age <= age:
                pubs.append(pub)
        except ValueError:
            continue
    return tuple(remove_duplicate_publications(pubs))
