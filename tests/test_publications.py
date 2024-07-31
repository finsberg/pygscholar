import datetime
import itertools
import random

import factory
import pygscholar
import pytest


@pytest.mark.parametrize("seed", (0, 1, 2))
def test_most_cited(seed):
    random.seed(seed)
    pub1 = factory.PublicationFactory.build(num_citations=10)
    pub2 = factory.PublicationFactory.build(num_citations=1)
    pub3 = factory.PublicationFactory.build(num_citations=0)
    pubs = [pub1, pub2, pub3]
    random.shuffle(pubs)
    pub = pygscholar.publication.most_cited(pubs)
    assert pub == pub1


@pytest.mark.parametrize("seed, k", itertools.product((0, 1, 2), (0, 1, 2, 3, 4)))
def test_topk_cited(seed, k):
    random.seed(seed)
    pub1 = factory.PublicationFactory.build(num_citations=10)
    pub2 = factory.PublicationFactory.build(num_citations=1)
    pub3 = factory.PublicationFactory.build(num_citations=0)
    pubs = [pub1, pub2, pub3]
    random.shuffle(pubs)
    lst = pygscholar.publication.topk_cited([pub1, pub2, pub3], k=k)

    assert len(lst) == min(k, len(pubs))
    if k >= 1:
        assert lst[0] == pub1
    if k >= 2:
        assert lst[1] == pub2
    if k >= 3:
        assert lst[2] == pub3


@pytest.mark.parametrize("seed, k", itertools.product((0, 1, 2), (0, 1, 2)))
def test_topk_age(seed, k):
    random.seed(seed)
    year = datetime.date.today().year
    pub1 = factory.PublicationFactory.build(year=year - 1)
    pub2 = factory.PublicationFactory.build(year=year - 3)
    pub3 = factory.PublicationFactory.build(year=-1)
    pubs = [pub1, pub2, pub3]
    random.shuffle(pubs)
    lst = pygscholar.publication.topk_age([pub1, pub2, pub3], k=k)

    assert len(lst) == k
    if k >= 1:
        assert lst[0] == pub1
    if k >= 2:
        assert lst[1] == pub2


@pytest.mark.parametrize("age", (1, 3, 5, 10))
def test_publication_year(age):
    year = datetime.date.today().year
    pub = factory.PublicationFactory.build(year=year - age)
    assert pub.age == age
    assert pub.year == year - age


def test_publications_not_older_than():
    year = datetime.date.today().year
    pub1 = factory.PublicationFactory.build(year=year - 1)
    pub2 = factory.PublicationFactory.build(year=year - 3)
    pub3 = factory.PublicationFactory.build(year=-1)
    pubs = [pub1, pub2, pub3]
    lst = pygscholar.publication.publications_not_older_than(pubs, age=1)

    assert len(lst) == 1
    assert lst[0] == pub1
