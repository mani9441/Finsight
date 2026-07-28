from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class HistoricalPrice:
    """
    Represents a single day's pricing and volume data.
    """
    date: datetime
    open_val: float
    high_val: float
    low_val: float
    close_val: float
    volume: int


@dataclass
class FinancialMetrics:
    """
    Captures primary financial indicators, margins, and ratios.
    """
    ticker: str
    currency: str
    
    # Valuation
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    enterprise_value: Optional[float] = None
    
    # Income & Margins
    revenue: Optional[float] = None
    gross_profit: Optional[float] = None
    ebitda: Optional[float] = None
    net_income: Optional[float] = None
    gross_margin: Optional[float] = None       # e.g., 0.42 for 42%
    operating_margin: Optional[float] = None   # e.g., 0.18
    profit_margin: Optional[float] = None      # e.g., 0.12
    eps: Optional[float] = None
    
    # Solvency & Performance
    debt_to_equity: Optional[float] = None
    free_cash_flow: Optional[float] = None
    roe: Optional[float] = None                 # Return on Equity
    roa: Optional[float] = None                 # Return on Assets
