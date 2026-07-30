"""
Mapper utility for translating yfinance API payloads into core domain models.
"""

import pandas as pd
from typing import Dict, Any, List
from models import CompanyInfo, FinancialMetrics, HistoricalPrice
from core import get_logger

logger = get_logger("finance_mapper")

class FinanceMapper:
    """
    Translates raw structures from Yahoo Finance into standardized dataclasses.
    """

    @staticmethod
    def to_company_info(ticker: str, raw_info: Dict[str, Any]) -> CompanyInfo:
        """
        Maps raw yfinance ticker info to CompanyInfo dataclass.
        """
        name = raw_info.get("longName") or raw_info.get("shortName") or ticker
        sector = raw_info.get("sector") or "Unknown"
        industry = raw_info.get("industry") or "Unknown"
        summary = raw_info.get("longBusinessSummary") or "No business summary available."
        website = raw_info.get("website") or ""
        logo_url = raw_info.get("logo_url") or ""

        # Map officers
        raw_officers = raw_info.get("companyOfficers") or []
        officers = []
        for officer in raw_officers:
            officers.append({
                "name": officer.get("name", "Unknown"),
                "title": officer.get("title", "Unknown")
            })

        return CompanyInfo(
            ticker=ticker.upper(),
            name=name,
            sector=sector,
            industry=industry,
            summary=summary,
            website=website,
            logo_url=logo_url,
            officers=officers
        )

    @staticmethod
    def to_financial_metrics(ticker: str, raw_info: Dict[str, Any]) -> FinancialMetrics:
        """
        Maps raw yfinance info details to FinancialMetrics dataclass.
        """
        currency = "£"

        # Float conversion helper
        def get_float(key: str) -> Any:
            val = raw_info.get(key)
            if val is None:
                return None
            try:
                return float(val)
            except (ValueError, TypeError):
                return None

        return FinancialMetrics(
            ticker=ticker.upper(),
            currency=currency,
            
            # Valuation ratios
            market_cap=get_float("marketCap"),
            pe_ratio=get_float("trailingPE") or get_float("forwardPE"),
            ps_ratio=get_float("priceToSalesTrailing12Months"),
            pb_ratio=get_float("priceToBook"),
            enterprise_value=get_float("enterpriseValue"),
            
            # Income metrics
            revenue=get_float("totalRevenue"),
            gross_profit=get_float("grossProfits") or get_float("grossProfit"),
            ebitda=get_float("ebitda"),
            net_income=get_float("netIncomeToCommon") or get_float("netIncome"),
            gross_margin=get_float("grossMargins"),
            operating_margin=get_float("operatingMargins"),
            profit_margin=get_float("profitMargins"),
            eps=get_float("trailingEps"),
            
            # Solvency & performance
            debt_to_equity=get_float("debtToEquity"),
            free_cash_flow=get_float("freeCashflow"),
            roe=get_float("returnOnEquity"),
            roa=get_float("returnOnAssets")
        )

    @staticmethod
    def to_historical_prices(history_df: pd.DataFrame) -> List[HistoricalPrice]:
        """
        Maps a pandas DataFrame returned by yfinance history() to a list of HistoricalPrice models.
        """
        prices = []
        if history_df.empty:
            return prices

        for index, row in history_df.iterrows():
            # Handle index being a DatetimeIndex
            date_val = index.to_pydatetime() if hasattr(index, "to_pydatetime") else index
            
            # yfinance returns lowercase/title columns (Open, High, Low, Close, Volume)
            prices.append(
                HistoricalPrice(
                    date=date_val,
                    open_val=float(row.get("Open", 0.0)),
                    high_val=float(row.get("High", 0.0)),
                    low_val=float(row.get("Low", 0.0)),
                    close_val=float(row.get("Close", 0.0)),
                    volume=int(row.get("Volume", 0))
                )
            )
        return prices
