"""
Risk Assessment Controller.
Coordinates interactions between Streamlit UI views and risk services.
"""

from models import FinancialRatios, SentimentResult, RiskAssessment
from services.interfaces import IRiskService
from core import get_logger

logger = get_logger("risk_controller")

class RiskController:
    """
    Controller responsible for coordinating investment risk assessments.
    Uses Dependency Injection to accept service implementations.
    """

    def __init__(self, risk_service: IRiskService):
        self.risk_service = risk_service

    def get_risk_assessment(self, ticker: str, ratios: FinancialRatios, sentiment: SentimentResult) -> RiskAssessment:
        """
        Coordinates the workflow to validate inputs, run engine evaluation, and build explanations.
        """
        ticker_str = ticker.strip().upper()
        logger.info(f"RiskController: Requesting risk assessment for ticker: '{ticker_str}'")
        try:
            assessment = self.risk_service.evaluate_risk(ticker_str, ratios, sentiment)
            logger.info(f"RiskController: Successfully resolved risk level for ticker: '{ticker_str}'")
            return assessment
        except Exception as e:
            logger.error(f"RiskController: Risk evaluation failed for ticker '{ticker_str}': {e}")
            raise
