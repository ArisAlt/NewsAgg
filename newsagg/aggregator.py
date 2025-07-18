"""Core aggregation logic for NewsAgg."""

from __future__ import annotations

import logging
import re
from typing import List, Dict, Tuple
from urllib.parse import urljoin

import feedparser
import requests
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)

# Configuration: list of news sources with precise CSS selectors and optional pagination
# You can optionally include 'max_pages' to cap the number of pages fetched per source
SOURCES = [
    {
        "name": "Kathimerini",
        "url": "https://www.kathimerini.gr/most-popular/",
        "parser": "html",
        "selector": "ul.most-popular-list li a",
        "pagination_param": "?page={page}",
        "max_pages": 3,
    },
    {
        "name": "Proto Thema",
        "url": "https://www.protothema.gr/most-read/",
        "parser": "html",
        "selector": "div.article-list article h2 a",
        "pagination_selector": "a.next",
        "max_pages": 5,
    },
    {
        "name": "In.gr",
        "url": "https://www.in.gr/most-viewed/",
        "parser": "html",
        "selector": "div.mostread-list li a",
        "pagination_param": "?page={page}",
    },
    {
        "name": "News247",
        "url": "https://www.news247.gr/most-popular/",
        "parser": "html",
        "selector": "div#most_popular ul li a",
    },
    {
        "name": "SKAI",
        "url": "https://www.skai.gr/most-popular/",
        "parser": "html",
        "selector": "div.module-content li a",
    },
    {
        "name": "Naftemporiki",
        "url": "https://www.naftemporiki.gr/most-popular/",
        "parser": "html",
        "selector": "div.popular-news li a",
    },
    {
        "name": "To Vima",
        "url": "https://www.tovima.gr/most-read/",
        "parser": "html",
        "selector": "section.popular-posts a.post-title",
    },
    {
        "name": "Ethnos",
        "url": "https://www.ethnos.gr/most-popular/",
        "parser": "html",
        "selector": "section.popular-news li a",
    },
    {
        "name": "Zougla",
        "url": "https://www.zougla.gr/most-popular/",
        "parser": "html",
        "selector": "ul.top10 li a",
    },
    {
        "name": "NewsIT",
        "url": "https://www.newsit.gr/most-popular/",
        "parser": "html",
        "selector": "div.view-most-popular .views-row a",
    },
]


from . import __version__

_SESSION = requests.Session()
_SESSION.headers.update({"User-Agent": f"NewsAgg/{__version__}"})


def get_max_pages_from_soup(soup: BeautifulSoup) -> int:
    """Detect the maximum page number from pagination links."""
    pages = []
    for link in soup.select("a[href]"):
        href = link["href"]
        match = re.search(r"page=(\d+)", href)
        if match:
            pages.append(int(match.group(1)))
    return max(pages) if pages else 1


def _parse_page(url: str, selector: str) -> Tuple[List[Dict[str, str]], BeautifulSoup]:
    resp = _SESSION.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    items = []
    for a in soup.select(selector):
        title = a.get_text(strip=True)
        href = a.get("href")
        if title and href:
            link = urljoin(url, href)
            items.append({"title": title, "link": link})
    return items, soup


def fetch_html_list(source: Dict[str, str], top_n: int | None = None) -> List[Dict[str, str]]:
    """Fetch list of links from a source that provides HTML."""
    results: List[Dict[str, str]] = []
    selector = source.get("selector", "li a")

    if source.get("pagination_param"):
        first_page_url = source["url"] + source["pagination_param"].format(page=1)
        items, soup = _parse_page(first_page_url, selector)
        results.extend(items)
        detected_max = get_max_pages_from_soup(soup)
        cap = source.get("max_pages") or detected_max
        total_pages = min(detected_max, cap)
        for page in range(2, total_pages + 1):
            page_url = source["url"] + source["pagination_param"].format(page=page)
            items, _ = _parse_page(page_url, selector)
            results.extend(items)
    elif source.get("pagination_selector"):
        next_url = source["url"]
        pages_fetched = 0
        cap = source.get("max_pages", float("inf"))
        while next_url and pages_fetched < cap:
            items, soup = _parse_page(next_url, selector)
            results.extend(items)
            pages_fetched += 1
            next_link = soup.select_one(source["pagination_selector"])
            if next_link and next_link.get("href"):
                next_url = urljoin(source["url"], next_link["href"])
            else:
                break
    else:
        items, _ = _parse_page(source["url"], selector)
        results = items

    return results[:top_n] if top_n else results


def aggregate(top_n: int = 10) -> List[Dict[str, str]]:
    """Aggregate most viewed news from configured sources."""
    aggregated: List[Dict[str, str]] = []
    for source in SOURCES:
        try:
            if source["parser"] == "html":
                items = fetch_html_list(source, top_n)
            elif source["parser"] == "rss":
                feed = feedparser.parse(source["url"])
                items = [
                    {"title": e.title, "link": e.link} for e in feed.entries[:top_n]
                ]
            else:
                logger.warning("Unknown parser for %s", source["name"])
                continue
            for item in items:
                aggregated.append({
                    "source": source["name"],
                    "title": item["title"],
                    "link": item["link"],
                })
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Error fetching %s: %s", source["name"], exc)

    aggregated.sort(key=lambda x: (x["source"], x["title"]))
    return aggregated
