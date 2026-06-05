from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper


class UomNewsScraper(BaseScraper):
    name = "University of Macedonia"

    def __init__(self):
        self.base_url = "https://www.uom.gr"

        self.sources = [
            {
                "label": "UoM Main News",
                "url": "https://www.uom.gr/nea",
                "pages": 2,
            },
            {
                "label": "UoM Economics",
                "url": "https://www.uom.gr/eco/ta-teleytaia-nea-toy-tmhmatos",
                "pages": 1,
            },
            {
                "label": "UoM Balkan, Slavic & Oriental Studies",
                "url": "https://www.uom.gr/bso/ta-nea-mas",
                "pages": 1,
            },
            {
                "label": "UoM Applied Informatics",
                "url": "https://www.uom.gr/dai/ta-nea-toy-tmhmatos",
                "pages": 1,
            },
            {
                "label": "UoM Business Administration",
                "url": "https://www.uom.gr/ba/enhmerosh",
                "pages": 1,
            },
            {
                "label": "UoM Accounting & Finance",
                "url": "https://www.uom.gr/fin/enhmerosh",
                "pages": 1,
            },
            {
                "label": "UoM International & European Studies",
                "url": "https://www.uom.gr/ies/ta-teleytaia-nea-toy-tmhmatos",
                "pages": 1,
            },
            {
                "label": "UoM Music Science & Art",
                "url": "https://www.uom.gr/msa/enhmerosh",
                "pages": 1,
            },
            {
                "label": "UoM Educational & Social Policy",
                "url": "https://www.uom.gr/esp/ta-nea-mas",
                "pages": 1,
            },
        ]

    def scrape(self) -> list[dict]:
        articles = []
        seen_links = set()

        for source in self.sources:
            source_articles = self.scrape_source(source)

            for article in source_articles:
                link = article.get("link")

                if link and link not in seen_links:
                    seen_links.add(link)
                    articles.append(article)

        return articles

    def scrape_source(self, source: dict) -> list[dict]:
        articles = []

        for page_number in range(1, source.get("pages", 1) + 1):
            page_url = self.build_page_url(source["url"], page_number)

            try:
                html = self.fetch_page(page_url)
                articles.extend(self.parse_page(html, source["label"]))
            except Exception as error:
                print(f"Could not scrape {page_url}: {error}")

        return articles

    def build_page_url(self, base_url: str, page_number: int) -> str:
        if page_number == 1:
            return base_url

        separator = "&" if "?" in base_url else "?"
        return f"{base_url}{separator}pn={page_number}"

    def fetch_page(self, url: str) -> str:
        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "UniNews/0.1 (+https://github.com/open-source-uom/UniNews)"
            },
        )

        response.raise_for_status()
        return response.text

    def parse_page(self, html: str, source_label: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        results = []

        news_items = soup.select("article.post-news.post-news-wide")

        for item in news_items:
            title_link = item.select_one("h6 a")

            if not title_link:
                continue

            title = title_link.get_text(strip=True)
            link = urljoin(self.base_url, title_link.get("href", ""))

            image = item.select_one("img")
            image_url = ""

            if image and image.get("src"):
                image_url = urljoin(self.base_url, image.get("src"))

            date_spans = item.select(".post-news-meta span.small")
            published = (
                date_spans[0].get_text(strip=True)
                if date_spans
                else "Unknown date"
            )

            results.append(
                {
                    "university": self.name,
                    "source": source_label,
                    "title": title,
                    "summary": source_label,
                    "link": link,
                    "published": published,
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "image_url": image_url,
                }
            )

        return results