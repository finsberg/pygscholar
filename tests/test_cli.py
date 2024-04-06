from pathlib import Path
from unittest import mock

import factory
import pygscholar
import pytest
from pygscholar.cli import app
from scholarly import MaxTriesExceededException
from typer.testing import CliRunner

runner = CliRunner(mix_stderr=False)


@pytest.mark.parametrize("backend", ["scholarly", "scraper", ""])
def test_add_author_simple_scholarly(tmpdir, backend):
    author = factory.AuthorInfoFactory.build()

    args = [
        "add-author",
        author.name,
        "--scholar-id",
        author.scholar_id,
        "--cache-dir",
        tmpdir,
    ]
    if backend != "":
        args += [
            "--backend",
            backend,
        ]
    else:
        # Just for the mock
        backend = "scraper"

    with mock.patch(f"pygscholar.api.{backend}.search_author") as m:
        m.return_value = [author]

        result = runner.invoke(app, args)
    assert result.exit_code == 0, result.stderr

    assert (
        f"Successfully added author with name {author.name} and scholar id {author.scholar_id}"
        in result.stdout
    )


@pytest.mark.parametrize("backend", ["scholarly", "scraper", ""])
def test_add_author_with_name_that_already_exist(tmpdir, backend):
    author = factory.AuthorInfoFactory.build()

    args = [
        "add-author",
        author.name,
        "--scholar-id",
        author.scholar_id,
        "--cache-dir",
        tmpdir,
    ]
    # Add author with same name but different scholar id
    args2 = [
        "add-author",
        author.name,
        "--scholar-id",
        "23432refw",
        "--cache-dir",
        tmpdir,
    ]
    if backend != "":
        args += [
            "--backend",
            backend,
        ]
        args2 += [
            "--backend",
            backend,
        ]
    else:
        # Just for the mock
        backend = "scraper"

    with mock.patch(f"pygscholar.api.{backend}.search_author") as m:
        m.return_value = [author]
        result = runner.invoke(app, args)
        result = runner.invoke(app, args2)

    assert result.exit_code == 101
    assert f"Author with name {author.name} already exist in database" in result.stderr


@pytest.mark.parametrize("backend", ["scholarly", "scraper", ""])
def test_add_author_with_scholar_id_that_already_exist(tmpdir, backend):
    author = factory.AuthorInfoFactory.build()

    args = [
        "add-author",
        author.name,
        "--scholar-id",
        author.scholar_id,
        "--cache-dir",
        tmpdir,
    ]
    if backend != "":
        args += [
            "--backend",
            backend,
        ]
    else:
        # Just for the mock
        backend = "scraper"

    with mock.patch(f"pygscholar.api.{backend}.search_author") as m:
        m.return_value = [author]

        result = runner.invoke(app, args)
        result = runner.invoke(app, args)

    assert result.exit_code == 102
    assert "There is already an author with the provided scholar id" in result.stderr


def test_list_author(tmpdir):
    name1 = "John Snow"
    scholar_id1 = "12345"
    name2 = "John von Neumann"
    scholar_id2 = "42"
    with mock.patch("pygscholar.api.scholarly.get_author") as m:
        m.side_effect = MaxTriesExceededException
        runner.invoke(
            app,
            [
                "add-author",
                name1,
                "--scholar-id",
                scholar_id1,
                "--cache-dir",
                tmpdir,
            ],
        )
        runner.invoke(
            app,
            [
                "add-author",
                name2,
                "--scholar-id",
                scholar_id2,
                "--cache-dir",
                tmpdir,
            ],
        )
    result = runner.invoke(app, ["list-authors", "--cache-dir", tmpdir])
    assert result.exit_code == 0

    for item in [name1, name2, scholar_id1, scholar_id2]:
        assert item in result.stdout


def test_list_author_publications_when_no_author_is_added(tmpdir):
    author = factory.AuthorFactory.build()
    with mock.patch("pygscholar.api.scholarly.scholarly") as m:
        m.search_author = lambda name: iter([author.dict()])
        m.fill = lambda x: x
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


def test_list_author_publications(tmpdir):
    author = factory.AuthorFactory.build()
    with mock.patch("pygscholar.api.scholarly.scholarly") as m:
        m.search_author = lambda name: iter([author.dict()])
        m.fill = lambda x: x
        runner.invoke(
            app,
            [
                "add-author",
                author.name,
                "--cache-dir",
                tmpdir,
            ],
        )
        result = runner.invoke(
            app,
            [
                "list-author-publications",
                author.name,
                "--cache-dir",
                tmpdir,
            ],
        )

    assert result.exit_code == 0
    assert f"Publications for {author.name} (Sorted by citations)" in result.stdout
    for pub in author.publications:
        assert pub.title in result.stdout
        assert str(pub.year) in result.stdout
        assert str(pub.num_citations) in result.stdout


def test_list_dep_new_publications(tmpdir):
    old_author = factory.AuthorFactory.build()

    authors_file = Path(tmpdir).joinpath("authors.json")
    pygscholar.utils.dump_json({old_author.name: old_author.scholar_id}, authors_file)

    dep = pygscholar.Department(authors=(old_author,))
    publications_file = Path(tmpdir).joinpath("publications.json")
    pygscholar.utils.dump_json(dep.dict(), publications_file)

    # Create a new publication
    new_pub = factory.PublicationFactory.build()

    author_dict = old_author.dict()
    author_dict["publications"] = (author_dict["publications"][0], new_pub.dict())
    new_author = pygscholar.Author(**author_dict)

    with mock.patch("pygscholar.api.scholarly.scholarly") as m:
        m.search_author = lambda name: iter([new_author.dict()])
        m.fill = lambda x: x
        result = runner.invoke(
            app,
            [
                "list-new-dep-publications",
                "--no-add-authors",
                "--cache-dir",
                tmpdir,
            ],
        )

    assert result.exit_code == 0
    assert "New publications" in result.stdout
    assert new_pub.title in result.stdout
