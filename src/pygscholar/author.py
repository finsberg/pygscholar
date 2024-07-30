from __future__ import annotations
from typing import Sequence
from typing import Any

from pydantic import BaseModel, Field
from structlog import get_logger

from . import publication as pub


logger = get_logger()


class AuthorInfo(BaseModel):
    name: str
    scholar_id: str
    link: str = ""
    affiliation: str = ""
    email: str = ""
    cited_by: int = 0
    data: dict[str, Any] = Field(default_factory=dict)


class Author(BaseModel):
    info: AuthorInfo
    publications: Sequence[pub.Publication] = ()

    @property
    def name(self) -> str:
        return self.info.name

    @property
    def scholar_id(self) -> str:
        return self.info.scholar_id

    @property
    def most_cited(self):
        return pub.most_cited(self.publications)

    def topk_cited(self, k: int) -> Sequence[pub.Publication]:
        return pub.topk_cited(self.publications, k=k)

    def topk_age(self, k: int) -> Sequence[pub.Publication]:
        return pub.topk_age(self.publications, k=k)

    @property
    def num_citations(self) -> int:
        return sum(pub.num_citations for pub in self.publications)

    def publications_not_older_than(self, age: int) -> Sequence[pub.Publication]:
        return pub.publications_not_older_than(self.publications, age)

    def most_cited_not_older_than(self, age: int) -> pub.Publication:
        return pub.most_cited(self.publications_not_older_than(age))

    def topk_cited_not_older_than(self, k: int, age: int) -> Sequence[pub.Publication]:
        return pub.topk_cited(self.publications_not_older_than(age), k=k)

    def topk_age_not_older_than(self, k: int, age: int) -> Sequence[pub.Publication]:
        return pub.topk_age(self.publications_not_older_than(age), k=k)


def author_pub_diff(
    new_author: Author,
    old_author: Author,
    only_new: bool = False,
) -> list[pub.Publication]:
    new_pubs = []
    old_author_publications = {p.title.lower().strip() for p in old_author.publications}
    if only_new:
        new_author_publications = new_author.publications_not_older_than(0)
    else:
        new_author_publications = new_author.publications
    # We only need to check new publications
    for publication in new_author_publications:
        if publication.title.lower().strip() not in old_author_publications:
            new_pubs.append(publication)
    return new_pubs
