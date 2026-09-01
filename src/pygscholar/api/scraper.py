from __future__ import annotations
from typing import Any, Protocol
import os
from concurrent.futures import ThreadPoolExecutor
from structlog import get_logger
from selectolax.lexbor import LexborHTMLParser, LexborNode
from scholarly._navigator import Navigator

from ..author import AuthorInfo, Author
from ..publication import Publication
from .local_db import LocalNavigator


logger = get_logger()


class NavigatorType(Protocol):
    def _get_page(self, link: str) -> str: ...


def get_driver(driver: NavigatorType | None = None) -> NavigatorType:
    """Use the recorded pages in LOCAL_DBPATH if it is set, otherwise go online."""
    if driver is not None:
        return driver

    local_db_path = os.getenv("LOCAL_DBPATH")
    if local_db_path:
        return LocalNavigator(local_db_path)
    return Navigator()


def to_publication(item: dict[str, Any]) -> Publication:
    # First get the basic information
    kwargs = {
        "title": item.get("title", ""),
        "year": item.get("publication_year", 0),
        "num_citations": item.get("cited_by_count", 0),
        "authors": item.get("authors", ""),
        "journal": item.get("publication", ""),
        "scholar_url": item.get("link", ""),
    }
    # In case the values are empty strings
    kwargs["num_citations"] = kwargs["num_citations"] or 0
    kwargs["year"] = kwargs["year"] or 0

    if "extra" not in item:
        return Publication(**kwargs)

    # Then get the extra information
    extra = item["extra"]

    kwargs.update(
        {
            "abstract": extra.get("description", ""),
            "authors": extra.get("authors", ""),
            "journal": extra.get("publication", ""),
            "volume": extra.get("volume", ""),
            "issue": extra.get("issue", ""),
            "pages": extra.get("pages", ""),
            "publisher": extra.get("publisher", ""),
            "pdf_url": extra.get("pdf_link", ""),
            "date": extra.get("publication_date", ""),
        }
    )

    return Publication(**{k: v for k, v in kwargs.items() if v is not None})


def get_extra_article_info(link: str | None, driver: NavigatorType | None = None) -> dict[str, Any]:
    logger.debug(f"Getting extra info for {link}")

    driver = get_driver(driver)

    if link is None:
        return {}

    page_source = driver._get_page(link)
    parser = LexborHTMLParser(page_source)

    fields = [g.text() for g in parser.css(".gsc_oci_field")]
    values = [g.text() for g in parser.css(".gsc_oci_value")]
    extra_info: dict[str, Any] = dict(zip(fields, values))
    try:
        extra_info["pdf_link"] = parser.css_first(".gsc_oci_title_ggi").child.attrs["href"]
    except AttributeError:
        logger.debug("Could not find PDF link")
        extra_info["pdf_link"] = ""

    return {k.replace(" ", "_").lower(): v for k, v in extra_info.items()}


_publication_fields = {
    ".gsc_a_at": "title",
    ".gsc_a_at+ .gs_gray": "authors",
    ".gs_gray+ .gs_gray": "publication",
    ".gsc_a_ac": "cited_by_count",
    ".gsc_a_hc": "publication_year",
}


def process_article(
    article: LexborNode,
    full: bool = True,
    driver: NavigatorType | None = None,
) -> dict[str, Any]:
    driver = get_driver(driver)

    article_dict = {
        value: getattr(article.css_first(key), "text", lambda: None)()
        for key, value in _publication_fields.items()
    }
    try:
        article_dict["link"] = (
            f"https://scholar.google.com{article.css_first('.gsc_a_at').attrs['href']}"
        )
    except AttributeError:
        article_dict["link"] = None

    if full:
        article_dict["extra"] = get_extra_article_info(article_dict["link"], driver)
    return article_dict


def extract_all_articles(
    scholar_id: str, full: bool = True, driver: NavigatorType | None = None
) -> list[dict[str, Any]]:
    logger.debug(f"Extracting all articles for {scholar_id}")
    driver = get_driver(driver)
    page_num = 0
    articles = []
    EOF = False

    while not EOF:
        page_source = driver._get_page(
            f"https://scholar.google.com/citations?user={scholar_id}&hl=en&gl=us&cstart={page_num}&pagesize=100"
        )
        parser = LexborHTMLParser(page_source)

        if full:
            # Use ThreadPoolExecutor to speed up the process
            results = []
            with ThreadPoolExecutor() as executor:
                for article in parser.css(".gsc_a_tr"):
                    results.append(executor.submit(process_article, article, full, driver))

            for result in results:
                articles.append(result.result())
        else:
            for article in parser.css(".gsc_a_tr"):
                articles.append(process_article(article, full, driver))

        if parser.css_first(".gsc_a_e"):
            EOF = True
        else:
            page_num += 100  # paginate to the next page
    return articles


