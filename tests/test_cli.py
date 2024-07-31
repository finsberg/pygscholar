from unittest import mock
import contextlib

import factory
import pygscholar
import pytest
from pygscholar.cli import app
from typer.testing import CliRunner

runner = CliRunner(mix_stderr=False)


@contextlib.contextmanager
def mock_add_author(author: pygscholar.author.Author, backend):
    with mock.patch(f"pygscholar.api.{backend}.search_author") as m1:
        m1.return_value = [author.info]
        with mock.patch("pygscholar.api.search_author_with_publications") as m2:
            m2.return_value = author
            yield


def create_args(
    author: pygscholar.AuthorInfo, backend: pygscholar.api.APIBackend, cache_dir: str
) -> tuple[list[str], pygscholar.api.APIBackend]:
    args = [
        "add-author",
        author.name,
        "--scholar-id",
        author.scholar_id,
        "--cache-dir",
        str(cache_dir),
    ]
    if backend == "":
        backend = pygscholar.api.APIBackend.SCRAPER

    args += [
        "--backend",
        str(backend),
    ]

    return args, backend


@pytest.mark.parametrize("backend", ["scholarly", "scraper"])
def test_add_author_simple(tmpdir, backend):
    author = factory.AuthorFactory.build()
    args, backend = create_args(author, backend, tmpdir)

    with mock_add_author(author, backend):
        result = runner.invoke(app, args)

    assert result.exit_code == 0, result.stderr

    assert (
        f"Successfully added author with name {author.name} and scholar id {author.scholar_id}"
        in result.stdout
    )


@pytest.mark.parametrize("backend", ["scholarly", "scraper"])
def test_add_author_with_name_that_already_exist(tmpdir, backend):
    author = factory.AuthorFactory.build()
    args, backend = create_args(author, backend, tmpdir)
    args2, _ = create_args(author, backend, tmpdir)
    args2[3] = "23432refw"  # Change scholar id

    with mock_add_author(author, backend):
        result = runner.invoke(app, args)
        result = runner.invoke(app, args2)

    assert result.exit_code == 101
    assert f"Author with name {author.name} already exist in database" in result.stderr


@pytest.mark.parametrize("backend", ["scholarly", "scraper"])
def test_add_author_with_scholar_id_that_already_exist(tmpdir, backend):
    author = factory.AuthorFactory.build()

    args, backend = create_args(author, backend, tmpdir)

    with mock_add_author(author, backend):
        result = runner.invoke(app, args)
        args[1] = "Another name"
        result = runner.invoke(app, args)

    assert result.exit_code == 102
    assert "There is already an author with the provided scholar id" in result.stderr


@pytest.mark.parametrize("backend", ["scholarly", "scraper"])
def test_list_author(tmpdir, backend):
    author1 = factory.AuthorFactory.build()
    author2 = factory.AuthorFactory.build()
    args1, backend = create_args(author1, backend, tmpdir)
    args2, backend = create_args(author2, backend, tmpdir)
    with mock.patch(f"pygscholar.api.{backend}.search_author") as m1:
        m1.return_value = [author1.info, author2.info]

        with mock.patch("pygscholar.api.search_author_with_publications") as m2:
            m2.return_value = author1
            result1 = runner.invoke(app, args1)
        with mock.patch("pygscholar.api.search_author_with_publications") as m2:
            m2.return_value = author2
            result2 = runner.invoke(app, args2)

        result = runner.invoke(app, ["list-authors", "--cache-dir", tmpdir])

    assert result1.exit_code == 0
    assert result2.exit_code == 0
    assert result.exit_code == 0
    assert author1.name in result.stdout
    assert author2.name in result.stdout
    assert author1.scholar_id in result.stdout
    assert author2.scholar_id in result.stdout


@pytest.mark.parametrize("backend", ["scholarly", "scraper"])
def test_list_author_publications_when_no_author_is_added(tmpdir, backend):
    author = factory.AuthorFactory.build()
    with mock.patch(f"pygscholar.api.{backend}.search_author") as m:
        m.return_value = []
        result = runner.invoke(
            app,
            [
                "list-author-publications",
                author.name,
                "--cache-dir",
                tmpdir,
            ],
        )

    assert result.exit_code == 1
    assert f"Unable to find name '{author.name}'. Possible options are \n" == str(
        result.exception,
    )


