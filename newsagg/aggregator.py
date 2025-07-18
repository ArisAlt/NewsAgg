"""Core aggregation logic for NewsAgg.

This module fetches headlines from various Greek news outlets and now also
retrieves a short text preview for each entry.
"""

from __future__ import annotations

import logging
import os
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
        "url": "https://www.kathimerini.gr/infeeds/popular/popular_html.txt",
        "parser": "json_html",
        "selector": "ul.nx-dhmofilh__list li a",
        "json_key": "popular",
    },
    {
        "name": "Proto Thema",
        "url": "https://www.protothema.gr/rss/",
        "parser": "rss",
    },
    {
        "name": "In.gr",
        "url": "https://www.in.gr/feed",
        "parser": "rss",
    },
    {
        "name": "News247",
        "url": "https://www.news247.gr",
        "parser": "html",
        "selector": "section.popular_articles_section article a",
    },
    {
        "name": "SKAI",
        "url": "https://www.skai.gr/feed.xml",
        "parser": "rss",
    },
    {
        "name": "Naftemporiki",
        "url": "https://www.naftemporiki.gr/feed/",
        "parser": "rss",
    },
    {
        "name": "To Vima",
        "url": "https://www.tovima.gr/feed",
        "parser": "rss",
    },
    {
        "name": "Ethnos",
        "url": "https://www.ethnos.gr/rss",
        "parser": "rss",
    },
    {
        "name": "Zougla",
        "url": "https://www.zougla.gr/feed/",
        "parser": "rss",
    },
    {
        "name": "NewsIT",
        "url": "https://www.newsit.gr/feed/",
        "parser": "rss",
    },
]


from . import __version__

FILE_PATH = os.path.abspath(__file__)
FILE_VERSION = __version__

_SESSION = requests.Session()
_SESSION.headers.update({"User-Agent": f"NewsAgg/{__version__}"})


def extract_preview(url: str) -> str:
    """Return a short text preview for an article."""
    try:
        resp = _SESSION.get(url, timeout=5)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        meta = soup.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            text = meta["content"]
        else:
            para = soup.find("p")
            text = para.get_text(strip=True) if para else ""
        return text[:200]
    except Exception as exc:  # pylint: disable=broad-except
        logger.debug("Preview error %s: %s", url, exc)
        return ""


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
            preview = extract_preview(link)
            items.append({"title": title, "link": link, "preview": preview})
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


def fetch_json_html_list(source: Dict[str, str], top_n: int | None = None) -> List[Dict[str, str]]:
    """Fetch list of links from a JSON endpoint containing HTML."""
    resp = _SESSION.get(source["url"])
    resp.raise_for_status()
    data = resp.json()
    html = data.get(source.get("json_key", "html"), "")
    soup = BeautifulSoup(html, "html.parser")
    items = []
    selector = source.get("selector", "li a")
    for a in soup.select(selector):
        title = a.get_text(strip=True)
        href = a.get("href")
        if title and href:
            link = urljoin(source["url"], href)
            preview = extract_preview(link)
            items.append({"title": title, "link": link, "preview": preview})
    return items[:top_n] if top_n else items


def aggregate(top_n: int = 10) -> List[Dict[str, str]]:
    """Aggregate most viewed news from configured sources."""
    aggregated: List[Dict[str, str]] = []
    for source in SOURCES:
        try:
            if source["parser"] == "html":
                items = fetch_html_list(source, top_n)
            elif source["parser"] == "json_html":
                items = fetch_json_html_list(source, top_n)
            elif source["parser"] == "rss":
                feed = feedparser.parse(source["url"])
                items = []
                for e in feed.entries[:top_n]:
                    preview = getattr(e, "summary", None) or getattr(e, "description", "")
                    if preview:
                        preview = BeautifulSoup(preview, "html.parser").get_text(strip=True)[:200]
                    else:
                        preview = extract_preview(e.link)
                    items.append({"title": e.title, "link": e.link, "preview": preview})
            else:
                logger.warning("Unknown parser for %s", source["name"])
                continue
            for item in items:
                aggregated.append({
                    "source": source["name"],
                    "title": item["title"],
                    "link": item["link"],
                    "preview": item.get("preview", ""),
                })
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Error fetching %s: %s", source["name"], exc)

    aggregated.sort(key=lambda x: (x["source"], x["title"]))
    return aggregated
