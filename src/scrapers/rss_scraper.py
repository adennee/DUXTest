"""RSS feed scraper for collecting news articles."""

import logging
from datetime import datetime, timedelta
from typing import List
import feedparser
from dateutil import parser as date_parser
import pytz

from ..models.news import NewsArticle

logger = logging.getLogger(__name__)


class RSSFeedScraper:
    """Scraper for collecting articles from RSS feeds."""

    def __init__(self, feeds: List[str]):
        """
        Initialize RSS feed scraper.

        Args:
            feeds: List of RSS feed URLs
        """
        self.feeds = feeds
        logger.info(f"Initialized RSS scraper with {len(feeds)} feeds")

    def scrape_feed(self, feed_url: str, days_back: int = 7) -> List[NewsArticle]:
        """
        Scrape articles from a single RSS feed.

        Args:
            feed_url: URL of the RSS feed
            days_back: Only include articles from the last N days

        Returns:
            List of NewsArticle objects
        """
        articles = []
        cutoff_date = datetime.now(pytz.UTC) - timedelta(days=days_back)

        try:
            logger.info(f"Fetching feed: {feed_url}")
            feed = feedparser.parse(feed_url)

            if feed.bozo:
                logger.warning(f"Feed parsing error for {feed_url}: {feed.bozo_exception}")

            for entry in feed.entries:
                try:
                    # Parse publication date
                    pub_date = self._parse_date(entry)

                    # Skip if too old
                    if pub_date and pub_date < cutoff_date:
                        continue

                    # Extract content
                    content = self._extract_content(entry)
                    summary = entry.get("summary", "")

                    # Create article object
                    article = NewsArticle(
                        title=entry.get("title", "Untitled"),
                        url=entry.get("link", ""),
                        published_date=pub_date or datetime.now(pytz.UTC),
                        source=feed.feed.get("title", feed_url),
                        summary=summary,
                        content=content,
                        author=entry.get("author", None),
                    )

                    articles.append(article)
                    logger.debug(f"Scraped article: {article.title}")

                except Exception as e:
                    logger.error(f"Error parsing feed entry: {e}")
                    continue

            logger.info(f"Scraped {len(articles)} articles from {feed_url}")

        except Exception as e:
            logger.error(f"Error fetching feed {feed_url}: {e}")

        return articles

    def scrape_all_feeds(self, days_back: int = 7) -> List[NewsArticle]:
        """
        Scrape articles from all configured RSS feeds.

        Args:
            days_back: Only include articles from the last N days

        Returns:
            List of all NewsArticle objects
        """
        all_articles = []

        for feed_url in self.feeds:
            articles = self.scrape_feed(feed_url, days_back)
            all_articles.extend(articles)

        logger.info(f"Total articles scraped: {len(all_articles)}")
        return all_articles

    def _parse_date(self, entry) -> datetime:
        """
        Parse publication date from feed entry.

        Args:
            entry: Feed entry object

        Returns:
            Parsed datetime object
        """
        date_str = entry.get("published") or entry.get("updated")

        if not date_str:
            return datetime.now(pytz.UTC)

        try:
            # Try to parse the date string
            dt = date_parser.parse(date_str)

            # Make timezone aware if naive
            if dt.tzinfo is None:
                dt = pytz.UTC.localize(dt)

            return dt

        except Exception as e:
            logger.warning(f"Failed to parse date '{date_str}': {e}")
            return datetime.now(pytz.UTC)

    def _extract_content(self, entry) -> str:
        """
        Extract content from feed entry.

        Args:
            entry: Feed entry object

        Returns:
            Article content text
        """
        # Try different content fields
        content = ""

        if hasattr(entry, "content") and entry.content:
            content = entry.content[0].get("value", "")
        elif hasattr(entry, "description"):
            content = entry.description
        elif hasattr(entry, "summary"):
            content = entry.summary

        # Basic HTML stripping (for simple cases)
        if content:
            # Remove common HTML tags
            import re
            content = re.sub(r"<[^>]+>", "", content)
            content = content.strip()

        return content
