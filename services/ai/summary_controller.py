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

        # Context validation check: Ensure all required context models are present (non-None)
        if not overview or not ratios or not sentiment or not risk:
            logger.error(f"SummaryController: Incomplete context models for '{ticker_str}'")
            raise DataRetrievalError(
                "AI summary cannot be generated because required financial information is incomplete."
            )

        # Verify ratios contains actual numeric data (not just an empty object)
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

        # Ensure overview has basic company info
        if not overview.name or not overview.business_summary:
            logger.error(f"SummaryController: Overview is missing essential fields for '{ticker_str}'")
            raise DataRetrievalError(
                "AI summary cannot be generated because company information is incomplete."
            )

        # Ensure sentiment has data
        if sentiment.average_score is None:
            logger.error(f"SummaryController: Sentiment data is incomplete for '{ticker_str}'")
            raise DataRetrievalError(
                "AI summary cannot be generated because sentiment information is incomplete."
            )

        # Ensure risk assessment has risk factors (if risk score is calculated)
        # Note: risk rules engine always produces at least one list factor or level info
        if not risk.risk_level:
            logger.error(f"SummaryController: Risk assessment level is missing for '{ticker_str}'")
            raise DataRetrievalError(
                "AI summary cannot be generated because risk assessment is incomplete."
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
