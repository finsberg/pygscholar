from __future__ import annotations
from typing import Any
from concurrent.futures import ThreadPoolExecutor
from structlog import get_logger
from selectolax.lexbor import LexborHTMLParser, LexborNode
from scholarly._navigator import Navigator

from ..author import AuthorInfo, Author
from ..publication import Publication


logger = get_logger()


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


def get_extra_article_info(link: str | None, driver: Navigator | None = None) -> dict[str, Any]:
    logger.debug(f"Getting extra info for {link}")

    if driver is None:
        driver = Navigator()

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
    driver: Navigator | None = None,
) -> dict[str, Any]:
    if driver is None:
        driver = Navigator()

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
    scholar_id: str, full: bool = True, driver: Navigator | None = None
) -> list[dict[str, Any]]:
    logger.debug(f"Extracting all articles for {scholar_id}")
    if driver is None:
        driver = Navigator()
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
                    results.append(executor.submit(process_article, article, full))

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


def extract_author_info(scholar_id: str, driver: Navigator | None = None) -> dict[str, Any]:
    logger.debug("Extracting author info")
    if driver is None:
        driver = Navigator()

    page_source = driver._get_page(
        f"https://scholar.google.com/citations?user={scholar_id}&hl=en&gl=us&pagesize=100"
    )
    parser = LexborHTMLParser(page_source)

    info: dict[str, Any] = {
        "info": {},
        "co-authors": [],
    }

    info["info"]["name"] = parser.css_first("#gsc_prf_in").text()
    info["info"]["affiliations"] = parser.css_first(".gsc_prf_ila").text()
    info["info"]["email"] = parser.css_first("#gsc_prf_ivh").text()
    info["info"]["interests"] = [interest.text() for interest in parser.css("#gsc_prf_int .gs_ibl")]

    citations = [int(c.text()) for c in parser.css(".gsc_rsb_std")]
    info["info"]["citations"] = {
        "all": citations[0],
        "last_5_years": citations[1],
    }
    info["info"]["h_index"] = {
        "all": citations[2],
        "last_5_years": citations[3],
    }
    info["info"]["i10_index"] = {
        "all": citations[4],
        "last_5_years": citations[5],
    }

    info["co-authors"] = extract_co_authors(parser)

    return info


def search_author(name: str, driver: Navigator | None = None) -> list[AuthorInfo]:
    logger.info(f"Searching for author {name}")
    if driver is None:
        driver = Navigator()

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
    name: str, scholar_id: str = "", driver: Navigator | None = None
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
    kwargs = author.dict()
    kwargs["data"] = info
    return AuthorInfo(**kwargs)


def search_author_with_publications(
    name: str,
    scholar_id: str = "",
    full: bool = False,
    driver: Navigator | None = None,
) -> Author:
    if driver is None:
        driver = Navigator()

    author = get_author(name, scholar_id, driver=driver)

    if author is None:
        raise RuntimeError(f"Could not find author '{name}' with id '{scholar_id}'")

    publications = list(
        map(
            to_publication,
            filter(
                lambda x: x["title"] is not None,
                extract_all_articles(author.scholar_id, full=full, driver=driver),
            ),
        )
    )
    info = update_author_info(author, driver=driver)

    return Author(info=info, publications=publications)


def fill_publication(publication: Publication, driver: Navigator | None = None) -> Publication:
    if driver is None:
        driver = Navigator()

    pub = get_extra_article_info(publication.scholar_url, driver=driver)
    kwargs = publication.dict()
    kwargs["extra"] = pub
    return to_publication(kwargs)