def _text(parser: LexborHTMLParser, selector: str, default: str = "") -> str:
    node = parser.css_first(selector)
    return node.text() if node is not None else default


def extract_co_authors(parser: LexborHTMLParser) -> list[dict[str, str]]:
    logger.debug("Extracting co-authors")
    co_authors = []
    for co_author in parser.css(".gsc_rsb_aa"):
        co_authors.append(
            {
                "name": co_author.css_first(".gsc_rsb_a_desc a").text(),
                "profile_link": f"https://scholar.google.com{co_author.css_first('.gsc_rsb_a_desc a').attrs['href']}",  # noqa: E501
                "affiliation": co_author.css_first(".gsc_rsb_a_ext").text(),
            }
        )
    return co_authors


def extract_author_info(scholar_id: str, driver: NavigatorType | None = None) -> dict[str, Any]:
    logger.debug("Extracting author info")
    driver = get_driver(driver)

    page_source = driver._get_page(
        f"https://scholar.google.com/citations?user={scholar_id}&hl=en&gl=us&pagesize=100"
    )
    parser = LexborHTMLParser(page_source)

    info: dict[str, Any] = {
        "info": {},
        "co-authors": [],
    }

    name = _text(parser, "#gsc_prf_in")
    if name == "":
        # Most likely a captcha, a sign in page or an invalid scholar id
        raise RuntimeError(
            f"The page for scholar id '{scholar_id}' does not look like an author profile",
        )

    info["info"]["name"] = name
    info["info"]["affiliations"] = _text(parser, ".gsc_prf_ila")
    info["info"]["email"] = _text(parser, "#gsc_prf_ivh")
    info["info"]["interests"] = [interest.text() for interest in parser.css("#gsc_prf_int .gs_ibl")]

    # Authors without any citations yet have an empty statistics table
    citations = [int(c.text()) for c in parser.css(".gsc_rsb_std")]

    def stat(index: int) -> int:
        return citations[index] if index < len(citations) else 0

    info["info"]["citations"] = {
        "all": stat(0),
        "last_5_years": stat(1),
    }
    info["info"]["h_index"] = {
        "all": stat(2),
        "last_5_years": stat(3),
    }
    info["info"]["i10_index"] = {
        "all": stat(4),
        "last_5_years": stat(5),
    }

    info["co-authors"] = extract_co_authors(parser)

    return info


def name_variants(name: str) -> list[str]:
    """Query variants to look for, in decreasing order of precision.

    Google only shows the user profile panel for some queries. A full name such
    as "Henrik Nicolay Finsberg" gives no panel at all, while "Henrik Finsberg"
    does, so fall back to the first and the last name.
    """
    variants = [name]
    parts = name.split()
    if len(parts) > 2:
        variants.append(f"{parts[0]} {parts[-1]}")
    return variants


def parse_author_panel(parser: LexborHTMLParser) -> list[AuthorInfo]:
    """Parse the 'User profiles' panel of a search result page."""
    authors = []
    for author in parser.css(".gs_rt2"):
        anchor = author.css_first("a")
        if anchor is None:
            continue
        link = anchor.attrs.get("href", "")

        # The same cell holds affiliation, verified email and citation count
        details = [d.text() for d in author.parent.css("div")] if author.parent else []
        email = next((d for d in details if "email" in d.lower()), "")
        cited_by = next((d for d in details if d.lower().startswith("cited by")), "")
        affiliation = next((d for d in details if d not in (email, cited_by)), "")

        authors.append(
            AuthorInfo(
                name=anchor.text(),
                link=link,
                scholar_id=link.split("?user=")[-1].split("&")[0],
                affiliation=affiliation,
                email=email,
                cited_by=cited_by.lower().replace("cited by", "").replace(",", "").strip() or 0,
            )
        )
    return authors


