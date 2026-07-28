"""
Validation utilities for news articles data streams.
Filters out incomplete, duplicate, or malformed entries.
"""

from typing import List, Set
from models import NewsArticle
from core import get_logger

logger = get_logger("news_validator")

class NewsValidator:
    """
    Validates news articles for completeness, format, and removes duplicates.
    """

    @staticmethod
    def is_valid_article(article: NewsArticle) -> bool:
        """
        Validates that the article contains all required fields.
        Checks for non-empty title, published date, summary, and a valid URL.
        """
        if not article:
            return False

        # 1. Title validation
        if not article.title or not isinstance(article.title, str) or not article.title.strip():
            logger.warning("Skipping news article: title is missing or empty.")
            return False

        # 2. Date validation
        if article.published_at is None:
            logger.warning(f"Skipping news article '{article.title[:30]}...': publication date is missing.")
            return False

        # 3. Summary validation
        if not article.summary or not isinstance(article.summary, str) or not article.summary.strip():
            logger.warning(f"Skipping news article '{article.title[:30]}...': summary is missing or empty.")
            return False

        # 4. URL validation
        if not article.url or not isinstance(article.url, str) or not article.url.strip():
            logger.warning(f"Skipping news article '{article.title[:30]}...': URL link is missing.")
            return False
            
        url_clean = article.url.strip()
        if not (url_clean.startswith("http://") or url_clean.startswith("https://")):
            logger.warning(f"Skipping news article '{article.title[:30]}...': URL link '{article.url}' is invalid.")
            return False

        return True

    @classmethod
    def remove_duplicates(cls, articles: List[NewsArticle]) -> List[NewsArticle]:
        """
        Filters out duplicate articles from the list based on title or URL.
        Preserves original chronological ordering.
        """
        unique_articles = []
        seen_titles: Set[str] = set()
        seen_urls: Set[str] = set()

        for article in articles:
            # Check validation rules first
            if not cls.is_valid_article(article):
                continue

            # Standardize titles for exact deduplication checks
            title_key = article.title.strip().lower()
            url_key = article.url.strip().lower()

            if title_key in seen_titles:
                logger.warning(f"Excluding duplicate article title: '{article.title[:40]}...'")
                continue
                
            if url_key in seen_urls:
                logger.warning(f"Excluding duplicate article link: '{article.url}'")
                continue

            seen_titles.add(title_key)
            seen_urls.add(url_key)
            unique_articles.append(article)

        logger.info(
            f"Deduplication completed. Remaining unique articles: {len(unique_articles)} "
            f"(excluded {len(articles) - len(unique_articles)} duplicate/invalid entries)."
        )
        return unique_articles
