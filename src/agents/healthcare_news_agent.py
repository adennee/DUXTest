"""Main healthcare UX news aggregation agent."""

import logging
from datetime import datetime
from typing import List

from ..config.settings import get_settings
from ..models.news import NewsArticle
from ..integrations.notion_client import NotionClient
from ..integrations.claude_analyzer import ClaudeAnalyzer
from ..scrapers.rss_scraper import RSSFeedScraper
from ..scrapers.web_scraper import WebSearchScraper

logger = logging.getLogger(__name__)


class HealthcareNewsAgent:
    """Agent for collecting, analyzing, and publishing healthcare UX news."""

    def __init__(self):
        """Initialize the healthcare news agent."""
        self.settings = get_settings()

        # Initialize components
        self.notion = NotionClient()
        self.analyzer = ClaudeAnalyzer()
        self.rss_scraper = RSSFeedScraper(self.settings.rss_feeds)
        self.web_scraper = WebSearchScraper()

        logger.info("Healthcare News Agent initialized")

    def run(self, days_back: int = 7) -> dict:
        """
        Run the complete news aggregation workflow.

        Args:
            days_back: Number of days to look back for articles

        Returns:
            Summary statistics
        """
        logger.info(f"Starting news aggregation run (looking back {days_back} days)")

        stats = {
            "start_time": datetime.now().isoformat(),
            "articles_collected": 0,
            "articles_analyzed": 0,
            "articles_published": 0,
            "errors": []
        }

        try:
            # Step 1: Collect articles from sources
            logger.info("Step 1: Collecting articles from sources")
            articles = self._collect_articles(days_back)
            stats["articles_collected"] = len(articles)
            logger.info(f"Collected {len(articles)} articles")

            if not articles:
                logger.warning("No articles collected, exiting")
                return stats

            # Step 2: Analyze articles with Claude
            logger.info("Step 2: Analyzing articles for relevance")
            analyzed_articles = self._analyze_articles(articles)
            stats["articles_analyzed"] = len(analyzed_articles)

            # Step 3: Filter by relevance score
            logger.info("Step 3: Filtering by relevance score")
            relevant_articles = self._filter_relevant(analyzed_articles)
            logger.info(f"Found {len(relevant_articles)} relevant articles")

            # Step 4: Limit to max articles
            limited_articles = relevant_articles[:self.settings.max_articles_per_run]
            logger.info(f"Limited to top {len(limited_articles)} articles")

            # Step 5: Publish to Notion
            logger.info("Step 5: Publishing to Notion")
            published_count = self._publish_to_notion(limited_articles)
            stats["articles_published"] = published_count

            # Generate digest if we published articles
            if published_count > 0:
                logger.info("Generating executive digest")
                digest = self.analyzer.create_digest(limited_articles)
                logger.info("Digest created (not published separately)")

        except Exception as e:
            logger.error(f"Error in agent run: {e}")
            stats["errors"].append(str(e))

        stats["end_time"] = datetime.now().isoformat()
        logger.info(f"Agent run complete: {stats}")

        return stats

    def _collect_articles(self, days_back: int) -> List[NewsArticle]:
        """
        Collect articles from all sources.

        Args:
            days_back: Number of days to look back

        Returns:
            List of collected articles
        """
        articles = []

        # Collect from RSS feeds
        try:
            rss_articles = self.rss_scraper.scrape_all_feeds(days_back)
            articles.extend(rss_articles)
            logger.info(f"Collected {len(rss_articles)} articles from RSS feeds")
        except Exception as e:
            logger.error(f"Error collecting from RSS feeds: {e}")

        # Collect from web search (if API key available)
        try:
            if self.settings.news_api_key:
                web_articles = self.web_scraper.search_all_keywords(days_back)
                articles.extend(web_articles)
                logger.info(f"Collected {len(web_articles)} articles from web search")
        except Exception as e:
            logger.error(f"Error collecting from web search: {e}")

        # Deduplicate by URL
        seen_urls = set()
        unique_articles = []

        for article in articles:
            url_str = str(article.url)
            if url_str not in seen_urls:
                seen_urls.add(url_str)
                unique_articles.append(article)

        logger.info(f"Deduplicated to {len(unique_articles)} unique articles")
        return unique_articles

    def _analyze_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """
        Analyze articles with Claude for relevance and insights.

        Args:
            articles: List of articles to analyze

        Returns:
            List of analyzed articles
        """
        analyzed = []

        for i, article in enumerate(articles):
            try:
                logger.info(f"Analyzing article {i+1}/{len(articles)}: {article.title}")

                # Fetch full content if needed
                if not article.content or len(article.content) < 200:
                    article = self.web_scraper.fetch_full_content(article)

                # Generate summary if needed
                if not article.summary and article.content:
                    article.summary = self.analyzer.generate_summary(article)

                # Analyze for relevance
                article = self.analyzer.analyze_article(article)

                analyzed.append(article)

            except Exception as e:
                logger.error(f"Error analyzing article '{article.title}': {e}")
                continue

        return analyzed

    def _filter_relevant(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """
        Filter articles by relevance score.

        Args:
            articles: List of analyzed articles

        Returns:
            Filtered and sorted list
        """
        # Filter by minimum relevance score
        relevant = [
            article for article in articles
            if article.relevance_score >= self.settings.min_relevance_score
        ]

        # Sort by relevance score (highest first)
        relevant.sort(key=lambda x: x.relevance_score, reverse=True)

        return relevant

    def _publish_to_notion(self, articles: List[NewsArticle]) -> int:
        """
        Publish articles to Notion.

        Args:
            articles: List of articles to publish

        Returns:
            Number of successfully published articles
        """
        published_count = 0

        for article in articles:
            try:
                # Check if already exists
                if self.notion.page_exists(str(article.url)):
                    logger.info(f"Article already exists in Notion: {article.title}")
                    continue

                # Create page
                page_id = self.notion.create_article_page(article)

                if page_id:
                    published_count += 1

            except Exception as e:
                logger.error(f"Error publishing article '{article.title}': {e}")
                continue

        logger.info(f"Published {published_count} new articles to Notion")
        return published_count

    def verify_setup(self) -> bool:
        """
        Verify that all integrations are configured correctly.

        Returns:
            True if setup is valid, False otherwise
        """
        logger.info("Verifying agent setup...")

        # Check Notion connection
        if not self.notion.setup_database():
            logger.error("Notion database not accessible")
            logger.info(self.notion.get_database_schema_instructions())
            return False

        logger.info("Setup verification complete")
        return True
