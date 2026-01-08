"""Configuration settings for the Healthcare UX News Agent."""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    anthropic_api_key: str = Field(..., alias="ANTHROPIC_API_KEY")
    notion_api_key: str = Field(..., alias="NOTION_API_KEY")
    notion_database_id: str = Field(..., alias="NOTION_DATABASE_ID")
    news_api_key: Optional[str] = Field(None, alias="NEWS_API_KEY")

    # Agent Configuration
    agent_run_interval_hours: int = Field(24, alias="AGENT_RUN_INTERVAL_HOURS")
    max_articles_per_run: int = Field(20, alias="MAX_ARTICLES_PER_RUN")
    min_relevance_score: float = Field(0.7, alias="MIN_RELEVANCE_SCORE")

    # Logging
    log_level: str = Field("INFO", alias="LOG_LEVEL")

    # News Sources Configuration
    rss_feeds: List[str] = Field(default_factory=lambda: [
        "https://www.healthcareitnews.com/rss.xml",
        "https://www.mobihealthnews.com/rss.xml",
        "https://healthtechmagazine.net/rss.xml",
        "https://www.uxmatters.com/index.xml",
        "https://www.nngroup.com/feed/rss/",
    ])

    # Search Keywords
    search_keywords: List[str] = Field(default_factory=lambda: [
        "healthcare UX",
        "medical device design",
        "patient experience",
        "health app usability",
        "clinical workflow design",
        "EHR user interface",
        "telemedicine UX",
        "healthcare accessibility",
        "medical user research",
        "life sciences UX",
    ])

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings instance."""
    global settings
    if settings is None:
        settings = Settings()
    return settings
