"""
Sentiment Analyzer using TextBlob NLP library.
Classifies articles as Positive, Neutral, or Negative.
"""

from textblob import TextBlob
from models import NewsArticle
from core.constants import SENTIMENT_THRESHOLDS
from core import get_logger

logger = get_logger("sentiment_analyzer")

class SentimentAnalyzer:
    """
    Evaluates polarity scores of textual content and labels them according to project boundaries.
    """

    def __init__(self):
        # Read boundaries from project configurations
        self.pos_threshold = SENTIMENT_THRESHOLDS.get("POSITIVE", 0.05)
        self.neg_threshold = SENTIMENT_THRESHOLDS.get("NEGATIVE", -0.05)

    def analyze_article_sentiment(self, article: NewsArticle) -> NewsArticle:
        """
        Analyzes the combined title and summary text of a news article.
        Modifies and returns the article in-place with score and label details.
        """
        if not article:
            return article

        # Combine title and summary for context-rich sentiment parsing
        text_content = f"{article.title}. {article.summary or article.content}"
        
        try:
            blob = TextBlob(text_content)
            polarity = blob.sentiment.polarity
            
            # Map score to category label
            if polarity >= self.pos_threshold:
                label = "Positive"
            elif polarity <= self.neg_threshold:
                label = "Negative"
            else:
                label = "Neutral"

            article.sentiment_score = polarity
            article.sentiment_label = label
            logger.debug(
                f"Article sentiment resolved: score={polarity:.3f}, "
                f"label='{label}' for title='{article.title[:30]}...'"
            )
        except Exception as e:
            logger.error(f"Sentiment analysis failed for article '{article.title[:30]}...': {e}")
            article.sentiment_score = 0.0
            article.sentiment_label = "Neutral"

        return article
