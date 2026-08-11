"""
Validation helper for corporate investment risk indicators.
Asserts presence and completeness of dependent domain data models.
"""

from models import FinancialRatios, SentimentResult
from core.exceptions import DataRetrievalError
from core import get_logger

logger = get_logger("risk_validator")

class RiskValidator:
    """
    Validates presence and field completeness of ratios and sentiment data before risk engine run.
    """

    @staticmethod
    def validate_inputs(ratios: FinancialRatios, sentiment: SentimentResult):
        """
        Validates the dependent domain models. Throws custom DataRetrievalError exceptions
        containing descriptive visual alert messages for failure states.
        """
        # 1. Ratios validation
        if ratios is None:
            logger.warning("Risk assessment failed: ratios payload is missing.")
            raise DataRetrievalError(
                "Risk assessment cannot be generated because financial information is unavailable."
            )

        # 2. Sentiment validation
        if sentiment is None:
            logger.warning("Risk assessment failed: sentiment payload is missing.")
            raise DataRetrievalError(
                "Risk assessment cannot be generated because sentiment analysis is unavailable."
            )

        # 3. Minimum field completeness validation
        # Assert that at least one of the major ratio metric descriptors or sentiment summaries are available.
        # If all major scoring metrics are missing, reject as incomplete.
        ratio_values = [
            ratios.pe_ratio,
            ratios.pb_ratio,
            ratios.roe,
            ratios.profit_margin,
            ratios.eps
        ]
        has_any_ratio = False
        for val in ratio_values:
            if val is not None:
                has_any_ratio = True
                break
        
        if not has_any_ratio:
            logger.warning("Risk assessment failed: ratio models contain all null values.")
            raise DataRetrievalError(
                "Additional information is required to generate a risk assessment."
            )

        logger.info(
            f"RiskValidator: input validation succeeded for ticker context '{ratios.ticker}' "
            f"(Article count: {sentiment.article_count})."
        )
