"""
Historical Stock Price Service implementation using yfinance.
"""

import time
import yfinance as yf
from typing import List
from models import HistoricalPrice
from services.interfaces import IHistoricalPriceService
from services.finance.historical_mapper import HistoricalDataMapper
from services.common.historical_validator import HistoricalDataValidator
from services.finance.time_range_manager import TimeRangeManager
from services.common.response_validator import ResponseValidator
from core import get_logger
from core.exceptions import DataRetrievalError

logger = get_logger("historical_price_service")

class HistoricalPriceService(IHistoricalPriceService):
    """
    Retrieves and standardizes historical stock price and volume datasets.
    """

    def get_historical_prices_by_range(self, ticker: str, time_range: str) -> List[HistoricalPrice]:
        """
        Retrieves historical stock price details for a specific ticker and time range.
        Validates the inputs and outputs, maps to the core domain models.
        """
        ticker_str = ticker.strip().upper()
        logger.info(f"Historical data request started for '{ticker_str}' with range '{time_range}'")
        
        # 1. Validate inputs
        ResponseValidator.validate_ticker_input(ticker_str)
        yf_period = TimeRangeManager.get_yfinance_period(time_range)
        
        start_time = time.time()
        try:
            # 2. Query yfinance history
            ticker_obj = yf.Ticker(ticker_str)
            history_df = ticker_obj.history(period=yf_period)
            
            response_time = (time.time() - start_time) * 1000
            logger.info(f"Provider response received for '{ticker_str}' historical prices in {response_time:.2f}ms")
            
            # 3. Map DataFrame to dataclass structures
            prices = HistoricalDataMapper.to_historical_prices(history_df)
            logger.debug(f"Mapped {len(prices)} raw history rows for '{ticker_str}'")
            
            # 4. Filter, clean, sort, and validate dataset
            validated_prices = HistoricalDataValidator.validate_historical_prices(prices, ticker_str)
            logger.info(
                f"Successfully retrieved {len(validated_prices)} records "
                f"for '{ticker_str}' over range '{time_range}'"
            )
            return validated_prices
            
        except DataRetrievalError:
            # Re-raise custom core errors directly
            raise
        except Exception as e:
            logger.error(f"Unexpected error during historical data retrieval for '{ticker_str}': {e}")
            raise DataRetrievalError(
                f"Failed to retrieve historical stock prices from Yahoo Finance for symbol '{ticker_str}' due to: {str(e)}"
            ) from e
