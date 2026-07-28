"""
Rules Engine for evaluating investment risk levels.
Provides simple transparent boundary assertions.
"""

from typing import List, Tuple
from models import FinancialRatios, SentimentResult
from core import get_logger

logger = get_logger("risk_rules_engine")

class RiskRulesEngine:
    """
    Evaluates corporate ratios and market news sentiment against static risk thresholds.
    Determines factors and classification mapping: Low, Moderate, High.
    """

    @staticmethod
    def evaluate_factors(ratios: FinancialRatios, sentiment: SentimentResult) -> Tuple[List[str], str, float]:
        """
        Runs transparency rules on corporate inputs.
        Returns a tuple: (list_of_factors, risk_level, risk_score)
        """
        factors = []

        # 1. Valuation Risk Rules
        if ratios.pe_ratio is not None and ratios.pe_ratio > 35:
            factors.append("High P/E valuation (PE > 35) suggests high market premium pricing.")
        if ratios.pb_ratio is not None and ratios.pb_ratio > 6:
            factors.append("High P/B ratio (PB > 6) indicates premium price relative to core book value.")

        # 2. Profitability Risk Rules
        if ratios.roe is not None and ratios.roe < 0:
            factors.append("Negative Return on Equity (ROE < 0%) indicates inefficient capital allocation.")
        if ratios.profit_margin is not None and ratios.profit_margin < 0:
            factors.append("Negative profit margins indicate net operational losses.")
        if ratios.eps is not None and ratios.eps < 0:
            factors.append("Negative Earnings Per Share indicates the company is unprofitable on a per-share basis.")

        # 3. Sentiment Risk Rules
        if sentiment.sentiment_label == "Negative":
            factors.append("Negative overall news sentiment reflects poor public market perception.")
        elif sentiment.average_score < -0.10:
            factors.append("Average news sentiment polarity score is significantly negative (< -0.10).")

        factor_count = len(factors)

        # 4. Map active factor tally to category classifications
        # Low: 0-1 factors
        # Moderate: 2-3 factors
        # High: >= 4 factors
        if factor_count <= 1:
            risk_level = "Low Risk"
            risk_score = 15.0
        elif factor_count <= 3:
            risk_level = "Moderate Risk"
            risk_score = 50.0
        else:
            risk_level = "High Risk"
            risk_score = 85.0

        logger.info(
            f"RiskRulesEngine resolved {factor_count} factors for {ratios.ticker}: "
            f"Level='{risk_level}' (Score={risk_score})"
        )
        return factors, risk_level, risk_score
