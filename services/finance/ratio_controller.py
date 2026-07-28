"""
Financial Ratios Controller module.
Coordinates financial ratio data retrieval and exception management.
"""

from models import FinancialRatios
from services.interfaces import IFinancialRatioService
from core import get_logger

logger = get_logger("ratio_controller")

class RatioController:
    """
    Coordinates interactions between Streamlit UI views and ratio service.
    Uses Dependency Injection to accept service interfaces.
    """

    def __init__(self, ratio_service: IFinancialRatioService):
        self.ratio_service = ratio_service

    def get_ratios(self, ticker: str) -> FinancialRatios:
        """
        Coordinates the workflow to fetch, validate, and standardize ratios for a target ticker.
        """
        ticker_str = ticker.strip().upper()
        logger.info(f"RatioController: Requesting ratios for ticker: '{ticker_str}'")
        try:
            ratios = self.ratio_service.get_financial_ratios(ticker_str)
            logger.info(f"RatioController: Successfully resolved ratios for ticker: '{ticker_str}'")
            return ratios
        except Exception as e:
            logger.error(f"RatioController: Service failed for ticker '{ticker_str}': {e}")
            raise
