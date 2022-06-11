__author__ = "Henrik Finsberg (henriknf@simula.no), 2017--2022"
__maintainer__ = "Henrik Finsberg"
__email__ = "henriknf@simula.no"
__program_name__ = "pyscolar"
__license__ = "MIT"
from pathlib import Path

import os


import typer
from rich.console import Console
from rich.table import Table


# from . import Department
# from . import scholar_api
from . import utils

DEFAULT_CACHE_DIR = os.getenv(
    "PYSCHOLAR_CACHE_DIR",
    Path.home().joinpath(".pyscholar").as_posix(),
)
app = typer.Typer()


def version_callback(show_version: bool):
    """Prints version information."""
    if show_version:
        from . import __version__

        typer.echo(f"{__program_name__} {__version__}")
        raise typer.Exit()


def license_callback(show_license: bool):
    """Prints license information."""
    if show_license:
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
def list_authors(cache_dir: str = DEFAULT_CACHE_DIR):
    authors_file = Path(cache_dir).joinpath("authors.json")
    authors = utils.load_json(authors_file)

    table = Table(title="Authors")

    table.add_column("Name", justify="right", style="cyan", no_wrap=True)
    table.add_column("Scholar ID", style="magenta")

    for name, scholar_id in authors.items():
        print(name)
        table.add_row(name, scholar_id)

    console = Console()
    console.print(table)


@app.command(help="Add new author")
def add_author(name: str, scholar_id: str, cache_dir: str = DEFAULT_CACHE_DIR):
    authors_file = Path(cache_dir).joinpath("authors.json")
    authors = utils.load_json(authors_file)

    if name in authors:
        typer.echo(f"Author with name {name} already exist in database", err=True)
        raise typer.Exit(101)
    if scholar_id in authors.values():
        typer.echo("There is already an author with the provided scholar id", err=True)
        raise typer.Exit(102)
    authors[name] = scholar_id
    utils.dump_json(authors, authors_file)
    typer.echo(
        f"Successfully added author with name {name} and scholar id {scholar_id}",
    )


# def compute_todays_impact(history_file, pubs_file, people):

#     # breakpoint()
#     old_pubs = load_json(pubs_file)
#     old_dep: Optional[Department] = None
#     if old_pubs:
#         old_dep = Department(**old_pubs)

#     # Load database
#     history = load_json(history_file)

#     dep = scholar_api.extract_scholar_publications(people)

#     # pubs = dep.publications
#     aut = dep.get_author_by_name("Henrik Nicolay Finsberg")
#     breakpoint()
#     # aut = dep.get_author_by_name("Henrik Nicolay Finsberg")
#     # pub = aut.most_cited()

#     if old_dep is None:
#         old_dep = dep

#     dep_diff = scholar.department_diff(dep, old_dep, fill=True)
#     #
#     breakpoint()
#     dump_json(dep.dict(), pubs_file)


# def main_func(args):

#     cache_dir = Path(args["cache_dir"]).expanduser()
#     cache_dir.mkdir(parents=True, exist_ok=True)

#     history_file = cache_dir.joinpath("history.json")
#     people_file = cache_dir.joinpath("people.json")
#     pubs_file = cache_dir.joinpath("publications.json")

#     # Import input data
#     people = utils.load_json(people_file)

#     if not people_file.is_file():
#         print(f"No peoople found in {people_file}")
#         sys.exit()

#     compute_todays_impact(history_file, pubs_file, people)


# def get_args():

#     descr = "Get citations from the Computational Physiology group"
#     parser = argparse.ArgumentParser(description=descr, add_help=True)

#     parser.add_argument(
#         "--cache-dir",
#         action="store",
#         dest="cache_dir",
#         default=Path.home().joinpath(".pyscholar").as_posix(),
#         type=str,
#         help="Which folder to store the cached data",
#     )

#     return parser


# def main():
#     parser = get_args()
#     args = vars(parser.parse_args())
#     print(args)
#     main_func(args)
