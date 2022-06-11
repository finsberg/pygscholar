import factory
import pyscholar


def test_dep_diff():
    author1_old = factory.AuthorFactory.build()
    author2_old = factory.AuthorFactory.build()
    new_pub_common = factory.PublicationFactory.build()
    new_pub_author1 = factory.PublicationFactory.build()
    author1_new = pyscholar.Author(
        name=author1_old.name,
        scholar_id=author1_old.scholar_id,
        publications=author1_old.publications + (new_pub_common, new_pub_author1),
    )
    author2_new = pyscholar.Author(
        name=author2_old.name,
        scholar_id=author2_old.scholar_id,
        publications=author2_old.publications + (new_pub_common,),
    )
    department_old = pyscholar.Department(authors=(author1_old, author2_old))
    department_new = pyscholar.Department(authors=(author1_new, author2_new))

    new_pubs = pyscholar.department.department_diff(
        department_new,
        department_old,
        fill=False,
    )
    assert len(new_pubs) == 2
    assert new_pub_common.title in new_pubs
    assert new_pub_author1.title in new_pubs
    assert new_pubs[new_pub_common.title] == new_pub_common
    assert new_pubs[new_pub_author1.title] == new_pub_author1

    # assert len(new_pubs) == 1
    # assert new_pubs[0] == new_pub
