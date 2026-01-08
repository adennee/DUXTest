"""Company release scraper for tracking competitor product announcements."""

import logging
from datetime import datetime, timedelta
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import feedparser
import pytz

from ..models.news import NewsArticle
from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class CompanyReleaseScraper:
    """Scraper for tracking product releases from competitor companies."""

    def __init__(self):
        """Initialize company release scraper."""
        settings = get_settings()
        self.companies = settings.competitor_companies
        self.release_keywords = settings.release_keywords
        self.news_api_key = settings.news_api_key
        logger.info(f"Initialized company release scraper for {len(self.companies)} companies")

    def scrape_all_companies(self, days_back: int = 14) -> List[NewsArticle]:
        """
        Scrape releases from all tracked companies.

        Args:
            days_back: Number of days to look back (default: 14 for releases)

        Returns:
            List of NewsArticle objects containing product releases
        """
        all_releases = []
        seen_urls = set()

        for company in self.companies:
            try:
                logger.info(f"Checking releases for {company['name']}")
                releases = self._scrape_company(company, days_back)

                # Deduplicate by URL
                for release in releases:
                    url_str = str(release.url)
                    if url_str not in seen_urls:
                        seen_urls.add(url_str)
                        all_releases.append(release)

            except Exception as e:
                logger.error(f"Error scraping {company['name']}: {e}")
                continue

        logger.info(f"Found {len(all_releases)} total product releases")
        return all_releases

    def _scrape_company(self, company: Dict, days_back: int) -> List[NewsArticle]:
        """
        Scrape releases for a single company.

        Args:
            company: Company configuration dict
            days_back: Number of days to look back

        Returns:
            List of NewsArticle objects
        """
        releases = []

        # Method 1: Search via News API
        if self.news_api_key:
            releases.extend(self._search_via_news_api(company, days_back))

        # Method 2: Try to find RSS feed from blog URL
        releases.extend(self._try_blog_rss(company, days_back))

        # Method 3: Search for press releases
        releases.extend(self._search_press_releases(company, days_back))

        return releases

    def _search_via_news_api(self, company: Dict, days_back: int) -> List[NewsArticle]:
        """
        Search for company releases using News API.

        Args:
            company: Company configuration
            days_back: Number of days to look back

        Returns:
            List of NewsArticle objects
        """
        releases = []

        if not self.news_api_key:
            return releases

        try:
            # Build search query with company name and release keywords
            company_names = [company['name']] + company.get('aliases', [])

            # Search for each release keyword
            for keyword in ['launches', 'announces', 'releases']:
                for name in company_names[:2]:  # Limit to avoid too many queries
                    query = f'"{name}" {keyword} healthcare OR "life sciences"'

                    # Calculate date range
                    to_date = datetime.now()
                    from_date = to_date - timedelta(days=days_back)

                    url = "https://newsapi.org/v2/everything"
                    params = {
                        "q": query,
                        "from": from_date.strftime("%Y-%m-%d"),
                        "to": to_date.strftime("%Y-%m-%d"),
                        "language": "en",
                        "sortBy": "publishedAt",
                        "pageSize": 5,  # Limit per query
                        "apiKey": self.news_api_key,
                    }

                    response = requests.get(url, params=params, timeout=10)
                    response.raise_for_status()

                    data = response.json()

                    if data.get("status") != "ok":
                        continue

                    # Parse articles
                    for item in data.get("articles", []):
                        try:
                            pub_date_str = item.get("publishedAt")
                            pub_date = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00")) if pub_date_str else datetime.now(pytz.UTC)

                            article = NewsArticle(
                                title=item.get("title", "Untitled"),
                                url=item.get("url", ""),
                                published_date=pub_date,
                                source=item.get("source", {}).get("name", company['name']),
                                summary=item.get("description", ""),
                                content=item.get("content", ""),
                                author=item.get("author"),
                                tags=["Product Release", company['name']],
                            )

                            releases.append(article)

                        except Exception as e:
                            logger.error(f"Error parsing News API result: {e}")
                            continue

            logger.info(f"Found {len(releases)} releases for {company['name']} via News API")

        except Exception as e:
            logger.error(f"Error searching News API for {company['name']}: {e}")

        return releases

    def _try_blog_rss(self, company: Dict, days_back: int) -> List[NewsArticle]:
        """
        Try to find and parse RSS feed from company blog.

        Args:
            company: Company configuration
            days_back: Number of days to look back

        Returns:
            List of NewsArticle objects
        """
        releases = []
        blog_url = company.get('blog_url')

        if not blog_url:
            return releases

        # Common RSS feed patterns to try
        rss_patterns = [
            f"{blog_url}/feed",
            f"{blog_url}/rss",
            f"{blog_url}/feed.xml",
            f"{blog_url}/rss.xml",
            blog_url if 'feed' in blog_url or 'rss' in blog_url else None,
        ]

        cutoff_date = datetime.now(pytz.UTC) - timedelta(days=days_back)

        for rss_url in rss_patterns:
            if not rss_url:
                continue

            try:
                logger.debug(f"Trying RSS feed: {rss_url}")
                feed = feedparser.parse(rss_url)

                if feed.bozo:
                    continue

                for entry in feed.entries:
                    try:
                        # Parse publication date
                        pub_date = self._parse_date(entry)

                        # Skip if too old
                        if pub_date and pub_date < cutoff_date:
                            continue

                        # Check if entry contains release keywords
                        title = entry.get("title", "").lower()
                        summary = entry.get("summary", "").lower()

                        if not any(keyword in title or keyword in summary for keyword in self.release_keywords):
                            continue

                        # Check if healthcare/life sciences related
                        content = f"{title} {summary}".lower()
                        if not any(term in content for term in ['healthcare', 'health', 'life sciences', 'medical', 'clinical', 'patient']):
                            continue

                        # Extract content
                        full_content = self._extract_content(entry)

                        article = NewsArticle(
                            title=entry.get("title", "Untitled"),
                            url=entry.get("link", ""),
                            published_date=pub_date or datetime.now(pytz.UTC),
                            source=company['name'],
                            summary=entry.get("summary", ""),
                            content=full_content,
                            author=entry.get("author", None),
                            tags=["Product Release", company['name']],
                        )

                        releases.append(article)

                    except Exception as e:
                        logger.error(f"Error parsing feed entry: {e}")
                        continue

                # If we found entries, don't try other patterns
                if releases:
                    logger.info(f"Found {len(releases)} releases from {company['name']} RSS feed")
                    break

            except Exception as e:
                logger.debug(f"Could not access RSS at {rss_url}: {e}")
                continue

        return releases

    def _search_press_releases(self, company: Dict, days_back: int) -> List[NewsArticle]:
        """
        Search for press releases via web search.

        Args:
            company: Company configuration
            days_back: Number of days to look back

        Returns:
            List of NewsArticle objects
        """
        releases = []

        # This would require a web search API or scraping
        # For now, we'll rely on News API and RSS feeds
        # Could be extended with Google Custom Search API or similar

        return releases

    def _parse_date(self, entry) -> datetime:
        """Parse publication date from feed entry."""
        from dateutil import parser as date_parser

        date_str = entry.get("published") or entry.get("updated")

        if not date_str:
            return datetime.now(pytz.UTC)

        try:
            dt = date_parser.parse(date_str)
            if dt.tzinfo is None:
                dt = pytz.UTC.localize(dt)
            return dt
        except Exception as e:
            logger.warning(f"Failed to parse date '{date_str}': {e}")
            return datetime.now(pytz.UTC)

    def _extract_content(self, entry) -> str:
        """Extract content from feed entry."""
        import re

        content = ""

        if hasattr(entry, "content") and entry.content:
            content = entry.content[0].get("value", "")
        elif hasattr(entry, "description"):
            content = entry.description
        elif hasattr(entry, "summary"):
            content = entry.summary

        if content:
            content = re.sub(r"<[^>]+>", "", content)
            content = content.strip()

        return content
