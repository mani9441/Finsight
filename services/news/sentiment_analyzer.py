"""
Sentiment Analyzer using TextBlob NLP library.
Classifies articles as Positive, Neutral, or Negative.
"""

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from textblob import TextBlob
from models import NewsArticle
from core.constants import SENTIMENT_THRESHOLDS
from core import get_logger

logger = get_logger("sentiment_analyzer")

class SentimentAnalyzer:
    """
    Evaluates polarity scores of textual content and labels them according to project boundaries.
    Uses NLTK for tokenisation and text preparation, and TextBlob for sentiment analysis.
    """

    def __init__(self):
        # Read boundaries from project configurations
        self.pos_threshold = SENTIMENT_THRESHOLDS.get("POSITIVE", 0.05)
        self.neg_threshold = SENTIMENT_THRESHOLDS.get("NEGATIVE", -0.05)
        
        # Download required NLTK resources quietly if they are not already cached
        for resource in ["punkt", "punkt_tab", "stopwords"]:
            try:
                if resource == "punkt_tab":
                    nltk.data.find("tokenizers/punkt_tab")
                elif resource == "punkt":
                    nltk.data.find("tokenizers/punkt")
                elif resource == "stopwords":
                    nltk.data.find("corpora/stopwords")
            except LookupError:
                logger.info(f"Downloading NLTK resource: '{resource}'")
                nltk.download(resource, quiet=True)

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
            # Tokenize and clean text using NLTK
            try:
                words = word_tokenize(text_content)
                stop_words = set(stopwords.words("english"))
                cleaned_words = [w for w in words if w.isalnum() and w.lower() not in stop_words]
                prepared_text = " ".join(cleaned_words)
            except Exception as nltk_err:
                logger.warning(f"NLTK preprocessing failed: {nltk_err}. Defaulting to raw text.")
                prepared_text = text_content

            blob = TextBlob(prepared_text)
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
