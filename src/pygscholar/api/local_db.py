from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os
import json
from scholarly._navigator import Navigator
from selectolax.lexbor import LexborHTMLParser


@dataclass
class LocalNavigator:
    _dbname: Path | str | None

    def __post_init__(self):
        if self._dbname is None:
            self._dbname = Path(os.getenv("LOCAL_DBPATH"))
            assert self._dbname is not None, "LOCAL_DBPATH must be set"

        self.dbname = Path(self._dbname)
        if not self.dbname.is_file():
            self._db = {}
        else:
            self._db = json.loads(self.dbname.read_text())

    def _get_page(self, link: str):
        return self._db.get(link, None)

    def insert_page(self, link: str, page_source: str):
        self._db[link] = page_source
        self.dbname.write_text(json.dumps(self._db, indent=2))

    def search_author(self, name: str, driver: Navigator | None = None) -> str:
        if driver is None:
            driver = Navigator()

        print(f"Searching for author {name}")
        query = name.lower().replace(" ", "+")
        link = f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={query}"
        # link = f"https://scholar.google.com/citations?view_op=search_authors&hl=en&mauthors={query}"
        print(f"Fetching {link}")
        page_source = driver._get_page(link)
        self.insert_page(link, page_source)
        # scholar_id = (
        #     LexborHTMLParser(page_source)
        #     .css(".gs_ai_t")[0]
        #     .css_first(".gs_ai_name")
        #     .child.attrs["href"]
        #     .split("&user=")[-1]
        # )

        scholar_id = (
            LexborHTMLParser(page_source)
            .css(".gs_rt2")[0]
            .child.attrs["href"]
            .split("?user=")[-1]
            .split("&")[0]
        )
        return scholar_id

    def search_all_articles(self, name: str, driver: Navigator | None = None) -> None:
        if driver is None:
            driver = Navigator()
        scholar_id = self.search_author(name, driver)

        page_num = 0
        EOF = False
        while not EOF:
            link = f"https://scholar.google.com/citations?user={scholar_id}&hl=en&gl=us&cstart={page_num}&pagesize=100"
            print(f"Fetching {link}")
            page_source = driver._get_page(link)
            self.insert_page(link, page_source)
            paper_parser = LexborHTMLParser(page_source)
            for article in paper_parser.css(".gsc_a_tr"):
                try:
                    link = (
                        f"https://scholar.google.com{article.css_first('.gsc_a_at').attrs['href']}"
                    )
                except AttributeError:
                    continue
                else:
                    print(f"Fetching {link}")
                    page_source = driver._get_page(link)
                    self.insert_page(link, page_source)
            if paper_parser.css_first(".gsc_a_e"):
                EOF = True
            else:
                page_num += 100

    def populate_author(self, name: str) -> None:
        print(f"Populating author {name}")
        driver = Navigator()
        scholar_id = self.search_author(name, driver)
        link = f"https://scholar.google.com/citations?user={scholar_id}&hl=en&gl=us&pagesize=100"
        print(f"Fetching {link}")
        page_source = driver._get_page(link)
        self.insert_page(link, page_source)
        self.search_all_articles(name, driver)
