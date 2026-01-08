"""External integrations module."""

from .notion_client import NotionClient
from .claude_analyzer import ClaudeAnalyzer

__all__ = ["NotionClient", "ClaudeAnalyzer"]
