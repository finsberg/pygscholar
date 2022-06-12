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


@pytest.mark.parametrize("seed, k", itertools.product((0, 1, 2), (0, 1, 2, 3, 4)))
def test_topk_age(seed, k):
    random.seed(seed)
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
    random.shuffle(pubs)
    lst = pyscholar.publication.topk_age([pub1, pub2, pub3], k=k)
    assert len(lst) == min(k, 2)  # pub3 should never be included
    if k >= 1:
        assert lst[0] == pub1
    if k >= 2:
        assert lst[1] == pub2


@pytest.mark.parametrize(
    "age, PubBibPubFactory",
    itertools.product(
        (1, 3, 5, 10),
        (
            (factory.PublicationBibFactory, factory.PublicationFactory),
            (factory.FullPublicationBibFactory, factory.FullPublicationFactory),
        ),
    ),
)
def test_publication_year(age, PubBibPubFactory):
    PubBibFactor, PubFactory = PubBibPubFactory
    year = datetime.date.today().year
    pub = PubFactory.build(
        bib=PubBibFactor.build(pub_year=year - age),
    )
    assert pub.age == age
    assert pub.year == year - age


def test_publication_invalid_year():
    pub = factory.PublicationFactory.build(
        bib=factory.PublicationBibFactory.build(pub_year=-1),
    )
    with pytest.raises(ValueError):
        pub.year


def test_publication_invalid_age():
    pub = factory.PublicationFactory.build(
        bib=factory.PublicationBibFactory.build(pub_year=-1),
    )
    with pytest.raises(ValueError):
        pub.age


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
