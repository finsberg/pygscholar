from __future__ import annotations

from typing import Union

from pydantic import BaseModel

from .author import Author
from .author import author_pub_diff
from .publication import FullPublication
from .publication import most_cited
from .publication import Publication
from .publication import topk_cited


class Department(BaseModel):
    authors: tuple[Author, ...] = ()

    @property
    def publications(self):
        publications = set()
        for author in self.authors:
            publications.update(set(author.publications))
        return publications

    def get_author_by_name(self, name: str) -> Author:
        for author in self.authors:
            if author.name.lower() == name.lower():
                return author
        raise RuntimeError(f"Unable to find author with name '{name}'")

    def get_author_by_scholar_id(self, scholar_id: str) -> Author:
        for author in self.authors:
            if author.scholar_id.lower() == scholar_id.lower():
                return author
        raise RuntimeError(f"Unable to find author with scholar id '{scholar_id}'")

    @property
    def names(self) -> set[str]:
        return {author.name for author in self.authors}

    @property
    def most_cited(self):
        return most_cited(self.publications)

    def topk_cited(self, k: int) -> list[Publication]:
        return topk_cited(self.publications, k)


def department_diff(
    new_dep: Department,
    old_dep: Department,
    fill: bool = True,
) -> dict[str, Union[Publication, FullPublication]]:
    # FIXME: Add overload
    author_names = new_dep.names.intersection(old_dep.names)

    all_pubs: list[Publication] = []
    for name in author_names:
        new_author = new_dep.get_author_by_name(name)
        old_author = old_dep.get_author_by_name(name)
        all_pubs.extend(author_pub_diff(new_author, old_author))

    new_pubs = {p.title: p for p in all_pubs}
    if fill:
        new_filled_pubs = {}
        for title, p in new_pubs.items():
            new_filled_pubs[title] = p.fill()
        return new_filled_pubs
    else:
        return new_pubs
