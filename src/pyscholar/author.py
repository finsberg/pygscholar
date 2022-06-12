from typing import List
from typing import Sequence
from typing import Tuple

from pydantic import BaseModel
from structlog import get_logger

from .publication import most_cited
from .publication import Publication
from .publication import publications_not_older_than
from .publication import topk_age
from .publication import topk_cited

logger = get_logger()


class Author(BaseModel):
    name: str
    scholar_id: str = ""
    publications: Tuple[Publication, ...] = ()

    @property
    def most_cited(self):
        return most_cited(self.publications)

    def topk_cited(self, k: int) -> Sequence[Publication]:
        return topk_cited(self.publications, k=k)

    def topk_age(self, k: int) -> Sequence[Publication]:
        return topk_age(self.publications, k=k)

    @property
    def num_citations(self) -> int:
        return sum(pub.num_citations for pub in self.publications)

    def publications_not_older_than(self, age: int) -> Sequence[Publication]:
        return publications_not_older_than(self.publications, age)

    def most_cited_not_older_than(self, age: int) -> Publication:
        return most_cited(self.publications_not_older_than(age))

    def topk_cited_not_older_than(self, k: int, age: int) -> Sequence[Publication]:
        return topk_cited(self.publications_not_older_than(age), k=k)

    def topk_age_not_older_than(self, k: int, age: int) -> Sequence[Publication]:
        return topk_age(self.publications_not_older_than(age), k=k)


def author_pub_diff(new_author: Author, old_author: Author) -> List[Publication]:
    new_pubs = []
    for publication in new_author.publications:
        if publication not in old_author.publications:
            new_pubs.append(publication)
    return new_pubs
