"""
Financial Ratios Service implementation using yfinance.
"""

import time
import yfinance as yf
from models import FinancialRatios
from services.interfaces import IFinancialRatioService
from services.finance.ratio_mapper import FinancialRatioMapper
from services.common.ratio_validator import RatioResponseValidator
from services.common.response_validator import ResponseValidator
from core import get_logger
from core.exceptions import DataRetrievalError

logger = get_logger("ratio_service")

class FinancialRatioService(IFinancialRatioService):
    """
    Service responsible for retrieving corporate valuation and performance ratios.
    Implements IFinancialRatioService interface.
    """

    def get_financial_ratios(self, ticker: str) -> FinancialRatios:
        """
        Retrieves key financial ratios (valuation, profitability, EPS, dividends) for a specific ticker.
        Validates raw results and maps them to a standardized internal model.
        """
        ticker_str = ticker.strip().upper()
        logger.info(f"Ratio retrieval request started for ticker: '{ticker_str}'")
        
        # 1. Validate ticker input format
        ResponseValidator.validate_ticker_input(ticker_str)
        
        start_time = time.time()
        try:
            # 2. Call yfinance ticker info
            ticker_obj = yf.Ticker(ticker_str)
            raw_info = ticker_obj.info
            
            response_time = (time.time() - start_time) * 1000
            logger.info(f"Provider response received for ratios of '{ticker_str}' in {response_time:.2f}ms")
            
            # 3. Validate response format
            RatioResponseValidator.validate_raw_response(raw_info, ticker_str)
            
            # Identify missing key fields for logging
            expected_fields = ["trailingPE", "priceToBook", "returnOnEquity", "profitMargins", "dividendYield", "trailingEps"]
            missing_fields = [f for f in expected_fields if f not in raw_info or raw_info[f] is None]
            if missing_fields:
                logger.warning(
                    f"Missing fields in yfinance ratio response for '{ticker_str}': {', '.join(missing_fields)}"
                )
            
            # 4. Map into FinancialRatios model
            ratios = FinancialRatioMapper.to_financial_ratios(ticker_str, raw_info)
            
            # Log successful count of retrieved metrics
            retrieved_count = sum(1 for v in [ratios.pe_ratio, ratios.pb_ratio, ratios.roe, ratios.profit_margin, ratios.dividend_yield, ratios.eps] if v is not None)
            logger.info(f"Successfully retrieved {retrieved_count}/6 metrics for '{ticker_str}'")
            return ratios
            
        except DataRetrievalError as e:
            logger.error(f"Validation failure or empty response for ratios of '{ticker_str}': {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during financial ratios retrieval for '{ticker_str}': {e}")
            raise DataRetrievalError(
                f"Failed to retrieve financial ratios from Yahoo Finance for symbol '{ticker_str}' due to: {str(e)}"
            ) from e
