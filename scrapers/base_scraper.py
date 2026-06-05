from abc import ABC, abstractmethod


class BaseScraper(ABC):
    name: str = "Base Scraper"

    @abstractmethod
    def scrape(self) -> list[dict]:
        pass