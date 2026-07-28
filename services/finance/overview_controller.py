"""
Overview Controller module.
Coordinates data retrieval workflow for the company financial overview.
"""

from models import CompanyOverview
from services.interfaces import IFinancialOverviewService
from core import get_logger

logger = get_logger("overview_controller")

class OverviewController:
    """
    Coordinates interactions between UI pages and underlying financial overview services.
    Uses Dependency Injection to accept service interfaces.
    """

    def __init__(self, overview_service: IFinancialOverviewService):
        self.overview_service = overview_service

    def get_overview(self, ticker: str) -> CompanyOverview:
        """
        Runs the financial overview retrieval workflow for a target ticker.
        """
        ticker_str = ticker.strip().upper()
        logger.info(f"OverviewController: Requesting company overview for: '{ticker_str}'")
        try:
            overview = self.overview_service.get_company_overview(ticker_str)
            logger.info(f"OverviewController: Successfully resolved overview for: '{ticker_str}'")
            return overview
        except Exception as e:
            logger.error(f"OverviewController: Service failed for '{ticker_str}': {e}")
            raise
