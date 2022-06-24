import tempfile
from pathlib import Path
from unittest import mock

import factory
import pygscholar
import pytest
from pygscholar.cli import app
from scholarly import MaxTriesExceededException
from typer.testing import CliRunner

runner = CliRunner(mix_stderr=False)


@pytest.fixture
def cache_dir():

    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


def test_add_author_simple(cache_dir):
    name = "John Snow"
    scholar_id = "12345"
    with mock.patch("pygscholar.scholar_api.get_author") as m:
        m.side_effect = MaxTriesExceededException
        result = runner.invoke(
            app,
            ["add-author", name, "--scholar-id", scholar_id, "--cache-dir", cache_dir],
        )
    assert result.exit_code == 0

    assert (
        f"Successfully added author with name {name} and scholar id {scholar_id}"
        in result.stdout
    )


def test_add_author_with_name_that_already_exist(cache_dir):
    name = "John Snow"
    scholar_id = "12345"
    with mock.patch("pygscholar.scholar_api.get_author") as m:
        m.side_effect = MaxTriesExceededException
        runner.invoke(
            app,
            ["add-author", name, "--scholar-id", scholar_id, "--cache-dir", cache_dir],
        )
        result = runner.invoke(
            app,
            ["add-author", name, "--scholar-id", "34141", "--cache-dir", cache_dir],
        )
    assert result.exit_code == 101
    assert f"Author with name {name} already exist in database" in result.stderr


def test_add_author_with_scholar_id_that_already_exist(cache_dir):
    name = "John Snow"
    scholar_id = "12345"
    with mock.patch("pygscholar.scholar_api.get_author") as m:
        m.side_effect = MaxTriesExceededException
        runner.invoke(
            app,
            ["add-author", name, "--scholar-id", scholar_id, "--cache-dir", cache_dir],
        )
        result = runner.invoke(
            app,
            [
                "add-author",
                "Barbara",
                "--scholar-id",
                scholar_id,
                "--cache-dir",
                cache_dir,
            ],
        )
    assert result.exit_code == 102
    assert "There is already an author with the provided scholar id" in result.stderr


def test_list_author(cache_dir):
    name1 = "John Snow"
    scholar_id1 = "12345"
    name2 = "John von Neumann"
    scholar_id2 = "42"
    with mock.patch("pygscholar.scholar_api.get_author") as m:
        m.side_effect = MaxTriesExceededException
        runner.invoke(
            app,
            [
                "add-author",
                name1,
                "--scholar-id",
                scholar_id1,
                "--cache-dir",
                cache_dir,
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
                cache_dir,
            ],
        )
    result = runner.invoke(app, ["list-authors", "--cache-dir", cache_dir])
    assert result.exit_code == 0

    for item in [name1, name2, scholar_id1, scholar_id2]:
        assert item in result.stdout


def test_list_author_publications_when_no_author_is_added(cache_dir):
    author = factory.AuthorFactory.build()
    with mock.patch("pygscholar.scholar_api.scholarly") as m:

        m.search_author = lambda name: iter([author.dict()])
        m.fill = lambda x: x
        result = runner.invoke(
            app,
            [
                "list-author-publications",
                author.name,
                "--cache-dir",
                cache_dir,
            ],
        )

    assert result.exit_code == 1
    assert f"Unable to find name '{author.name}'. Possible options are \n" == str(
        result.exception,
    )


def test_list_author_publications(cache_dir):
    author = factory.AuthorFactory.build()
    with mock.patch("pygscholar.scholar_api.scholarly") as m:

        m.search_author = lambda name: iter([author.dict()])
        m.fill = lambda x: x
        runner.invoke(
            app,
            [
                "add-author",
                author.name,
                "--cache-dir",
                cache_dir,
            ],
        )
        result = runner.invoke(
            app,
            [
                "list-author-publications",
                author.name,
                "--cache-dir",
                cache_dir,
            ],
        )

    assert result.exit_code == 0
    assert f"Publications for {author.name} (Sorted by citations)" in result.stdout
    for pub in author.publications:
        assert pub.title in result.stdout
        assert str(pub.year) in result.stdout
        assert str(pub.num_citations) in result.stdout


def test_list_dep_new_publications(cache_dir):
    old_author = factory.AuthorFactory.build()

    authors_file = Path(cache_dir).joinpath("authors.json")
    pygscholar.utils.dump_json({old_author.name: old_author.scholar_id}, authors_file)

    dep = pygscholar.Department(authors=(old_author,))
    publications_file = Path(cache_dir).joinpath("publications.json")
    pygscholar.utils.dump_json(dep.dict(), publications_file)

    # Create a new publication
    new_pub = factory.PublicationFactory.build()

    author_dict = old_author.dict()
    author_dict["publications"] = (author_dict["publications"][0], new_pub.dict())
    new_author = pygscholar.Author(**author_dict)

    with mock.patch("pygscholar.scholar_api.scholarly") as m:

        m.search_author = lambda name: iter([new_author.dict()])
        m.fill = lambda x: x
        result = runner.invoke(
            app,
            [
                "list-new-dep-publications",
                "--no-add-authors",
                "--cache-dir",
                cache_dir,
            ],
        )

    assert result.exit_code == 0
    assert "New publications" in result.stdout
    assert new_pub.title in result.stdout
