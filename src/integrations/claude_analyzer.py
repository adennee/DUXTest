"""Claude API integration for analyzing and summarizing news articles."""

import logging
import json
from typing import Dict, Optional
from anthropic import Anthropic

from ..models.news import NewsArticle
from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class ClaudeAnalyzer:
    """Analyzer using Claude API for content relevance and summarization."""

    def __init__(self):
        """Initialize Claude client."""
        settings = get_settings()
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-sonnet-4-5-20250929"
        logger.info("Claude analyzer initialized")

    def analyze_article(self, article: NewsArticle) -> NewsArticle:
        """
        Analyze article for relevance to healthcare/life sciences UX.

        Args:
            article: NewsArticle to analyze

        Returns:
            Updated NewsArticle with relevance score, reasoning, and insights
        """
        content_to_analyze = f"""
Title: {article.title}
Source: {article.source}
Published: {article.published_date}
URL: {article.url}

Content:
{article.content or article.summary or "No content available"}
"""

        prompt = f"""You are an expert in UX design for healthcare and life sciences. Analyze the following article and provide:

1. A relevance score (0.0 to 1.0) for how relevant this is to UX design in healthcare/life sciences
2. A brief explanation of why it's relevant (or not)
3. Key insights that would be valuable for a Senior Director of UX in healthcare/life sciences at Oracle
4. Appropriate tags/categories (up to 5)

Article to analyze:
{content_to_analyze}

Respond in JSON format:
{{
    "relevance_score": 0.0-1.0,
    "relevance_reasoning": "explanation of relevance",
    "key_insights": "bullet points or paragraphs of key insights",
    "tags": ["tag1", "tag2", "tag3"]
}}

Focus on:
- User experience design principles
- Healthcare technology interfaces
- Patient-centered design
- Clinical workflow optimization
- Medical device usability
- Health data visualization
- Accessibility in healthcare
- Life sciences research tools
- Regulatory compliance (FDA, HIPAA)
- Emerging healthcare technologies"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract the response text
            response_text = response.content[0].text

            # Parse JSON response
            analysis = json.loads(response_text)

            # Update article with analysis results
            article.relevance_score = float(analysis.get("relevance_score", 0.0))
            article.relevance_reasoning = analysis.get("relevance_reasoning", "")
            article.key_insights = analysis.get("key_insights", "")
            article.tags = analysis.get("tags", [])

            logger.info(f"Analyzed article '{article.title}': relevance={article.relevance_score}")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {e}")
            logger.debug(f"Response was: {response_text}")
            # Set defaults on parse error
            article.relevance_score = 0.0
            article.relevance_reasoning = "Failed to analyze"

        except Exception as e:
            logger.error(f"Error analyzing article with Claude: {e}")
            article.relevance_score = 0.0
            article.relevance_reasoning = "Analysis error"

        return article

    def generate_summary(self, article: NewsArticle) -> str:
        """
        Generate a concise summary of the article.

        Args:
            article: NewsArticle to summarize

        Returns:
            Summary text
        """
        if not article.content:
            return article.summary or ""

        prompt = f"""Summarize the following article in 2-3 paragraphs, focusing on aspects relevant to UX design in healthcare and life sciences:

Title: {article.title}

Content:
{article.content[:4000]}

Provide a clear, concise summary that a busy executive could read in under a minute."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            summary = response.content[0].text
            logger.info(f"Generated summary for '{article.title}'")
            return summary

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return article.summary or ""

    def create_digest(self, articles: list[NewsArticle]) -> str:
        """
        Create a digest summary of multiple articles.

        Args:
            articles: List of NewsArticles

        Returns:
            Digest text
        """
        if not articles:
            return "No articles to summarize."

        articles_text = "\n\n".join([
            f"{i+1}. {article.title}\n   Source: {article.source}\n   Key Insight: {article.key_insights[:200] if article.key_insights else 'N/A'}"
            for i, article in enumerate(articles)
        ])

        prompt = f"""Create an executive digest of the following {len(articles)} healthcare UX articles. Identify the top 3-5 themes or trends, and provide actionable insights for a Senior Director of UX.

Articles:
{articles_text}

Format as:
- Key Trends: (3-5 bullet points)
- Strategic Insights: (2-3 paragraphs)
- Recommended Actions: (3-5 bullet points)"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            digest = response.content[0].text
            logger.info(f"Created digest for {len(articles)} articles")
            return digest

        except Exception as e:
            logger.error(f"Error creating digest: {e}")
            return "Failed to create digest."

    def analyze_product_release(self, article: NewsArticle) -> NewsArticle:
        """
        Analyze a product release announcement specifically for UX implications.

        Args:
            article: NewsArticle containing a product release

        Returns:
            Updated NewsArticle with release-specific analysis
        """
        content_to_analyze = f"""
Title: {article.title}
Company: {article.source}
Published: {article.published_date}
URL: {article.url}

Content:
{article.content or article.summary or "No content available"}
"""

        prompt = f"""You are an expert in UX design for healthcare and life sciences. Analyze this product release announcement from a competitor and provide:

1. A relevance score (0.0 to 1.0) for how important this is for a UX leader to know about
2. Brief summary of what was released (1-2 sentences)
3. UX implications and competitive insights for Oracle's UX team (2-3 bullet points)
4. Appropriate tags/categories (up to 5)

Product Release:
{content_to_analyze}

Respond in JSON format:
{{
    "relevance_score": 0.0-1.0,
    "relevance_reasoning": "brief summary of what was released",
    "key_insights": "UX implications and competitive insights as bullet points",
    "tags": ["tag1", "tag2", "tag3"]
}}

Focus on:
- New features or capabilities announced
- UX/UI improvements or innovations
- Healthcare/life sciences specific functionality
- Patient or clinician-facing features
- Workflow or integration enhancements
- Accessibility or compliance features
- Technology trends or approaches
- Competitive positioning implications"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            response_text = response.content[0].text
            analysis = json.loads(response_text)

            # Update article with analysis results
            article.relevance_score = float(analysis.get("relevance_score", 0.0))
            article.relevance_reasoning = analysis.get("relevance_reasoning", "")
            article.key_insights = analysis.get("key_insights", "")

            # Ensure "Product Release" tag is included
            tags = analysis.get("tags", [])
            if "Product Release" not in tags:
                tags.insert(0, "Product Release")
            article.tags = tags

            logger.info(f"Analyzed release '{article.title}': relevance={article.relevance_score}")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {e}")
            article.relevance_score = 0.0
            article.relevance_reasoning = "Failed to analyze"
            article.tags = ["Product Release", article.source]

        except Exception as e:
            logger.error(f"Error analyzing product release with Claude: {e}")
            article.relevance_score = 0.0
            article.relevance_reasoning = "Analysis error"
            article.tags = ["Product Release", article.source]

        return article