@pytest.mark.parametrize("add_authors", [False, True])
@pytest.mark.parametrize("backend", ["scholarly", "scraper"])
def test_list_author_publications(tmpdir, backend, add_authors):
    author = factory.AuthorFactory.build()
    args1, backend = create_args(author.info, backend, tmpdir)

    args = [
        "list-author-publications",
        author.name,
        "--cache-dir",
        str(tmpdir),
        "--backend",
        backend,
    ]
    if add_authors:
        args.append("--add-authors")

    with mock_add_author(author, backend):
        runner.invoke(app, args1)

        result = runner.invoke(
            app,
            args,
        )

    assert result.exit_code == 0

    assert f"Publications for {author.name} (Sorted by citations)" in result.stdout
    for pub in author.publications:
        assert pub.title[:10] in result.stdout
        assert str(pub.year) in result.stdout
        assert str(pub.num_citations) in result.stdout
        if add_authors:
            assert pub.authors[:10] in result.stdout


@pytest.mark.parametrize("backend", ["scholarly", "scraper"])
def test_list_new_author_publications(tmpdir, backend):
    old_author = factory.AuthorFactory.build()
    new_pub = factory.PublicationFactory.build()

    author_dict = old_author.dict()
    author_dict["publications"] = (author_dict["publications"][0], new_pub.dict())
    new_author = pygscholar.Author(**author_dict)

    args, backend = create_args(old_author.info, backend, tmpdir)

    with mock_add_author(old_author, backend):
        runner.invoke(app, args)
    with mock_add_author(new_author, backend):
        result = runner.invoke(
            app,
            [
                "list-new-author-publications",
                old_author.info.name,
                "--cache-dir",
                str(tmpdir),
                "--overwrite",
            ],
        )
    assert result.exit_code == 0
    assert author_dict["publications"][0]["title"] not in result.stdout
    assert new_pub.title in result.stdout


@pytest.mark.parametrize("backend", ["scholarly", "scraper"])
@pytest.mark.parametrize("add_authors", [False, True])
def test_list_department_publications(tmpdir, backend, add_authors):
    author1 = factory.AuthorFactory.build()
    author2 = factory.AuthorFactory.build()

    args1, backend = create_args(author1.info, backend, tmpdir)
    args2, backend = create_args(author2.info, backend, tmpdir)

    with mock_add_author(author1, backend):
        runner.invoke(app, args1)
    with mock_add_author(author2, backend):
        runner.invoke(app, args2)

    args = [
        "list-department-publications",
        "--cache-dir",
        str(tmpdir),
    ]
    if add_authors:
        args.append("--add-authors")

    result = runner.invoke(app, args)
    assert result.exit_code == 0

    for pub in author1.publications + author2.publications:
        assert pub.title[:10] in result.stdout
        assert str(pub.year) in result.stdout
        assert str(pub.num_citations) in result.stdout

        if add_authors:
            assert pub.authors[:10] in result.stdout
        else:
            assert pub.authors[:10] not in result.stdout


@pytest.mark.parametrize("backend", ["scholarly", "scraper"])
def test_list_new_department_publications(tmpdir, backend):
    author1 = factory.AuthorFactory.build()
    author2 = factory.AuthorFactory.build()
    new_pub = factory.PublicationFactory.build()

    author_dict1 = author1.dict()
    author_dict1["publications"] = (author_dict1["publications"][0], new_pub.dict())
    new_author1 = pygscholar.Author(**author_dict1)

    author_dict2 = author2.dict()
    author_dict2["publications"] = (author_dict2["publications"][0], new_pub.dict())
    new_author2 = pygscholar.Author(**author_dict2)

    args1, backend = create_args(author1.info, backend, tmpdir)
    args2, backend = create_args(author2.info, backend, tmpdir)

    with mock_add_author(author1, backend):
        runner.invoke(app, args1)
    with mock_add_author(author2, backend):
        runner.invoke(app, args2)

    def search_mock(*args, **kwargs):
        if kwargs.get("name") == author1.info.name:
            return new_author1
        if kwargs.get("name") == author2.info.name:
            return new_author2
        raise RuntimeError("Could not find author")

    with mock.patch("pygscholar.api.search_author_with_publications") as m2:
        m2.side_effect = search_mock
        result = runner.invoke(
            app,
            [
                "list-new-department-publications",
                "--cache-dir",
                str(tmpdir),
                "--overwrite",
            ],
        )

    assert result.exit_code == 0

    assert author_dict1["publications"][0]["title"] not in result.stdout
    assert author_dict2["publications"][0]["title"] not in result.stdout
    assert new_pub.title in result.stdout
