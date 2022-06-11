import datetime
import itertools
import random

import factory
import pyscholar
import pytest


@pytest.mark.parametrize("seed", (0, 1, 2))
def test_most_cited(seed):
    random.seed(seed)
    pub1 = factory.PublicationFactory.build(num_citations=10)
    pub2 = factory.PublicationFactory.build(num_citations=1)
    pub3 = factory.PublicationFactory.build(num_citations=0)
    pubs = [pub1, pub2, pub3]
    random.shuffle(pubs)
    pub = pyscholar.publication.most_cited(pubs)
    assert pub == pub1


@pytest.mark.parametrize("seed, k", itertools.product((0, 1, 2), (0, 1, 2, 3, 4)))
def test_topk_cited(seed, k):
    random.seed(seed)
    pub1 = factory.PublicationFactory.build(num_citations=10)
    pub2 = factory.PublicationFactory.build(num_citations=1)
    pub3 = factory.PublicationFactory.build(num_citations=0)
    pubs = [pub1, pub2, pub3]
    random.shuffle(pubs)
    lst = pyscholar.publication.topk_cited([pub1, pub2, pub3], k=k)

    assert len(lst) == min(k, len(pubs))
    if k >= 1:
        assert lst[0] == pub1
    if k >= 2:
        assert lst[1] == pub2
    if k >= 3:
        assert lst[2] == pub3


def test_publications_not_older_than():
    year = datetime.date.today().year
    pub1 = factory.PublicationFactory.build(
        bib=factory.PublicationBibFactory.build(pub_year=year - 1),
    )
    pub2 = factory.PublicationFactory.build(
        bib=factory.PublicationBibFactory.build(pub_year=year - 3),
    )
    pub3 = factory.PublicationFactory.build(
        bib=factory.PublicationBibFactory.build(pub_year=-1),
    )
    pubs = [pub1, pub2, pub3]
    lst = pyscholar.publication.publications_not_older_than(pubs, age=1)

    assert len(lst) == 1
    assert lst[0] == pub1
