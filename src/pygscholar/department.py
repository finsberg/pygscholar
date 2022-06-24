from typing import Dict
from typing import List
from typing import Sequence
from typing import Set
from typing import Tuple
from typing import Union

from pydantic import BaseModel

from .author import Author
from .author import author_pub_diff
from .publication import FullPublication
from .publication import most_cited
from .publication import Publication
from .publication import publications_not_older_than
from .publication import topk_age
from .publication import topk_cited


class Department(BaseModel):
    authors: Tuple[Author, ...] = ()

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
    def names(self) -> Set[str]:
        return {author.name for author in self.authors}

    @property
    def most_cited(self):
        return most_cited(self.publications)

    def topk_age(self, k: int) -> Sequence[Publication]:
        return topk_age(self.publications, k=k)

    def topk_cited(self, k: int) -> Sequence[Publication]:
        return topk_cited(self.publications, k)

    def publications_not_older_than(self, age: int) -> Sequence[Publication]:
        return publications_not_older_than(self.publications, age)

    def most_cited_not_older_than(self, age: int) -> Publication:
        return most_cited(self.publications_not_older_than(age))

    def topk_cited_not_older_than(self, k: int, age: int) -> Sequence[Publication]:
        return topk_cited(self.publications_not_older_than(age), k=k)

    def topk_age_not_older_than(self, k: int, age: int) -> Sequence[Publication]:
        return topk_age(self.publications_not_older_than(age), k=k)


def department_diff(
    new_dep: Department,
    old_dep: Department,
    fill: bool = False,
    only_new: bool = False,
) -> Dict[str, Union[Publication, FullPublication]]:
    # FIXME: Add overload
    author_names = new_dep.names.intersection(old_dep.names)

    all_pubs: List[Publication] = []
    for name in author_names:
        new_author = new_dep.get_author_by_name(name)
        old_author = old_dep.get_author_by_name(name)
        all_pubs.extend(author_pub_diff(new_author, old_author, only_new=only_new))

    new_pubs = {p.title: p for p in all_pubs}
    if fill:
        new_filled_pubs = {}
        for title, p in new_pubs.items():
            new_filled_pubs[title] = p.fill()
        return new_filled_pubs
    else:
        return new_pubs