def search_author(name: str, driver: NavigatorType | None = None) -> list[AuthorInfo]:
    logger.info(f"Searching for author {name}")
    driver = get_driver(driver)

    for variant in name_variants(name):
        query = variant.lower().replace(" ", "+")
        page_source = driver._get_page(
            f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={query}"
        )
        if not page_source:
            continue

        authors = parse_author_panel(LexborHTMLParser(page_source))
        if authors:
            if variant != name:
                logger.debug(f"Found no profiles for '{name}', used '{variant}' instead")
            logger.debug(f"Found {len(authors)} author(s)")
            return authors

    logger.debug("Found 0 author(s)")
    return []


# This function does not work anymore because Google Scholar now requires
# users to be logged in to see the author search results.
def search_author_orig(name: str, driver: NavigatorType | None = None) -> list[AuthorInfo]:
    logger.info(f"Searching for author {name}")
    driver = get_driver(driver)
    query = name.lower().replace(" ", "+")

    page_source = driver._get_page(
        f"https://scholar.google.com/citations?view_op=search_authors&hl=en&mauthors={query}"
    )
    parser = LexborHTMLParser(page_source)

    authors = []
    for author in parser.css(".gs_ai_t"):
        name = author.css_first(".gs_ai_name").text()
        link = author.css_first(".gs_ai_name").child.attrs["href"]
        scholar_id = link.split("&user=")[-1]
        affiliation = author.css_first(".gs_ai_aff").text()
        email = author.css_first(".gs_ai_eml").text()
        cited_by = author.css_first(".gs_ai_cby").text()

        authors.append(
            AuthorInfo(
                name=name,
                link=link,
                scholar_id=scholar_id,
                affiliation=affiliation,
                email=email,
                cited_by=cited_by.lstrip("Cited by "),
            )
        )
    logger.debug(f"Found {len(authors)} author(s)")

    return authors


def get_author(
    name: str, scholar_id: str = "", driver: NavigatorType | None = None
) -> AuthorInfo | None:
    logger.info(f"Get author info for {name}")
    authors = search_author(name, driver=driver)

    if len(authors) == 0:
        return None

    if scholar_id == "":
        return authors[0]

    for author in authors:
        if author.scholar_id == scholar_id:
            return author
    return None


def update_author_info(author: AuthorInfo, driver: Navigator) -> AuthorInfo:
    logger.info(f"Updating author info for {author.name}")
    info = extract_author_info(author.scholar_id, driver=driver)
    kwargs = author.model_dump()
    kwargs["data"] = info
    return AuthorInfo(**kwargs)


def author_info_from_id(scholar_id: str, driver: NavigatorType | None = None) -> AuthorInfo:
    """Build the author info from the profile page alone.

    Searching for an author is unreliable (see `search_author`), so whenever we
    already know the scholar id we skip the search entirely.
    """
    logger.info(f"Get author info for scholar id {scholar_id}")
    info = extract_author_info(scholar_id, driver=get_driver(driver))

    return AuthorInfo(
        name=info["info"]["name"],
        scholar_id=scholar_id,
        link=f"https://scholar.google.com/citations?user={scholar_id}&hl=en",
        affiliation=info["info"]["affiliations"],
        email=info["info"]["email"],
        cited_by=info["info"]["citations"]["all"],
        data=info,
    )


def search_author_with_publications(
    name: str,
    scholar_id: str = "",
    full: bool = False,
    driver: NavigatorType | None = None,
) -> Author:
    driver = get_driver(driver)

    if scholar_id != "":
        info = author_info_from_id(scholar_id, driver=driver)
    else:
        author = get_author(name, driver=driver)

        if author is None:
            raise RuntimeError(f"Could not find author '{name}' with id '{scholar_id}'")

        info = update_author_info(author, driver=driver)

    publications = list(
        map(
            to_publication,
            filter(
                lambda x: x["title"] is not None,
                extract_all_articles(info.scholar_id, full=full, driver=driver),
            ),
        )
    )

    return Author(info=info, publications=publications)


def fill_publication(publication: Publication, driver: NavigatorType | None = None) -> Publication:
    driver = get_driver(driver)

    pub = get_extra_article_info(publication.scholar_url, driver=driver)
    kwargs = publication.model_dump()
    kwargs["extra"] = pub
    return to_publication(kwargs)
