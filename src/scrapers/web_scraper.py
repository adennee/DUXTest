"""Web search scraper for finding relevant articles by keywords."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
import pytz

from ..models.news import NewsArticle
from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class WebSearchScraper:
    """Scraper for finding articles via web search."""

    def __init__(self):
        """Initialize web search scraper."""
        settings = get_settings()
        self.api_key = settings.news_api_key
        self.keywords = settings.search_keywords
        logger.info(f"Initialized web scraper with {len(self.keywords)} keywords")

    def search_by_keyword(self, keyword: str, days_back: int = 7) -> List[NewsArticle]:
        """
        Search for articles matching a keyword.

        Args:
            keyword: Search keyword
            days_back: Only include articles from the last N days

        Returns:
            List of NewsArticle objects
        """
        articles = []

        # Use News API if available
        if self.api_key:
            articles = self._search_news_api(keyword, days_back)
        else:
            logger.info("No News API key configured, skipping web search")

        return articles

    def search_all_keywords(self, days_back: int = 7, max_per_keyword: int = 3, max_keywords: int = 3) -> List[NewsArticle]:
        """
        Search for articles matching configured keywords.

        Args:
            days_back: Only include articles from the last N days
            max_per_keyword: Maximum articles per keyword (default: 3)
            max_keywords: Maximum number of keywords to search (default: 3)

        Returns:
            List of all NewsArticle objects
        """
        all_articles = []
        seen_urls = set()

        # Limit to first N keywords to conserve API calls
        limited_keywords = self.keywords[:max_keywords]
        logger.info(f"Searching {len(limited_keywords)} keywords (limited from {len(self.keywords)} to conserve API calls)")

        for keyword in limited_keywords:
            articles = self.search_by_keyword(keyword, days_back)

            # Deduplicate by URL
            for article in articles[:max_per_keyword]:
                url_str = str(article.url)
                if url_str not in seen_urls:
                    seen_urls.add(url_str)
                    all_articles.append(article)

        logger.info(f"Found {len(all_articles)} unique articles from web search")
        return all_articles

    def _search_news_api(self, keyword: str, days_back: int) -> List[NewsArticle]:
        """
        Search using News API (newsapi.org).

        Args:
            keyword: Search keyword
            days_back: Days to search back

        Returns:
            List of NewsArticle objects
        """
        articles = []

        try:
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days_back)

            # Build API request
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": keyword,
                "from": from_date.strftime("%Y-%m-%d"),
                "to": to_date.strftime("%Y-%m-%d"),
                "language": "en",
                "sortBy": "publishedAt",
                "apiKey": self.api_key,
            }

            logger.info(f"Searching News API for: {keyword}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get("status") != "ok":
                logger.error(f"News API error: {data.get('message')}")
                return articles

            # Parse articles
            for item in data.get("articles", []):
                try:
                    # Parse date
                    pub_date_str = item.get("publishedAt")
                    pub_date = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00")) if pub_date_str else datetime.now(pytz.UTC)

                    article = NewsArticle(
                        title=item.get("title", "Untitled"),
                        url=item.get("url", ""),
                        published_date=pub_date,
                        source=item.get("source", {}).get("name", "Unknown"),
                        summary=item.get("description", ""),
                        content=item.get("content", ""),
                        author=item.get("author"),
                    )

                    articles.append(article)

                except Exception as e:
                    logger.error(f"Error parsing News API result: {e}")
                    continue

            logger.info(f"Found {len(articles)} articles for '{keyword}'")

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP error searching News API: {e}")
        except Exception as e:
            logger.error(f"Error searching News API: {e}")

        return articles

    def fetch_full_content(self, article: NewsArticle) -> NewsArticle:
        """
        Fetch full article content from URL.

        Args:
            article: NewsArticle with URL

        Returns:
            Updated NewsArticle with full content
        """
        if article.content and len(article.content) > 500:
            return article  # Already has content

        try:
            logger.debug(f"Fetching full content for: {article.url}")
            response = requests.get(str(article.url), timeout=10)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "aside"]):
                script.decompose()

            # Try to find main content
            content_tags = soup.find_all(["article", "main", "div"], class_=lambda x: x and any(
                keyword in x.lower() for keyword in ["content", "article", "post", "entry"]
            ))

            if content_tags:
                content = " ".join([tag.get_text(separator=" ", strip=True) for tag in content_tags])
            else:
                # Fallback to all paragraphs
                paragraphs = soup.find_all("p")
                content = " ".join([p.get_text(strip=True) for p in paragraphs])

            # Clean up whitespace
            content = " ".join(content.split())

            if content:
                article.content = content[:10000]  # Limit content length
                logger.debug(f"Fetched {len(content)} characters of content")

        except Exception as e:
            logger.warning(f"Failed to fetch content for {article.url}: {e}")

        return article
