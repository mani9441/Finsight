from dataclasses import dataclass
from typing import Optional

@dataclass
class CompanyOverview:
    """
    Standardized internal model representing a company's high-level financial overview.
    No provider-specific field names are exposed.
    """
    name: str
    ticker: str
    exchange: str
    currency: str
    sector: str
    industry: str
    country: str
    website: str
    business_summary: str
    market_capitalization: Optional[float] = None
