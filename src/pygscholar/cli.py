"""
Command line interface for pygscholar. You can also set the environment variable
`PYSCHOLAR_CACHE_DIR` to change the default cache directory.

"""

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from scholarly import MaxTriesExceededException


from . import api
from . import config
from . import cache
from .department import Department, department_diff

app = typer.Typer(help=__doc__)


def version_callback(show_version: bool):
    """Prints version information."""
    if show_version:
        from . import __version__, __program_name__

        typer.echo(f"{__program_name__} {__version__}")
        raise typer.Exit()


def license_callback(show_license: bool):
    """Prints license information."""
    if show_license:
        from . import __license__

        typer.echo(f"{__license__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version",
    ),
    license: bool = typer.Option(
        None,
        "--license",
        callback=license_callback,
        is_eager=True,
        help="Show license",
    ),
):
    # Do other global stuff, handle other global options here
    return


@app.command(help="List all authors")
def list_authors(cache_dir: str = config.DEFAULT_CACHE_DIR):
    authors = cache.load_authors(cache_dir)

    table = Table(title="Authors")

    table.add_column("Name", justify="right", style="cyan", no_wrap=True)
    table.add_column("Scholar ID", style="magenta")

    for name, scholar_id in authors.items():
        print(name)
        table.add_row(name, scholar_id)

    console = Console()
    console.print(table)


@app.command(help="Search for authors")
def search_author(
    name: str,
    backend: api.APIBackend = api.APIBackend.SCRAPER,
):
    authors = api.search_author(name=name, backend=backend)

    table = Table(title=f"Search results for author '{name}'")
    table.add_column("Name", style="cyan")
    table.add_column("Scholar ID", style="magenta")
    table.add_column("Affiliation", style="blue")
    table.add_column("Cited by", style="yellow")

    for author in authors:
        table.add_row(
            author.name,
            author.scholar_id,
            author.affiliation,
            str(author.cited_by),
        )

    console = Console()
    console.print(table)


@app.command(help="Add new author")
def add_author(
    name: str,
    scholar_id: str = "",
    cache_dir: str = config.DEFAULT_CACHE_DIR,
    backend: api.APIBackend = api.APIBackend.SCRAPER,
):
    authors = cache.load_authors(cache_dir)

    if name in authors:
        typer.echo(f"Author with name {name} already exist in database", err=True)
        raise typer.Exit(101)
    if scholar_id != "" and scholar_id in authors.values():
        typer.echo("There is already an author with the provided scholar id", err=True)
        raise typer.Exit(102)

    try:
        author_results = api.search_author(
            name,
            scholar_id=scholar_id,
            backend=backend,
        )

    except MaxTriesExceededException:
        typer.echo(f"Author {name} does not exist.")
        raise typer.Exit(104)
    else:
        if len(author_results) == 0:
            typer.echo(f"Author {name} does not exist.")
            raise typer.Exit(104)
        if len(author_results) > 1:
            msg = (
                f"Multiple authors ({len(author_results)}) found. "
                "Will choose the first result. Please be more specific "
                "or specify the scholar id if you want more rubust search."
            )
            typer.echo(msg)

        author = author_results[0]
        name = author.name
        typer.echo(f"Adding author {name}")

        if scholar_id == "":
            scholar_id = author.scholar_id

        # Now check if the author already exists in the database
        if name in authors:
            typer.echo(
                f"Author with name {name} already exist in database",
                err=True,
            )
            raise typer.Exit(101)

    authors[name] = scholar_id
    cache.save_authors(authors, cache_dir)

    typer.echo(
        f"Successfully added author with name {name} and scholar id {scholar_id}",
    )

    typer.echo("Search for publications. This can take some time")
    author_with_pubs = api.search_author_with_publications(
        name=name, scholar_id=author.scholar_id, full=False, backend=backend
    )
    cache.save_author(author=author_with_pubs, cache_dir=cache_dir)


