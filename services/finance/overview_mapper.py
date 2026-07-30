"""
Mapper utility for translating raw yfinance ticker info payloads into the standardized CompanyOverview model.
"""

from typing import Dict, Any, Optional
from models import CompanyOverview
from core import get_logger

logger = get_logger("overview_mapper")

class CompanyOverviewMapper:
    """
    Translates raw structures from Yahoo Finance into standardized CompanyOverview dataclass.
    """

    @staticmethod
    def to_company_overview(ticker: str, raw_info: Dict[str, Any]) -> CompanyOverview:
        """
        Maps raw yfinance ticker info to CompanyOverview dataclass.
        Applies defaults and fallbacks for missing data.
        """
        ticker_upper = ticker.strip().upper()
        
        name = raw_info.get("longName") or raw_info.get("shortName") or ticker_upper
        exchange = raw_info.get("exchange") or "Not Available"
        currency = "£"
        sector = raw_info.get("sector") or "Not Available"
        industry = raw_info.get("industry") or "Not Available"
        country = raw_info.get("country") or "Not Available"
        website = raw_info.get("website") or ""
        
        business_summary = raw_info.get("longBusinessSummary")
        if not business_summary or not business_summary.strip():
            business_summary = "Business description unavailable."
            
        # Parse market capitalization
        market_cap = raw_info.get("marketCap")
        parsed_market_cap = None
        if market_cap is not None:
            try:
                parsed_market_cap = float(market_cap)
            except (ValueError, TypeError):
                logger.warning(f"Could not parse marketCap '{market_cap}' as float for ticker '{ticker_upper}'")

        return CompanyOverview(
            name=name,
            ticker=ticker_upper,
            exchange=exchange,
            currency=currency,
            sector=sector,
            industry=industry,
            country=country,
            website=website,
            business_summary=business_summary,
            market_capitalization=parsed_market_cap
        )
