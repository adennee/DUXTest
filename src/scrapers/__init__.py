"""News scraping module."""

from .rss_scraper import RSSFeedScraper
from .web_scraper import WebSearchScraper

__all__ = ["RSSFeedScraper", "WebSearchScraper"]