@app.command(help="Remove author")
def remove_author(name: str, cache_dir: str = config.DEFAULT_CACHE_DIR):
    authors_file = Path(cache_dir) / "authors.json"
    authors = json.loads(authors_file.read_text())
    if name not in authors:
        closest_name = api.get_closest_name(name, authors.keys())
        typer.echo(
            f"Could not find author with name '{name}'. Did you mean '{closest_name}'?",
            err=True,
        )
        raise typer.Exit(103)

    authors.pop(name)
    authors_file.write_text(json.dumps(authors, indent=4))
    typer.echo(f"Successfully removed author with name {name}")


def print_publications(publications, sort_by_citations, add_authors, name):
    sort_txt = "(Sorted by "
    if sort_by_citations:
        sort_txt += "citations)"
    else:
        sort_txt += "age)"
    table = Table(title=f"Publications for {name} {sort_txt}")
    table.add_column("Title", style="cyan")
    if add_authors:
        table.add_column("Authors", style="magenta")
    table.add_column("Published year", style="green")
    table.add_column("Number of citations", style="yellow")
    for pub in publications:
        try:
            year = str(pub.year)
        except ValueError:
            year = "Unknown"
        if add_authors:
            if pub.authors == "":
                full_pub = pub.fill()
            else:
                full_pub = pub
            table.add_row(pub.title, full_pub.authors, year, str(pub.num_citations))
        else:
            table.add_row(pub.title, year, str(pub.num_citations))

    console = Console()
    console.print(table)


@app.command(help="List authors publications")
def list_author_publications(
    name: str,
    n: int = 5,
    sort_by_citations: bool = True,
    add_authors: bool = False,
    max_age: Optional[int] = None,
    update: bool = False,
    overwrite: bool = False,
    cache_dir: str = config.DEFAULT_CACHE_DIR,
    backend: api.APIBackend = api.APIBackend.SCRAPER,
):
    authors = cache.load_authors(cache_dir)

    if name not in authors:
        _name = name
        name = api.get_closest_name(name, authors.keys())
        typer.echo(
            f"Could not find author with name '{_name}'. Will use '{name}' instead",
        )

    author = cache.load_author(authors[name], cache_dir=cache_dir)
    if update or author is None:
        author = api.search_author_with_publications(
            name=name, scholar_id=authors[name], full=False, backend=backend
        )
        if overwrite:
            cache.save_author(author=author, cache_dir=cache_dir)

    if author is None:
        typer.echo(f"Could not find author with name '{name}'", err=True)
        raise typer.Exit(105)

    publications = api.extract_correct_publications(author, sort_by_citations, max_age, n)
    print_publications(publications, sort_by_citations, add_authors, name)


@app.command(help="List new authors publications")
def list_new_author_publications(
    name: str,
    overwrite: bool = False,
    sort_by_citations: bool = True,
    add_authors: bool = False,
    cache_dir: str = config.DEFAULT_CACHE_DIR,
    save_diff: Optional[Path] = None,
    backend: api.APIBackend = api.APIBackend.SCRAPER,
):
    authors = cache.load_authors(cache_dir=cache_dir)

    if name not in authors:
        _name = name
        name = api.get_closest_name(name, authors.keys())
        typer.echo(
            f"Could not find author with name '{_name}'. Will use '{name}' instead",
        )

    author = api.search_author_with_publications(
        name=name,
        scholar_id=authors[name],
        backend=backend,
        full=False,
    )

    old_author = cache.load_author(author.scholar_id, cache_dir=cache_dir)
    if old_author is not None:
        old_titles = {pub.title for pub in old_author.publications}
    else:
        typer.echo(f"Could not find author with name '{name}'", err=True)
        old_titles = set()

    new_publications = [pub for pub in author.publications if pub.title not in old_titles]
    print_publications(new_publications, sort_by_citations, add_authors, name)

    if overwrite:
        cache.save_author(
            author=author,
            cache_dir=cache_dir,
        )

    if save_diff is not None:
        save_diff.with_suffix(".json").write_text(
            json.dumps([p.fill().dict() for p in new_publications], indent=4)
        )


