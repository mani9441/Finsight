"""
Historical Price Controller module.
Coordinates historical stock price retrieval, mapping, and error handling.
"""

from typing import List
from models import HistoricalPrice
from services.interfaces import IHistoricalPriceService
from core import get_logger

logger = get_logger("historical_price_controller")

class HistoricalPriceController:
    """
    Coordinates interactions between Streamlit UI views and historical price service.
    Uses Dependency Injection to accept service interfaces.
    """

    def __init__(self, historical_price_service: IHistoricalPriceService):
        self.historical_price_service = historical_price_service

    def get_historical_prices(self, ticker: str, time_range: str) -> List[HistoricalPrice]:
        """
        Retrieves the historical prices for the company ticker over the specified time range.
        Logs timing, catches errors, and raises clean service exceptions.
        """
        ticker_str = ticker.strip().upper()
        logger.info(f"HistoricalPriceController: Fetching data for '{ticker_str}' ({time_range})")
        try:
            prices = self.historical_price_service.get_historical_prices_by_range(ticker_str, time_range)
            logger.info(
                f"HistoricalPriceController: Successfully resolved {len(prices)} "
                f"price records for '{ticker_str}'"
            )
            return prices
        except Exception as e:
            logger.error(f"HistoricalPriceController: Service failed for '{ticker_str}': {e}")
            raise
