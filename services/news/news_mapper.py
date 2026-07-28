"""
Mapper utility for translating raw news API results into standardized NewsArticle dataclasses.
"""

from datetime import datetime
from typing import Dict, Any
from models import NewsArticle
from core import get_logger

logger = get_logger("news_mapper")

class NewsMapper:
    """
    Translates raw third-party news payload structures into core NewsArticle domain models.
    """

    @staticmethod
    def to_news_article(raw_article: Dict[str, Any]) -> NewsArticle:
        content_dict = raw_article.get("content")
        if isinstance(content_dict, dict):
            # Extract from new nested format
            title = content_dict.get("title") or "No Title Available"
            
            provider_dict = content_dict.get("provider") or {}
            source = provider_dict.get("displayName") or "Yahoo Finance"
            
            click_through = content_dict.get("clickThroughUrl") or {}
            canonical = content_dict.get("canonicalUrl") or {}
            url = click_through.get("url") or canonical.get("url") or ""
            
            pub_date_str = content_dict.get("pubDate")
            if pub_date_str:
                try:
                    # Strip trailing Z to parse timezone properly
                    date_str = pub_date_str.replace("Z", "+00:00")
                    published_at = datetime.fromisoformat(date_str)
                except Exception:
                    published_at = datetime.now()
            else:
                published_at = datetime.now()
                
            summary = content_dict.get("summary") or ""
            content = content_dict.get("description") or summary or title
        else:
            # Fallback to legacy flat format
            title = raw_article.get("title") or "No Title Available"
            source = raw_article.get("publisher") or "Unknown Source"
            url = raw_article.get("link") or ""
            
            # Parse Unix timestamp
            publish_time_raw = raw_article.get("providerPublishTime")
            if publish_time_raw is not None:
                try:
                    published_at = datetime.fromtimestamp(int(publish_time_raw))
                except (ValueError, TypeError):
                    published_at = datetime.now()
            else:
                published_at = datetime.now()

            # Gather summary / text body placeholders
            summary = raw_article.get("summary") or ""
            content = raw_article.get("content") or summary or title

        return NewsArticle(
            title=title,
            source=source,
            published_at=published_at,
            url=url,
            summary=summary,
            content=content,
            sentiment_score=None  # Assigned in later phases
        )
