"""
News Service implementation fetching financial articles via yfinance news streams.
"""

import yfinance as yf
from typing import List

from core import get_logger
from core.exceptions import DataRetrievalError
from models import NewsArticle
from services.interfaces import INewsService
from services.news.news_mapper import NewsMapper
from services.common.response_validator import ResponseValidator

logger = get_logger("news_service")

class NewsService(INewsService):
    """
    Retrieves and standardizes financial news feeds using Yahoo Finance.
    """

    def get_recent_news(self, ticker: str, limit: int = 10) -> List[NewsArticle]:
        """
        Retrieves the most recent news articles for a ticker.
        """
        ticker_str = ticker.strip().upper()
        logger.info(f"Retrieving recent news articles for: {ticker_str} (Limit: {limit})")
        ResponseValidator.validate_ticker_input(ticker_str)

        try:
            ticker_obj = yf.Ticker(ticker_str)
            raw_news = ticker_obj.news

            # If ticker news list is empty or invalid
            if raw_news is None:
                logger.warning(f"No news channel resolved for ticker '{ticker_str}'")
                return []

            if not isinstance(raw_news, list):
                raise DataRetrievalError(
                    f"Unexpected news payload format from Yahoo Finance for ticker '{ticker_str}'"
                )

            # Map raw articles to list of domain objects
            articles = []
            for item in raw_news:
                if not isinstance(item, dict):
                    continue
                try:
                    # Enforce basic validation of critical keys depending on schema
                    content_dict = item.get("content")
                    if isinstance(content_dict, dict):
                        ResponseValidator.validate_keys(content_dict, ["title"], "News Article Content")
                    else:
                        ResponseValidator.validate_keys(item, ["title", "link"], "News Article")
                        
                    article = NewsMapper.to_news_article(item)
                    articles.append(article)
                except Exception as e:
                    logger.warning(f"Skipping malformed news item for ticker '{ticker_str}': {e}")

            # Truncate to limit
            truncated_articles = articles[:limit]
            logger.info(f"Successfully processed {len(truncated_articles)} articles for {ticker_str}")
            return truncated_articles

        except Exception as e:
            logger.error(f"Error fetching news for {ticker_str} from yfinance: {e}")
            raise DataRetrievalError(
                f"Failed to retrieve news articles for ticker '{ticker_str}' due to: {str(e)}"
            ) from e
