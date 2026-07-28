"""
Finance Service implementation using the yfinance library.
"""

import yfinance as yf
from datetime import datetime
from typing import List, Optional

from core import get_logger
from core.exceptions import DataRetrievalError, ServiceError
from models import CompanyInfo, FinancialMetrics, HistoricalPrice
from services.interfaces import ICompanySearchService, IFinancialService
from services.finance.finance_mapper import FinanceMapper
from services.common.response_validator import ResponseValidator

logger = get_logger("finance_service")

class FinanceService(ICompanySearchService, IFinancialService):
    """
    Retrieves corporate metadata and financial analytics from Yahoo Finance.
    Implements search and quantitative data operations.
    """

    def search_companies(self, query: str) -> List[CompanyInfo]:
        """
        Searches for companies matching the query (ticker or name).
        First attempts direct symbol lookup. If that fails, attempts name search.
        """
        query_clean = query.strip()
        if not query_clean:
            return []

        # 1. Attempt direct symbol lookup (major tickers are <= 5 characters)
        if query_clean.isalnum() and len(query_clean) <= 5:
            try:
                # Basic validation checks
                ResponseValidator.validate_ticker_input(query_clean)
                profile = self.get_profile(query_clean)
                if profile:
                    logger.info(f"Direct symbol lookup succeeded for: {query_clean}")
                    return [profile]
            except Exception as e:
                logger.info(f"Direct symbol lookup failed for '{query_clean}': {e}")

        # 2. Attempt name resolution via Yahoo Finance Search API
        logger.info(f"Attempting name resolution for query: '{query_clean}'")
        try:
            search = yf.Search(query_clean)
            quotes = getattr(search, "quotes", [])
            
            if not quotes:
                logger.warning(f"No quotes returned from Search for query: '{query_clean}'")
                return []
                
            for quote in quotes:
                symbol = quote.get("symbol")
                if not symbol:
                    continue
                try:
                    profile = self.get_profile(symbol)
                    if profile:
                        logger.info(f"Name resolution succeeded. Resolved '{query_clean}' to ticker '{symbol}'")
                        return [profile]
                except Exception as e:
                    logger.debug(f"Search result symbol '{symbol}' profile fetch failed: {e}")
                    
            logger.warning(f"Name resolution failed to find any valid company profiles for query '{query_clean}'")
            return []
            
        except Exception as e:
            logger.error(f"Error during search resolution for query '{query_clean}': {e}")
            raise DataRetrievalError(
                f"Search service encountered a failure resolving query '{query_clean}': {str(e)}"
            ) from e

    def get_profile(self, ticker: str) -> Optional[CompanyInfo]:
        """
        Retrieves company profile details for a specific ticker.
        """
        ticker_str = ticker.strip().upper()
        logger.info(f"Retrieving company profile for ticker: {ticker_str}")
        ResponseValidator.validate_ticker_input(ticker_str)

        try:
            ticker_obj = yf.Ticker(ticker_str)
            raw_info = ticker_obj.info

            # yfinance returns an empty dict or dict with only 'regularMarketPrice': None for invalid tickers
            if not raw_info or not isinstance(raw_info, dict) or len(raw_info) <= 5:
                logger.warning(f"Ticker '{ticker_str}' info contains no valid metadata.")
                return None

            # Verify presence of name/symbol
            if "symbol" not in raw_info and "ticker" not in raw_info:
                logger.warning(f"Ticker '{ticker_str}' payload lacks identifying symbol keys.")
                return None

            profile = FinanceMapper.to_company_info(ticker_str, raw_info)
            
            # Enforce validation of complete identity model
            if not profile.name or not profile.sector or not profile.industry or \
               profile.sector == "Unknown" or profile.industry == "Unknown" or \
               not profile.summary or profile.summary == "No business summary available.":
                logger.warning(f"Resolved profile for Ticker '{ticker_str}' contains incomplete identity details. Rejecting.")
                return None

            logger.info(f"Successfully retrieved profile for {ticker_str}: {profile.name}")
            return profile

        except Exception as e:
            logger.error(f"Error fetching profile for {ticker_str} from yfinance: {e}")
            raise DataRetrievalError(
                f"Failed to retrieve company profile from Yahoo Finance for symbol '{ticker_str}' due to: {str(e)}"
            ) from e

    def get_financial_metrics(self, ticker: str) -> Optional[FinancialMetrics]:
        """
        Retrieves parsed and calculated financial metrics for a ticker.
        """
        ticker_str = ticker.strip().upper()
        logger.info(f"Retrieving financial metrics for ticker: {ticker_str}")
        ResponseValidator.validate_ticker_input(ticker_str)

        try:
            ticker_obj = yf.Ticker(ticker_str)
            raw_info = ticker_obj.info

            if not raw_info or not isinstance(raw_info, dict) or len(raw_info) <= 5:
                logger.warning(f"No financial data available in yfinance payload for '{ticker_str}'")
                return None

            metrics = FinanceMapper.to_financial_metrics(ticker_str, raw_info)
            logger.info(f"Successfully retrieved financial metrics for {ticker_str}")
            return metrics

        except Exception as e:
            logger.error(f"Error fetching metrics for {ticker_str} from yfinance: {e}")
            raise DataRetrievalError(
                f"Failed to retrieve financial metrics from Yahoo Finance for symbol '{ticker_str}' due to: {str(e)}"
            ) from e

    def get_historical_prices(
        self, ticker: str, start_date: datetime, end_date: datetime
    ) -> List[HistoricalPrice]:
        """
        Retrieves a list of historical prices within a date range.
        """
        ticker_str = ticker.strip().upper()
        logger.info(f"Retrieving historical prices for: {ticker_str} | {start_date.date()} to {end_date.date()}")
        ResponseValidator.validate_ticker_input(ticker_str)

        try:
            ticker_obj = yf.Ticker(ticker_str)
            
            # Format dates to string
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")

            # Fetch history dataframe
            history_df = ticker_obj.history(start=start_str, end=end_str)
            
            if history_df.empty:
                logger.warning(f"No historical prices returned for '{ticker_str}' within requested dates.")
                return []

            prices = FinanceMapper.to_historical_prices(history_df)
            logger.info(f"Successfully retrieved {len(prices)} historical daily bars for {ticker_str}")
            return prices

        except Exception as e:
            logger.error(f"Error fetching history for {ticker_str} from yfinance: {e}")
            raise DataRetrievalError(
                f"Failed to retrieve historical stock data for '{ticker_str}' due to: {str(e)}"
            ) from e
