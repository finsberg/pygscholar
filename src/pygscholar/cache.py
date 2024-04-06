from pathlib import Path
import json
from structlog import get_logger

logger = get_logger()


def check_cache_dir_and_create(cache_dir: str) -> None:
    cachedir = Path(cache_dir)
    if not cachedir.is_dir():
        logger.info(f"Cache dir {cachedir} does not exist. Creating...")
        cachedir.mkdir(parents=True)


def authors_file(cache_dir: str) -> Path:
    return Path(cache_dir) / "authors.json"


def load_authors(cache_dir: str) -> dict[str, str]:
    check_cache_dir_and_create(cache_dir)

    if not authors_file(cache_dir).is_file():
        return {}
    return json.loads(authors_file(cache_dir).read_text())


def save_authors(authors: dict[str, str], cache_dir: str) -> None:
    check_cache_dir_and_create(cache_dir)
    original_authors = load_authors(cache_dir)
    original_authors.update(authors)
    authors_file(cache_dir).write_text(json.dumps(original_authors, indent=4))
