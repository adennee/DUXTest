"""Notion API integration for creating and updating pages."""

import logging
from typing import List, Optional
from notion_client import Client
from notion_client.errors import APIResponseError

from ..models.news import NewsArticle
from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class NotionClient:
    """Client for interacting with Notion API."""

    def __init__(self):
        """Initialize Notion client with API credentials."""
        settings = get_settings()
        self.client = Client(auth=settings.notion_api_key)
        self.database_id = settings.notion_database_id
        logger.info("Notion client initialized")

    def create_article_page(self, article: NewsArticle) -> Optional[str]:
        """
        Create a new page in Notion database for an article.

        Args:
            article: NewsArticle object to create page for

        Returns:
            Page ID if successful, None otherwise
        """
        try:
            # Create the page with properties
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=article.to_notion_properties(),
                children=article.to_notion_content()
            )

            page_id = response.get("id")
            logger.info(f"Created Notion page for article: {article.title} (ID: {page_id})")
            return page_id

        except APIResponseError as e:
            logger.error(f"Failed to create Notion page for {article.title}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating Notion page: {e}")
            return None

    def create_articles_batch(self, articles: List[NewsArticle]) -> int:
        """
        Create multiple article pages in Notion.

        Args:
            articles: List of NewsArticle objects

        Returns:
            Number of successfully created pages
        """
        success_count = 0

        for article in articles:
            if self.create_article_page(article):
                success_count += 1

        logger.info(f"Successfully created {success_count}/{len(articles)} Notion pages")
        return success_count

    def page_exists(self, article_url: str) -> bool:
        """
        Check if a page for this article already exists.

        Args:
            article_url: URL of the article to check

        Returns:
            True if page exists, False otherwise
        """
        try:
            response = self.client.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "URL",
                    "url": {
                        "equals": article_url
                    }
                }
            )

            exists = len(response.get("results", [])) > 0
            return exists

        except Exception as e:
            logger.error(f"Error checking if page exists: {e}")
            return False

    def setup_database(self) -> bool:
        """
        Verify database exists and has correct schema.
        Note: This requires the database to be shared with the integration.

        Returns:
            True if database is accessible, False otherwise
        """
        try:
            database = self.client.databases.retrieve(database_id=self.database_id)
            logger.info(f"Successfully connected to Notion database: {database.get('title', [{}])[0].get('plain_text', 'Unknown')}")
            return True

        except APIResponseError as e:
            logger.error(f"Failed to access Notion database: {e}")
            logger.error("Make sure the database is shared with your Notion integration")
            return False
        except Exception as e:
            logger.error(f"Unexpected error accessing database: {e}")
            return False

    def get_database_schema_instructions(self) -> str:
        """
        Return instructions for setting up the Notion database.

        Returns:
            Markdown formatted instructions
        """
        return """
## Notion Database Schema

Create a database in Notion with the following properties:

1. **Title** (Title) - The article title
2. **URL** (URL) - Link to the original article
3. **Published** (Date) - Publication date
4. **Source** (Text) - News source name
5. **Relevance Score** (Number) - Score from 0-1
6. **Tags** (Multi-select) - Article tags/categories

Optional properties for enhanced features:
7. **Author** (Text) - Article author
8. **Read Status** (Checkbox) - Mark as read
9. **Priority** (Select) - High/Medium/Low

After creating the database:
1. Click "..." menu → "Connections" → Add your integration
2. Copy the database ID from the URL (the part after your workspace name and before the "?")
3. Add it to your .env file as NOTION_DATABASE_ID
"""
