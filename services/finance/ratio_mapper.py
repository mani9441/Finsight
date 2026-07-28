"""
Mapper utility for translating raw yfinance ticker info payloads into the standardized FinancialRatios model.
"""

from typing import Dict, Any
from models import FinancialRatios
from services.common.ratio_validator import RatioResponseValidator

class FinancialRatioMapper:
    """
    Translates raw structures from Yahoo Finance into standardized FinancialRatios dataclass.
    """

    @staticmethod
    def to_financial_ratios(ticker: str, raw_info: Dict[str, Any]) -> FinancialRatios:
        """
        Maps raw yfinance ticker info to FinancialRatios dataclass.
        Filters out negative or invalid values where inappropriate.
        """
        ticker_upper = ticker.strip().upper()
        
        currency = raw_info.get("financialCurrency") or raw_info.get("currency") or "USD"
        
        # Parse P/E ratio (prefer trailing, fallback to forward)
        pe_val = raw_info.get("trailingPE") or raw_info.get("forwardPE")
        clean_pe = RatioResponseValidator.clean_ratio_value(pe_val, "pe_ratio", can_be_negative=False)
        
        # Parse P/B ratio
        pb_val = raw_info.get("priceToBook")
        clean_pb = RatioResponseValidator.clean_ratio_value(pb_val, "pb_ratio", can_be_negative=False)
        
        # Parse ROE
        roe_val = raw_info.get("returnOnEquity")
        clean_roe = RatioResponseValidator.clean_ratio_value(roe_val, "roe", can_be_negative=True)
        
        # Parse Profit Margin
        pm_val = raw_info.get("profitMargins")
        clean_pm = RatioResponseValidator.clean_ratio_value(pm_val, "profit_margin", can_be_negative=True)
        
        # Parse Dividend Yield
        dy_val = raw_info.get("dividendYield")
        clean_dy = RatioResponseValidator.clean_ratio_value(dy_val, "dividend_yield", can_be_negative=False)
        
        # Parse EPS (prefer trailing, fallback to forward)
        eps_val = raw_info.get("trailingEps") or raw_info.get("forwardEps")
        clean_eps = RatioResponseValidator.clean_ratio_value(eps_val, "eps", can_be_negative=True)

        return FinancialRatios(
            ticker=ticker_upper,
            currency=currency,
            pe_ratio=clean_pe,
            pb_ratio=clean_pb,
            roe=clean_roe,
            profit_margin=clean_pm,
            dividend_yield=clean_dy,
            eps=clean_eps
        )
