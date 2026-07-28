from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class NewsArticle:
    """
    Represents metadata and text content of a news article.
    """
    title: str
    source: str
    published_at: datetime
    url: str
    summary: str
    content: str
    id: Optional[str] = None
    sentiment_score: Optional[float] = None  # Float from -1.0 to 1.0
    sentiment_label: str = "Neutral"


@dataclass
class SentimentResult:
    """
    Holds aggregated sentiment analytics for a given ticker.
    """
    ticker: str
    average_score: float                   # Aggregated score from -1.0 to 1.0
    sentiment_label: str                   # e.g., Positive, Neutral, Negative
    article_count: int                     # Number of articles analyzed
    positive_count: int
    negative_count: int
    neutral_count: int
    last_updated: datetime = field(default_factory=datetime.now)
