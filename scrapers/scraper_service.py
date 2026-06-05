from scrapers.uom_scraper import UomNewsScraper


SCRAPER_REGISTRY = {
    "uom_news": UomNewsScraper,
}


def run_scraper(scraper_id: str) -> list[dict]:
    scraper_class = SCRAPER_REGISTRY.get(scraper_id)

    if scraper_class is None:
        raise ValueError(f"Unknown scraper: {scraper_id}")

    scraper = scraper_class()
    return scraper.scrape()