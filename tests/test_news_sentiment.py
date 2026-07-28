import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from models import NewsArticle, SentimentResult
from services.common.news_validator import NewsValidator
from services.news.news_mapper import NewsMapper
from services.news.sentiment_analyzer import SentimentAnalyzer
from services.news.sentiment_aggregator import SentimentAggregator
from services.news.news_controller import NewsController
from core.exceptions import DataRetrievalError

class TestNewsSentimentModule(unittest.TestCase):

    def setUp(self):
        self.d1 = datetime(2026, 7, 28, 10, 0)
        self.d2 = datetime(2026, 7, 28, 11, 0)
        self.d3 = datetime(2026, 7, 28, 12, 0)

        self.sample_article_raw = {
            "uuid": "news-12345",
            "title": "Apple Q3 Profits Surge",
            "publisher": "TechCrunch",
            "link": "https://techcrunch.com/apple-profits",
            "providerPublishTime": int(self.d2.timestamp()),
            "summary": "Apple posted strong quarterly profits exceeding market estimates."
        }

        # List of mapped articles (unsorted, duplicates, negatives)
        self.mapped_articles = [
            NewsArticle(
                title="Apple Q3 Profits Surge",
                source="TechCrunch",
                published_at=self.d2,
                url="https://techcrunch.com/apple-profits",
                summary="Apple posted strong quarterly profits exceeding market estimates.",
                content="Apple posted strong quarterly profits exceeding market estimates.",
                id="news-12345"
            ),
            # Duplicate URL
            NewsArticle(
                title="Apple Profits Go Up",
                source="Gizmodo",
                published_at=self.d3,
                url="https://techcrunch.com/apple-profits",
                summary="Some summary.",
                content="Some summary.",
                id="news-dup-url"
            ),
            # Missing summary (invalid)
            NewsArticle(
                title="Apple New Event Announced",
                source="Engadget",
                published_at=self.d1,
                url="https://engadget.com/apple-event",
                summary="",
                content="",
                id="news-no-sum"
            ),
            # Duplicate Title
            NewsArticle(
                title="apple q3 profits surge",
                source="Engadget",
                published_at=self.d1,
                url="https://engadget.com/apple-profits-alt",
                summary="Similar article.",
                content="Similar article.",
                id="news-dup-title"
            ),
            # Valid chronological article
            NewsArticle(
                title="Apple shares trade lower on inflation fears",
                source="Reuters",
                published_at=self.d3,
                url="https://reuters.com/apple-shares-lower",
                summary="Stock fell today because of macroeconomic headwinds and rate hikes.",
                content="Stock fell today because of macroeconomic headwinds and rate hikes.",
                id="news-67890"
            )
        ]

    def test_news_validator(self):
        # 1. Individual validation check
        valid_art = self.mapped_articles[0]
        self.assertTrue(NewsValidator.is_valid_article(valid_art))
        
        # Missing title
        self.assertFalse(NewsValidator.is_valid_article(
            NewsArticle(title="", source="S", published_at=self.d1, url="http://x.com", summary="S", content="S")
        ))
        # Missing date
        self.assertFalse(NewsValidator.is_valid_article(
            NewsArticle(title="T", source="S", published_at=None, url="http://x.com", summary="S", content="S")
        ))
        # Invalid URL format
        self.assertFalse(NewsValidator.is_valid_article(
            NewsArticle(title="T", source="S", published_at=self.d1, url="invalid-url", summary="S", content="S")
        ))

        # 2. List deduplication and validation check
        cleaned = NewsValidator.remove_duplicates(self.mapped_articles)
        # Remaining: 1st article (Apple profits surge), 5th article (Reuters shares lower)
        # Duplicate URL (2nd), empty summary (3rd), duplicate title (4th) are filtered out.
        self.assertEqual(len(cleaned), 2)
        self.assertEqual(cleaned[0].id, "news-12345")
        self.assertEqual(cleaned[1].id, "news-67890")

    def test_news_mapper(self):
        article = NewsMapper.to_news_article(self.sample_article_raw)
        self.assertEqual(article.id, "news-12345")
        self.assertEqual(article.title, "Apple Q3 Profits Surge")
        self.assertEqual(article.source, "TechCrunch")
        self.assertEqual(article.url, "https://techcrunch.com/apple-profits")
        self.assertEqual(article.published_at, self.d2)
        self.assertEqual(article.sentiment_label, "Neutral")

        # Map fallback with generated ID
        no_uuid_raw = self.sample_article_raw.copy()
        del no_uuid_raw["uuid"]
        article_gen = NewsMapper.to_news_article(no_uuid_raw)
        self.assertIsNotNone(article_gen.id)
        self.assertEqual(len(article_gen.id), 32)  # md5 hex string len is 32

    def test_sentiment_analyzer(self):
        analyzer = SentimentAnalyzer()
        
        # Test positive TextBlob statement
        pos_article = NewsArticle(
            title="Excellent Quarter",
            source="S",
            published_at=self.d1,
            url="http://x.com",
            summary="A truly great, amazing, and successful performance with record high revenues.",
            content=""
        )
        analyzed_pos = analyzer.analyze_article_sentiment(pos_article)
        self.assertEqual(analyzed_pos.sentiment_label, "Positive")
        self.assertTrue(analyzed_pos.sentiment_score > 0.05)

        # Test negative TextBlob statement
        neg_article = NewsArticle(
            title="Worst Failure ever",
            source="S",
            published_at=self.d1,
            url="http://x.com",
            summary="Horrible losses, terrible mistakes and disappointing performance.",
            content=""
        )
        analyzed_neg = analyzer.analyze_article_sentiment(neg_article)
        self.assertEqual(analyzed_neg.sentiment_label, "Negative")
        self.assertTrue(analyzed_neg.sentiment_score < -0.05)

    def test_sentiment_aggregator(self):
        # 2 Positive, 1 Neutral, 1 Negative
        articles = [
            NewsArticle(title="T1", source="S", published_at=self.d1, url="h", summary="S", content="S", sentiment_score=0.4, sentiment_label="Positive"),
            NewsArticle(title="T2", source="S", published_at=self.d1, url="h", summary="S", content="S", sentiment_score=0.2, sentiment_label="Positive"),
            NewsArticle(title="T3", source="S", published_at=self.d1, url="h", summary="S", content="S", sentiment_score=0.0, sentiment_label="Neutral"),
            NewsArticle(title="T4", source="S", published_at=self.d1, url="h", summary="S", content="S", sentiment_score=-0.2, sentiment_label="Negative")
        ]
        
        summary = SentimentAggregator.aggregate_sentiment("AAPL", articles)
        self.assertEqual(summary.ticker, "AAPL")
        self.assertEqual(summary.article_count, 4)
        self.assertEqual(summary.positive_count, 2)
        self.assertEqual(summary.neutral_count, 1)
        self.assertEqual(summary.negative_count, 1)
        # Average: (0.4 + 0.2 + 0.0 - 0.2) / 4 = 0.1
        self.assertAlmostEqual(summary.average_score, 0.1)
        self.assertEqual(summary.sentiment_label, "Positive")  # 0.1 >= 0.05

        # Empty list check
        empty_summary = SentimentAggregator.aggregate_sentiment("AAPL", [])
        self.assertEqual(empty_summary.article_count, 0)
        self.assertEqual(empty_summary.sentiment_label, "Neutral")
        self.assertEqual(empty_summary.average_score, 0.0)

    @patch("services.news.news_service.NewsService")
    def test_news_controller(self, mock_news_service):
        # Setup mock returns
        raw_news = [
            self.sample_article_raw,
            # Duplicate
            self.sample_article_raw,
            # Valid other article
            {
                "uuid": "news-67890",
                "title": "Reuters shares trade lower",
                "publisher": "Reuters",
                "link": "https://reuters.com/apple-shares-lower",
                "providerPublishTime": int(self.d3.timestamp()),
                "summary": "Apple posted poor quarterly forecasts today."
            }
        ]
        
        mock_instance = MagicMock()
        mock_instance.get_recent_news.return_value = [NewsMapper.to_news_article(x) for x in raw_news]
        mock_news_service.return_value = mock_instance
        
        controller = NewsController(mock_instance)
        articles, summary = controller.get_news_with_sentiment("AAPL", limit=5)
        
        # 1. Verification of duplicates removal (3 items input, 1 duplicate -> 2 items output)
        self.assertEqual(len(articles), 2)
        
        # 2. Verification of reverse chronological sorting (d3 is 12:00, d2 is 11:00 -> d3 first)
        self.assertEqual(articles[0].id, "news-67890")
        self.assertEqual(articles[1].id, "news-12345")
        
        # 3. Verification of sentiment result populated
        self.assertEqual(summary.article_count, 2)
        self.assertIsNotNone(articles[0].sentiment_label)
        self.assertIsNotNone(articles[1].sentiment_label)
