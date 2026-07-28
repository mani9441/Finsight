"""
Sentiment Aggregator utility.
Aggregates sentiment categories and scores across a collection of analyzed news articles.
"""

from typing import List
from models import NewsArticle, SentimentResult
from core.constants import SENTIMENT_THRESHOLDS
from core import get_logger

logger = get_logger("sentiment_aggregator")

class SentimentAggregator:
    """
    Computes overall statistics and determines overall sentiment tags for tickers.
    """

    @staticmethod
    def aggregate_sentiment(ticker: str, articles: List[NewsArticle]) -> SentimentResult:
        """
        Processes a list of analyzed articles.
        Returns a SentimentResult summarizing overall category counts, averages, and tags.
        """
        ticker_upper = ticker.strip().upper()
        total_count = len(articles)
        
        if total_count == 0:
            logger.info(f"SentimentAggregator: No articles provided for ticker '{ticker_upper}'. Returning Neutral summary.")
            return SentimentResult(
                ticker=ticker_upper,
                average_score=0.0,
                sentiment_label="Neutral",
                article_count=0,
                positive_count=0,
                negative_count=0,
                neutral_count=0
            )

        pos_count = 0
        neg_count = 0
        neu_count = 0
        total_score = 0.0

        for article in articles:
            label = article.sentiment_label
            score = article.sentiment_score or 0.0
            
            total_score += score
            
            if label == "Positive":
                pos_count += 1
            elif label == "Negative":
                neg_count += 1
            else:
                neu_count += 1

        avg_score = total_score / total_count

        # Classify the aggregated average score
        pos_threshold = SENTIMENT_THRESHOLDS.get("POSITIVE", 0.05)
        neg_threshold = SENTIMENT_THRESHOLDS.get("NEGATIVE", -0.05)

        if avg_score >= pos_threshold:
            overall_label = "Positive"
        elif avg_score <= neg_threshold:
            overall_label = "Negative"
        else:
            overall_label = "Neutral"

        logger.info(
            f"Sentiment aggregated for '{ticker_upper}': count={total_count}, avg_score={avg_score:.3f}, "
            f"overall='{overall_label}' (Pos: {pos_count}, Neu: {neu_count}, Neg: {neg_count})"
        )

        return SentimentResult(
            ticker=ticker_upper,
            average_score=avg_score,
            sentiment_label=overall_label,
            article_count=total_count,
            positive_count=pos_count,
            negative_count=neg_count,
            neutral_count=neu_count
        )
