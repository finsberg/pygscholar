import factory
import pygscholar


def test_dep_diff():
    author1_old = factory.AuthorFactory.build()
    author2_old = factory.AuthorFactory.build()
    new_pub_common = factory.PublicationFactory.build()
    new_pub_author1 = factory.PublicationFactory.build()
    author1_new = pygscholar.Author(
        info=author1_old.info,
        publications=author1_old.publications + [new_pub_common, new_pub_author1],
    )
    author2_new = pygscholar.Author(
        info=author2_old.info,
        publications=author2_old.publications + [new_pub_common],
    )
    department_old = pygscholar.Department(authors=(author1_old, author2_old))
    department_new = pygscholar.Department(authors=(author1_new, author2_new))

    new_pubs = pygscholar.department.department_diff(
        department_new,
        department_old,
        fill=False,
    )
    assert len(new_pubs) == 2
    assert new_pub_common.title in new_pubs
    assert new_pub_author1.title in new_pubs
    assert new_pubs[new_pub_common.title] == new_pub_common
    assert new_pubs[new_pub_author1.title] == new_pub_author1
