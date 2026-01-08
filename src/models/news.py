"""Data models for news articles."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl


class NewsArticle(BaseModel):
    """Model representing a news article."""

    title: str
    url: HttpUrl
    published_date: datetime
    source: str
    summary: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    relevance_score: float = 0.0
    relevance_reasoning: Optional[str] = None
    key_insights: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            HttpUrl: lambda v: str(v),
        }

    def to_notion_properties(self) -> dict:
        """Convert article to Notion page properties format."""
        return {
            "Title": {
                "title": [
                    {
                        "text": {
                            "content": self.title[:2000]  # Notion title limit
                        }
                    }
                ]
            },
            "URL": {
                "url": str(self.url)
            },
            "Published": {
                "date": {
                    "start": self.published_date.isoformat()
                }
            },
            "Source": {
                "rich_text": [
                    {
                        "text": {
                            "content": self.source[:2000]
                        }
                    }
                ]
            },
            "Relevance Score": {
                "number": round(self.relevance_score, 2)
            },
            "Tags": {
                "multi_select": [{"name": tag} for tag in self.tags[:10]]  # Limit tags
            },
        }

    def to_notion_content(self) -> List[dict]:
        """Convert article to Notion page content blocks."""
        blocks = []

        # Add summary if available
        if self.summary:
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Summary"}}]
                }
            })
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": self.summary[:2000]}}]
                }
            })

        # Add key insights
        if self.key_insights:
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Key Insights for UX"}}]
                }
            })
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": self.key_insights[:2000]}}]
                }
            })

        # Add relevance reasoning
        if self.relevance_reasoning:
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Why This Matters"}}]
                }
            })
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": self.relevance_reasoning[:2000]}}]
                }
            })

        # Add link to original article
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {"type": "text", "text": {"content": "🔗 "}},
                    {
                        "type": "text",
                        "text": {"content": "Read full article", "link": {"url": str(self.url)}}
                    }
                ]
            }
        })

        return blocks
