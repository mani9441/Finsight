"""
Application Controller module.
Coordinates workflow logic, service triggers, and data aggregation.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from core import get_logger
from core.exceptions import FinSightException, DataRetrievalError
from models import (
    CompanyInfo,
    FinancialMetrics,
    HistoricalPrice,
    NewsArticle,
    SentimentResult,
    RiskAssessment,
    AISummary,
    CompanyOverview,
    FinancialRatios,
)
from services.interfaces import (
    ICompanySearchService,
    IFinancialService,
    INewsService,
    ISentimentService,
    IRiskService,
    IAISummaryService,
)

logger = get_logger("controller")

class ApplicationController:
    """
    Coordinates interactions between Streamlit UI views and underlying business services.
    Uses Dependency Injection to accept service interfaces.
    """

    def __init__(
        self,
        company_service: ICompanySearchService,
        financial_service: IFinancialService,
        news_service: INewsService,
        sentiment_service: ISentimentService,
        risk_service: IRiskService,
        ai_service: IAISummaryService,
    ):
        self.company_service = company_service
        self.financial_service = financial_service
        self.news_service = news_service
        self.sentiment_service = sentiment_service
        self.risk_service = risk_service
        self.ai_service = ai_service

    def analyze_ticker(self, ticker: str, date_window_days: int = 30) -> Dict[str, Any]:
        """
        Runs the complete analysis pipeline for a target ticker.
        Aggregates output from all services into a single dictionary.
        Gracefully handles service disruptions to return partial data where possible.
        """
        ticker = ticker.strip().upper()
        logger.info(f"Starting analysis workflow for ticker: {ticker} (window: {date_window_days} days)")
        
        results: Dict[str, Any] = {
            "ticker": ticker,
            "profile": None,
            "metrics": None,
            "prices": [],
            "sentiment": None,
            "risk": None,
            "ai_summary": None,
            "errors": []
        }

        # 1. Fetch Company Profile (Core Dependency)
        try:
            profile = self.company_service.get_profile(ticker)
            if not profile:
                raise DataRetrievalError(f"No company information found for ticker '{ticker}'")
            results["profile"] = profile
        except Exception as e:
            logger.error(f"Failed to fetch profile for {ticker}: {e}")
            results["errors"].append(f"Company Profile Error: {str(e)}")
            # If we can't get basic info, we halt downstream steps
            return results

        # 2. Fetch Financial Metrics & Statements
        try:
            results["metrics"] = self.financial_service.get_financial_metrics(ticker)
        except Exception as e:
            logger.error(f"Failed to fetch financial metrics for {ticker}: {e}")
            results["errors"].append(f"Financial Ratios Error: {str(e)}")

        # 3. Fetch Historical Prices
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=date_window_days)
            results["prices"] = self.financial_service.get_historical_prices(ticker, start_date, end_date)
        except Exception as e:
            logger.error(f"Failed to fetch historical prices for {ticker}: {e}")
            results["errors"].append(f"Stock Prices Error: {str(e)}")

        # 4. Fetch News & Analyze Sentiment
        articles = []
        try:
            articles = self.news_service.get_recent_news(ticker)
            if articles:
                results["sentiment"] = self.sentiment_service.analyze_sentiment(articles)
            else:
                logger.warning(f"No recent news found for {ticker}")
        except Exception as e:
            logger.error(f"Failed to analyze news sentiment for {ticker}: {e}")
            results["errors"].append(f"Sentiment Analysis Error: {str(e)}")

        # 5. Evaluate Risks
        # We need metrics and sentiment results to evaluate risks properly.
        # Fallbacks are triggered using empty placeholders if services failed.
        if results["profile"]:
            try:
                # Ensure we have fallback dummy models if metrics/sentiment failed
                metrics_data = results["metrics"] or FinancialMetrics(ticker=ticker, currency="£")
                sentiment_data = results["sentiment"] or SentimentResult(
                    ticker=ticker, average_score=0.0, sentiment_label="Neutral",
                    article_count=0, positive_count=0, negative_count=0, neutral_count=0
                )
                results["risk"] = self.risk_service.assess_risk(metrics_data, sentiment_data)
            except Exception as e:
                logger.error(f"Failed to evaluate risks for {ticker}: {e}")
                results["errors"].append(f"Risk Assessment Error: {str(e)}")

        # 6. Generate AI Executive Summary & Advisory Report
        if results["profile"]:
            try:
                # Compile parameters with fallbacks
                metrics_data = results["metrics"] or FinancialMetrics(ticker=ticker, currency="£")
                sentiment_data = results["sentiment"] or SentimentResult(
                    ticker=ticker, average_score=0.0, sentiment_label="Neutral",
                    article_count=0, positive_count=0, negative_count=0, neutral_count=0
                )
                risk_data = results["risk"] or RiskAssessment(
                    ticker=ticker, risk_score=0.0, risk_level="Unknown", risk_factors=["Risk analysis unavailable"]
                )
                
                profile = results["profile"]
                overview_data = CompanyOverview(
                    name=profile.name,
                    ticker=profile.ticker,
                    exchange="Unknown",
                    currency=metrics_data.currency,
                    sector=profile.sector,
                    industry=profile.industry,
                    country="Unknown",
                    website=profile.website,
                    business_summary=profile.summary,
                    market_capitalization=metrics_data.market_cap
                )
                
                ratios_data = FinancialRatios(
                    ticker=ticker,
                    currency=metrics_data.currency,
                    pe_ratio=metrics_data.pe_ratio,
                    pb_ratio=metrics_data.pb_ratio,
                    roe=metrics_data.roe,
                    profit_margin=metrics_data.profit_margin,
                    dividend_yield=None,
                    eps=metrics_data.eps
                )
                
                results["ai_summary"] = self.ai_service.generate_advisory_summary(
                    company_overview=overview_data,
                    ratios=ratios_data,
                    sentiment=sentiment_data,
                    risk=risk_data
                )
            except Exception as e:
                logger.error(f"Failed to generate AI summary for {ticker}: {e}")
                results["errors"].append(f"AI Advisor Error: {str(e)}")

        logger.info(f"Completed analysis pipeline for {ticker}. Active errors: {len(results['errors'])}")
        return results
