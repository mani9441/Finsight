"""
News Sentiment Analysis Controller.
Orchestrates retrieving articles, validating, evaluating sentiment, and aggregating summary statistics.
"""

from typing import Tuple, List
from models import NewsArticle, SentimentResult
from services.interfaces import INewsService
from services.common.news_validator import NewsValidator
from services.news.sentiment_analyzer import SentimentAnalyzer
from services.news.sentiment_aggregator import SentimentAggregator
from core import get_logger

logger = get_logger("news_controller")

class NewsController:
    """
    Coordinates news flows: retrieves articles, applies validations, executes sentiment analysis,
    and returns sorted, aggregated metrics to visual layouts.
    """

    def __init__(self, news_service: INewsService):
        self.news_service = news_service
        self.analyzer = SentimentAnalyzer()

    def get_news_with_sentiment(self, ticker: str, limit: int = 10) -> Tuple[List[NewsArticle], SentimentResult]:
        """
        Retrieves, deduplicates, analyzes, sorts, and aggregates company news feeds.
        """
        ticker_str = ticker.strip().upper()
        logger.info(f"NewsController: Starting news & sentiment workflow for ticker: '{ticker_str}'")
        
        # 1. Fetch raw articles
        raw_articles = self.news_service.get_recent_news(ticker_str, limit=30)  # fetch extra to allow duplicate room
        
        # 2. Filter invalid or duplicate articles
        valid_articles = NewsValidator.remove_duplicates(raw_articles)
        
        # 3. Apply NLP sentiment analysis to each article
        analyzed_articles = []
        for article in valid_articles:
            try:
                analyzed = self.analyzer.analyze_article_sentiment(article)
                analyzed_articles.append(analyzed)
            except Exception as e:
                logger.error(f"NewsController: Failed to analyze sentiment for '{article.title[:30]}...': {e}")
                # Fallback to Neutral mapping so that failures don't drop valid articles
                article.sentiment_score = 0.0
                article.sentiment_label = "Neutral"
                analyzed_articles.append(article)

        # 4. Sort in reverse chronological order (newest first)
        analyzed_articles.sort(key=lambda a: a.published_at, reverse=True)
        
        # Keep only the requested limit size
        final_articles = analyzed_articles[:limit]
        
        # 5. Compute overall aggregated sentiment metrics
        sentiment_summary = SentimentAggregator.aggregate_sentiment(ticker_str, final_articles)
        
        logger.info(
            f"NewsController: Completed sentiment workflow for '{ticker_str}'. "
            f"Returned {len(final_articles)} articles."
        )
        return final_articles, sentiment_summary
