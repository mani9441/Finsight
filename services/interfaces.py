from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from models import (
    CompanyInfo,
    FinancialMetrics,
    HistoricalPrice,
    NewsArticle,
    SentimentResult,
    RiskAssessment,
    AISummary,
)

class ICompanySearchService(ABC):
    """
    Interface for company search and metadata retrieval.
    """
    @abstractmethod
    def search_companies(self, query: str) -> List[CompanyInfo]:
        """
        Searches for companies matching the query (ticker or name).
        """
        pass

    @abstractmethod
    def get_profile(self, ticker: str) -> Optional[CompanyInfo]:
        """
        Retrieves company profile details for a specific ticker.
        """
        pass


class IFinancialService(ABC):
    """
    Interface for financial statements, metrics, and price history retrieval.
    """
    @abstractmethod
    def get_financial_metrics(self, ticker: str) -> Optional[FinancialMetrics]:
        """
        Retrieves parsed and calculated financial metrics for a ticker.
        """
        pass

    @abstractmethod
    def get_historical_prices(
        self, ticker: str, start_date: datetime, end_date: datetime
    ) -> List[HistoricalPrice]:
        """
        Retrieves a list of historical prices within a date range.
        """
        pass


class INewsService(ABC):
    """
    Interface for retrieving news articles associated with a ticker.
    """
    @abstractmethod
    def get_recent_news(self, ticker: str, limit: int = 10) -> List[NewsArticle]:
        """
        Retrieves the most recent news articles for a ticker.
        """
        pass


class ISentimentService(ABC):
    """
    Interface for news sentiment analysis.
    """
    @abstractmethod
    def analyze_sentiment(self, articles: List[NewsArticle]) -> SentimentResult:
        """
        Calculates sentiment scores on a list of articles and returns aggregated results.
        """
        pass


class IRiskService(ABC):
    """
    Interface for risk analysis and risk factor extraction.
    """
    @abstractmethod
    def assess_risk(
        self, metrics: FinancialMetrics, sentiment: SentimentResult
    ) -> RiskAssessment:
        """
        Performs a risk analysis using company metrics and news sentiment outputs.
        """
        pass


class IAISummaryService(ABC):
    """
    Interface for LLM-generated advisory reports.
    """
    @abstractmethod
    def generate_advisory_summary(
        self, 
        company_info: CompanyInfo, 
        metrics: FinancialMetrics, 
        sentiment: SentimentResult,
        risk: RiskAssessment
    ) -> AISummary:
        """
        Generates an executive advisory summary integrating metadata, metrics, sentiment, and risk profile.
        """
        pass
