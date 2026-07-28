from dataclasses import dataclass, field
from datetime import datetime
from typing import List

@dataclass
class RiskAssessment:
    """
    Evaluates corporate and market risks based on ratios and news sentiment.
    """
    ticker: str
    risk_score: float                     # Range e.g. 0.0 (safest) to 100.0 (riskiest)
    risk_level: str                       # Low Risk, Moderate Risk, High Risk
    risk_explanation: str = ""
    risk_factors: List[str] = field(default_factory=list)  # Detailed list of indicators
    assessed_at: datetime = field(default_factory=datetime.now)


@dataclass
class AISummary:
    """
    Stores LLM-generated advisor summary.
    """
    ticker: str
    executive_summary: str
    investment_thesis: str
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)
