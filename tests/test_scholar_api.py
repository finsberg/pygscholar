from unittest import mock

import factory
import pyscholar


def test_get_author():
    author = factory.AuthorFactory.build()

    with mock.patch("pyscholar.scholar_api.scholarly.search_author") as m:
        m.return_value = iter([author.dict()])
        a = pyscholar.scholar_api.get_author(author.name, fill=False)

    assert a == author


def test_get_author_with_scholar_id():
    # Two authors with the same name but different scholar id
    author1 = factory.AuthorFactory.build(name="John Snow")
    author2 = factory.AuthorFactory.build(name="John Snow")

    with mock.patch("pyscholar.scholar_api.scholarly.search_author") as m:
        m.return_value = iter([author1.dict(), author2.dict()])
        a = pyscholar.scholar_api.get_author(
            author1.name,
            scholar_id=author2.scholar_id,
            fill=False,
        )

    m.assert_called_once_with(author1.name)
    assert a != author1
    assert a == author2


def test_extract_scholar_publications():
    author1 = factory.AuthorFactory.build(name="John Snow")
    author2 = factory.AuthorFactory.build(name="John Smith")
    author_list = (author1, author2)
    author_dict = {author.name: author.dict() for author in author_list}
    people = {author.name: author.scholar_id for author in author_list}

    with mock.patch("pyscholar.scholar_api.scholarly") as m:
        m.search_author = lambda name: iter([author_dict[name]])
        m.fill = lambda x: x
        dep = pyscholar.scholar_api.extract_scholar_publications(people)

    assert dep.authors == author_list


def test_find_publication():
    pub = factory.FullPublicationFactory.build()
    with mock.patch("pyscholar.scholar_api.scholarly") as m:
        m.search_pubs = lambda title: iter([pub.dict()])
        m.fill = lambda x: x
        p = pyscholar.scholar_api.find_publicaton(pub.title)
    assert p == pub
