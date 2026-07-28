"""
Risk Evaluation Service implementation.
Combines ratios and sentiment parameters to resolve overall corporate risk.
"""

from models import FinancialRatios, SentimentResult, RiskAssessment
from services.interfaces import IRiskService
from services.common.risk_validator import RiskValidator
from services.finance.risk_rules_engine import RiskRulesEngine
from core import get_logger

logger = get_logger("risk_service")

class RiskEvaluationService(IRiskService):
    """
    Evaluates corporate investment risk.
    Implements IRiskService.
    """

    def evaluate_risk(self, ticker: str, ratios: FinancialRatios, sentiment: SentimentResult) -> RiskAssessment:
        """
        Validates inputs, runs rules engine, creates a descriptive risk explanation, and returns a RiskAssessment.
        """
        ticker_str = ticker.strip().upper()
        logger.info(f"RiskEvaluationService: Starting evaluation for ticker: '{ticker_str}'")

        # 1. Run validator
        RiskValidator.validate_inputs(ratios, sentiment)

        # 2. Run rules engine
        factors, risk_level, risk_score = RiskRulesEngine.evaluate_factors(ratios, sentiment)

        # 3. Build dynamic explanation based on category outcomes
        if risk_level == "Low Risk":
            explanation = (
                "The company demonstrates solid financial characteristics with low risk signals. "
                "Operating margins and corporate ratios appear stable, and market news coverage is generally neutral or positive."
            )
            if factors:
                # Add minor factor as warning
                factor_text = factors[0].replace("High ", "").replace("Negative ", "")
                explanation += f" Note: {factor_text.lower()} is a minor consideration."
        elif risk_level == "Moderate Risk":
            clean_factors = [f.split(" suggests")[0].split(" indicates")[0].split(" reflects")[0] for f in factors]
            explanation = (
                f"Moderate investment risk indicators detected. The company has a few metrics requiring caution: "
                f"{', '.join(clean_factors)}. News sentiment or specific valuations suggest moderate overall uncertainty."
            )
        else:
            clean_factors = [f.split(" suggests")[0].split(" indicates")[0].split(" reflects")[0] for f in factors]
            explanation = (
                f"High risk signals detected. The company has multiple critical factors requiring caution: "
                f"{', '.join(clean_factors)}. Financial operating losses or negative market news sentiment indicate elevated risk."
            )

        logger.info(f"RiskEvaluationService: Resolved assessment level '{risk_level}' for '{ticker_str}'")
        return RiskAssessment(
            ticker=ticker_str,
            risk_score=risk_score,
            risk_level=risk_level,
            risk_explanation=explanation,
            risk_factors=factors
        )
