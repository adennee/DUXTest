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

    # Competitor Companies to Track
    competitor_companies: List[dict] = Field(default_factory=lambda: [
        # Tech Giants
        {"name": "Google", "aliases": ["Google Cloud", "Google Health"], "blog_url": "https://cloud.google.com/blog/products/healthcare-life-sciences"},
        {"name": "Microsoft", "aliases": ["Microsoft Cloud", "Microsoft Healthcare"], "blog_url": "https://www.microsoft.com/en-us/industry/blog/healthcare/"},
        {"name": "IBM", "aliases": ["IBM Watson Health", "IBM Cloud"], "blog_url": "https://www.ibm.com/blog/"},
        {"name": "SAP", "aliases": ["SAP Health"], "blog_url": "https://www.sap.com/industries/life-sciences.html"},
        {"name": "Salesforce", "aliases": ["Salesforce Health Cloud"], "blog_url": "https://www.salesforce.com/blog/"},
        {"name": "AWS", "aliases": ["Amazon Web Services", "AWS Health"], "blog_url": "https://aws.amazon.com/blogs/industries/healthcare/"},
        # Healthcare/Life Sciences Firms
        {"name": "Epic", "aliases": ["Epic Systems"], "blog_url": "https://www.epic.com/"},
        {"name": "Veeva Systems", "aliases": ["Veeva"], "blog_url": "https://www.veeva.com/resources/"},
        {"name": "Medidata", "aliases": ["Medidata Solutions", "Dassault Systèmes Medidata"], "blog_url": "https://www.medidata.com/en/"},
        {"name": "Qlik", "aliases": ["Qlik Healthcare"], "blog_url": "https://www.qlik.com/us/solutions/industries/healthcare"},
        {"name": "Informatica", "aliases": [], "blog_url": "https://www.informatica.com/industries/healthcare.html"},
        {"name": "Philips", "aliases": ["Philips Healthcare", "Royal Philips"], "blog_url": "https://www.philips.com/a-w/about/news/"},
    ])

    # Release Tracking Keywords
    release_keywords: List[str] = Field(default_factory=lambda: [
        "announces",
        "launches",
        "releases",
        "introduces",
        "unveils",
        "new feature",
        "new product",
        "update",
        "available now",
        "general availability",
        "beta",
        "preview",
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
