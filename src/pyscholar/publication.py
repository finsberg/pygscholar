from __future__ import annotations

import datetime
from functools import reduce
from typing import Sequence

from pydantic import BaseModel
from scholarly import publication_parser
from scholarly import scholarly
from structlog import get_logger

logger = get_logger()


def most_cited(publications: Sequence[Publication]) -> Publication:
    def func(pub1: Publication, pub2: Publication):
        if pub1.num_citations >= pub2.num_citations:
            return pub1
        return pub2

    return reduce(func, publications)


def topk_cited(publications: Sequence[Publication], k: int):
    sorted_publications = list(
        reversed(sorted(publications, key=lambda p: p.num_citations)),
    )
    return sorted_publications[:k]


def publications_not_older_than(
    publications: Sequence[Publication],
    age: int,
) -> list[Publication]:
    pubs = []
    for pub in publications:
        try:
            if pub.age <= age:
                pubs.append(pub)
        except ValueError:
            continue
    return pubs


class FullPublicationBib(BaseModel):
    title: str
    author: list[str]
    abstract: str = ""
    journal: str = ""
    citation: str
    pub_year: int = -1


class FullPublication(BaseModel):
    bib: FullPublicationBib
    eprint_url: str = ""

    num_citations: int
    container_type: str = "Publication"
    source: publication_parser.PublicationSource
    author_pub_id: str

    @property
    def title(self) -> str:
        return self.bib.title

    @property
    def journal(self) -> str:
        return self.bib.citation

    @property
    def year(self) -> int:
        if self.bib.pub_year == -1:
            raise ValueError(f"Invalid year for {self.title}")
        return self.bib.pub_year

    @property
    def age(self) -> int:
        year = datetime.date.today().year
        return year - self.year

    def __hash__(self) -> int:
        return hash(self.title)

    def print(self):
        pass


class PublicationBib(BaseModel):
    title: str
    citation: str
    pub_year: int = -1


class Publication(BaseModel):
    bib: PublicationBib
    num_citations: int
    container_type: str = "Publication"
    source: publication_parser.PublicationSource
    author_pub_id: str

    @property
    def title(self) -> str:
        return self.bib.title

    @property
    def journal(self) -> str:
        return self.bib.citation

    @property
    def year(self) -> int:
        if self.bib.pub_year == -1:
            raise ValueError(f"Invalid year for {self.title}")
        return self.bib.pub_year

    @property
    def age(self) -> int:
        year = datetime.date.today().year
        return year - self.year

    def __hash__(self) -> int:
        return hash(self.title)

    def fill(self) -> FullPublication:
        return FullPublication(**scholarly.fill(self.dict()))
