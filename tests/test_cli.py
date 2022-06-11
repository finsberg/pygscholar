import tempfile

import pytest
from pyscholar.cli import app
from typer.testing import CliRunner

runner = CliRunner(mix_stderr=False)


@pytest.fixture
def cache_dir():

    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


def test_add_author(cache_dir):
    name = "John Snow"
    scholar_id = "12345"
    result = runner.invoke(
        app,
        ["add-author", name, scholar_id, "--cache-dir", cache_dir],
    )
    assert result.exit_code == 0
    assert (
        f"Successfully added author with name {name} and scholar id {scholar_id}"
        in result.stdout
    )


def test_add_author_with_name_that_already_exist(cache_dir):
    name = "John Snow"
    scholar_id = "12345"
    runner.invoke(app, ["add-author", name, scholar_id, "--cache-dir", cache_dir])
    result = runner.invoke(app, ["add-author", name, "34141", "--cache-dir", cache_dir])
    assert result.exit_code == 101
    assert f"Author with name {name} already exist in database" in result.stderr


def test_add_author_with_scholar_id_that_already_exist(cache_dir):
    name = "John Snow"
    scholar_id = "12345"
    runner.invoke(app, ["add-author", name, scholar_id, "--cache-dir", cache_dir])
    result = runner.invoke(
        app,
        ["add-author", "Barbara", scholar_id, "--cache-dir", cache_dir],
    )
    assert result.exit_code == 102
    assert "There is already an author with the provided scholar id" in result.stderr


def test_list_author(cache_dir):
    name1 = "John Snow"
    scholar_id1 = "12345"
    runner.invoke(app, ["add-author", name1, scholar_id1, "--cache-dir", cache_dir])

    name2 = "John von Neumann"
    scholar_id2 = "42"
    runner.invoke(app, ["add-author", name2, scholar_id2, "--cache-dir", cache_dir])
    result = runner.invoke(app, ["list-authors", "--cache-dir", cache_dir])
    assert result.exit_code == 0

    for item in [name1, name2, scholar_id1, scholar_id2]:
        assert item in result.stdout