@app.command(help="List department publications")
def list_department_publications(
    n: int = 5,
    sort_by_citations: bool = True,
    add_authors: bool = False,
    max_age: Optional[int] = None,
    update: bool = False,
    cache_dir: str = config.DEFAULT_CACHE_DIR,
    backend: api.APIBackend = api.APIBackend.SCRAPER,
):
    authors = cache.load_authors(cache_dir=cache_dir)

    all_authors = []
    for name, scholar_id in authors.items():
        author = cache.load_author(scholar_id, cache_dir=cache_dir)
        if author is None or update:
            author = api.search_author_with_publications(
                name=name, scholar_id=scholar_id, full=False, backend=backend
            )
            cache.save_author(author=author, cache_dir=cache_dir)
        all_authors.append(author)

    department = Department(authors=all_authors)
    publications = api.extract_correct_publications(department, sort_by_citations, max_age, n)
    print_publications(publications, sort_by_citations, add_authors, "department")


@app.command(help="List department publications")
def list_new_department_publications(
    n: int = 5,
    sort_by_citations: bool = True,
    add_authors: bool = False,
    max_age: Optional[int] = None,
    overwrite: bool = False,
    cache_dir: str = config.DEFAULT_CACHE_DIR,
    backend: api.APIBackend = api.APIBackend.SCRAPER,
):
    authors = cache.load_authors(cache_dir=cache_dir)

    old_authors = []
    new_authors = []
    for name, scholar_id in authors.items():
        old_author = cache.load_author(scholar_id, cache_dir=cache_dir)
        if old_author is not None:
            old_authors.append(old_author)

        new_author = api.search_author_with_publications(
            name=name, scholar_id=scholar_id, full=False, backend=backend
        )
        if overwrite:
            cache.save_author(author=new_author, cache_dir=cache_dir)
        new_authors.append(new_author)

    old_department = Department(authors=old_authors)
    new_department = Department(authors=new_authors)

    new_pubs = department_diff(
        new_department,
        old_department,
        fill=False,
    )

    print_publications(list(new_pubs.values()), sort_by_citations, add_authors, "department")


# @app.command(help="Post new publications for the department to Slack")
# def post_slack_new_dep_publications(
#     channel: str,
#     overwrite: bool = False,
#     cache_dir: str = config.DEFAULT_CACHE_DIR,
# ):
#     try:
#         from slack_sdk import WebClient
#     except ImportError as e:
#         msg = "Please install slack_sdg: 'pip install slack_sdk"
#         raise ImportError(msg) from e

#     config = configparser.ConfigParser()
#     if token := os.getenv("SLACK_BOT_TOKEN", ""):
#         config["SLACK_BOT_TOKEN"] = {"token": token}
#     else:
#         config.read([config.CONFIG_PATH, Path(cache_dir) / "config"])

#     try:
#         token = config.get("SLACK_BOT_TOKEN", "token")

#     except Exception as e:
#         msg = "Please set the 'SLACK_BOT_TOKEN'"
#         raise KeyError(msg) from e

#     dep, diff_dep = _get_new_dep(cache_dir)

#     client = WebClient(token=token)

#     for title, pub in diff_dep.items():
#         full_pub = pub.fill()

#         text = (
#             ":tada:*New publication by ComPhy team members!*\n"
#             ":star::confetti_ball::star::confetti_ball:\n"
#             f"*{title}* by _{full_pub.authors}_ "
#         )
#         if pub.bib.citation:
#             text += f"published in _{pub.bib.citation}_"

#         client.chat_postMessage(
#             channel=f"#{channel}",
#             text=text,
#             blocks=[
#                 {
#                     "type": "section",
#                     "text": {"type": "mrkdwn", "text": text},
#                 },
#                 {"type": "divider", "block_id": "divider1"},
#             ],
#         )

#     if overwrite:
#         utils.dump_json(dep.dict(), publications_file(cache_dir))
