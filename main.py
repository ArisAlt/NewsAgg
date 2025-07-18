import requests
from bs4 import BeautifulSoup
import feedparser
from urllib.parse import urljoin
import re

# Configuration: list of news sources with precise CSS selectors and optional pagination
# You can optionally include 'max_pages' to cap the number of pages fetched per source
SOURCES = [
    {
        "name": "Kathimerini",
        "url": "https://www.kathimerini.gr/most-popular/",
        "parser": "html",
        "selector": "ul.most-popular-list li a",
        "pagination_param": "?page={page}",
        "max_pages": 3
    },
    {
        "name": "Proto Thema",
        "url": "https://www.protothema.gr/most-read/",
        "parser": "html",
        "selector": "div.article-list article h2 a",
        "pagination_selector": "a.next",
        "max_pages": 5
    },
    {
        "name": "In.gr",
        "url": "https://www.in.gr/most-viewed/",
        "parser": "html",
        "selector": "div.mostread-list li a",
        "pagination_param": "?page={page}"
    },
    {
        "name": "News247",
        "url": "https://www.news247.gr/most-popular/",
        "parser": "html",
        "selector": "div#most_popular ul li a"
    },
    {
        "name": "SKAI",
        "url": "https://www.skai.gr/most-popular/",
        "parser": "html",
        "selector": "div.module-content li a"
    },
    {
        "name": "Naftemporiki",
        "url": "https://www.naftemporiki.gr/most-popular/",
        "parser": "html",
        "selector": "div.popular-news li a"
    },
    {
        "name": "To Vima",
        "url": "https://www.tovima.gr/most-read/",
        "parser": "html",
        "selector": "section.popular-posts a.post-title"
    },
    {
        "name": "Ethnos",
        "url": "https://www.ethnos.gr/most-popular/",
        "parser": "html",
        "selector": "section.popular-news li a"
    },
    {
        "name": "Zougla",
        "url": "https://www.zougla.gr/most-popular/",
        "parser": "html",
        "selector": "ul.top10 li a"
    },
    {
        "name": "NewsIT",
        "url": "https://www.newsit.gr/most-popular/",
        "parser": "html",
        "selector": "div.view-most-popular .views-row a"
    }
]


def get_max_pages_from_soup(soup):
    """Detects the maximum page number from pagination links in a BeautifulSoup object."""
    pages = []
    for link in soup.select('a[href]'):
        href = link['href']
        match = re.search(r'page=(\d+)', href)
        if match:
            pages.append(int(match.group(1)))
    return max(pages) if pages else 1


def fetch_html_list(source, top_n=None):
    """Fetches and returns list of link dicts using selector and pagination if configured."""
    results = []

    def parse_page(url):
        resp = requests.get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        items = []
        for a in soup.select(source.get('selector', 'li a')):
            title = a.get_text(strip=True)
            href = a.get('href')
            if title and href:
                link = urljoin(source['url'], href)
                items.append({'title': title, 'link': link})
        return items, soup

    # Handle pagination by URL parameter
    if source.get('pagination_param'):
        # First page
        first_page_url = source['url'] + source['pagination_param'].format(page=1)
        items, soup = parse_page(first_page_url)
        results.extend(items)
        # Determine how many pages to fetch
        detected_max = get_max_pages_from_soup(soup)
        cap = source.get('max_pages') or detected_max
        total_pages = min(detected_max, cap)
        # Fetch subsequent pages up to the capped total
        for page in range(2, total_pages + 1):
            page_url = source['url'] + source['pagination_param'].format(page=page)
            items, _ = parse_page(page_url)
            results.extend(items)

    # Handle pagination by 'next' link
    elif source.get('pagination_selector'):
        next_url = source['url']
        pages_fetched = 0
        cap = source.get('max_pages', float('inf'))
        while next_url and pages_fetched < cap:
            items, soup = parse_page(next_url)
            results.extend(items)
            pages_fetched += 1
            next_link = soup.select_one(source['pagination_selector'])
            if next_link and next_link.get('href'):
                next_url = urljoin(source['url'], next_link['href'])
            else:
                break

    # No pagination
    else:
        items, _ = parse_page(source['url'])
        results = items

    # Limit to top_n if specified
    return results[:top_n] if top_n else results


def aggregate(top_n=10):
    """Aggregates most viewed news from configured sources, retrieving top_n per source."""
    aggregated = []
    for source in SOURCES:
        try:
            if source['parser'] == 'html':
                items = fetch_html_list(source, top_n)
            elif source['parser'] == 'rss':
                feed = feedparser.parse(source['url'])
                items = [{'title': e.title, 'link': e.link} for e in feed.entries[:top_n]]
            else:
                continue
            for item in items:
                aggregated.append({
                    'source': source['name'],
                    'title': item['title'],
                    'link': item['link']
                })
        except Exception as e:
            print(f"Error fetching {source['name']}: {e}")

    aggregated.sort(key=lambda x: (x['source'], x['title']))
    return aggregated


if __name__ == '__main__':
    news = aggregate()
    for idx, item in enumerate(news, start=1):
        print(f"{idx}. [{item['source']}] {item['title']} - {item['link']}")
