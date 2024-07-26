import factory
import pygscholar


def test_author_diff_with_one_new():
    author_old = factory.AuthorFactory.build()
    new_pub = factory.PublicationFactory.build()
    author_new = pygscholar.Author(
        info=author_old.info,
        publications=tuple(author_old.publications) + (new_pub,),
    )
    new_pubs = pygscholar.author.author_pub_diff(author_new, author_old)
    assert len(new_pubs) == 1
    assert new_pubs[0] == new_pub


def test_author_diff_with_one_new_and_one_new_old():
    author_old = factory.AuthorFactory.build()
    new_pub = factory.PublicationFactory.build()
    old_new_pub = factory.PublicationFactory.build()
    author_new = pygscholar.Author(
        info=author_old.info,
        publications=tuple(author_old.publications) + (new_pub,),
    )
    author_old = pygscholar.Author(
        info=author_old.info,
        publications=tuple(author_old.publications) + (old_new_pub,),
    )
    new_pubs = pygscholar.author.author_pub_diff(author_new, author_old)
    assert len(new_pubs) == 1
    assert new_pubs[0] == new_pub
