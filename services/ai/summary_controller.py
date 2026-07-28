"""
AI Summary Controller.
Coordinates context collection, validation, and AI summary resolution.
"""

import time
from models import CompanyOverview, FinancialRatios, SentimentResult, RiskAssessment, AISummary
from services.interfaces import IAISummaryService
from core import get_logger
from core.exceptions import DataRetrievalError

logger = get_logger("summary_controller")

class SummaryController:
    """
    Coordinates advisory summary generation workflow.
    Uses Dependency Injection to accept service implementations.
    """

    def __init__(self, summary_service: IAISummaryService):
        self.summary_service = summary_service

    def get_summary(
        self,
        ticker: str,
        overview: CompanyOverview,
        ratios: FinancialRatios,
        sentiment: SentimentResult,
        risk: RiskAssessment
    ) -> AISummary:
        """
        Validates input context models and requests the structured AI summary.
        """
        ticker_str = ticker.strip().upper()
        logger.info(f"SummaryController: Initiating request for ticker: '{ticker_str}'")

        # Context validation check: Ensure all previous modules completed with valid records
        if not overview or not ratios or not sentiment or not risk:
            logger.error(f"SummaryController: Incomplete context models for '{ticker_str}'")
            raise DataRetrievalError(
                "AI summary cannot be generated because required financial information is incomplete."
            )

        # Check ratios content: If the main financial ratios metrics are all None, fail summary validation
        has_any_ratio = any(
            val is not None for val in [
                ratios.pe_ratio,
                ratios.pb_ratio,
                ratios.roe,
                ratios.profit_margin,
                ratios.eps
            ]
        )
        if not has_any_ratio:
            logger.error(f"SummaryController: Key ratios metrics are empty for '{ticker_str}'")
            raise DataRetrievalError(
                "AI summary cannot be generated because required financial information is incomplete."
            )

        start_time = time.time()
        try:
            summary = self.summary_service.generate_advisory_summary(
                company_overview=overview,
                ratios=ratios,
                sentiment=sentiment,
                risk=risk
            )
            latency = (time.time() - start_time) * 1000
            logger.info(f"SummaryController: Summary resolved in {latency:.2f}ms for '{ticker_str}'")
            return summary
            
        except Exception as e:
            logger.error(f"SummaryController: Generation service failed for ticker '{ticker_str}': {e}")
            raise
