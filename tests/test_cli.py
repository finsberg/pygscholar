import tempfile
from unittest import mock

import pytest
from pyscholar.cli import app
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
    with mock.patch("pyscholar.scholar_api.get_author") as m:
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
    with mock.patch("pyscholar.scholar_api.get_author") as m:
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
    with mock.patch("pyscholar.scholar_api.get_author") as m:
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
    with mock.patch("pyscholar.scholar_api.get_author") as m:
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
