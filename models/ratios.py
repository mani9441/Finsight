from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class FinancialRatios:
    """
    Standardized internal model representing a company's key financial ratios.
    Stores valuation, profitability, earnings, and dividend indicators.
    """
    ticker: str
    currency: str
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    roe: Optional[float] = None
    profit_margin: Optional[float] = None
    dividend_yield: Optional[float] = None
    eps: Optional[float] = None
    last_updated: datetime = field(default_factory=datetime.now)
