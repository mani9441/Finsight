"""
UI component for rendering Financial Ratios in a Rich White Card theme.
"""

import streamlit as st
from models import FinancialRatios
from core import get_logger
from typing import Optional

logger = get_logger("ratio_cards")

# SVG Icons
ICON_INFO = """<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#64748B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>"""
ICON_CHART_BAR = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="20" x2="12" y2="10"></line><line x1="18" y1="20" x2="18" y2="4"></line><line x1="6" y1="20" x2="6" y2="16"></line></svg>"""

RATIO_METADATA = {
    "pe_ratio": {
        "title": "P/E Ratio",
        "category": "Valuation",
        "desc": "Price-to-Earnings Ratio: Compares share price to net earnings per share."
    },
    "pb_ratio": {
        "title": "Price-to-Book (P/B)",
        "category": "Valuation",
        "desc": "Price-to-Book Ratio: Compares market cap against net book value of assets."
    },
    "roe": {
        "title": "Return on Equity (ROE)",
        "category": "Profitability",
        "desc": "Return on Equity: Measures net income generated per dollar of equity."
    },
    "profit_margin": {
        "title": "Profit Margin",
        "category": "Profitability",
        "desc": "Net Profit Margin: Percentage of revenue converted into net bottom-line income."
    },
    "dividend_yield": {
        "title": "Dividend Yield",
        "category": "Shareholder Return",
        "desc": "Dividend Yield: Annual dividend payout relative to current stock price."
    },
    "eps": {
        "title": "Earnings Per Share (EPS)",
        "category": "Profitability",
        "desc": "Earnings Per Share: Portion of company profit allocated to each share."
    }
}

# Embedded CSS overlay for UI enhancements
_RATIO_CARD_CSS = """
<style>
    .ratio-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.1rem 1.25rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .ratio-card:hover {
        border-color: #CBD5E1;
        box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.06);
        transform: translateY(-2px);
    }
    .ratio-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.35rem;
    }
    .ratio-title-group {
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .ratio-title {
        font-size: 0.82rem;
        font-weight: 600;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .ratio-category-pill {
        font-size: 0.68rem;
        font-weight: 600;
        color: #2563EB;
        background: #EFF6FF;
        padding: 0.15rem 0.45rem;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }
    .ratio-value {
        font-size: 1.55rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.02em;
        margin: 0.2rem 0;
    }
    .ratio-desc {
        font-size: 0.75rem;
        color: #64748B;
        line-height: 1.35;
        margin-top: 0.35rem;
        border-top: 1px solid #F1F5F9;
        padding-top: 0.35rem;
    }
    .module-title {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1.1rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 1rem;
    }
</style>
"""


def render_individual_ratio_card(key: str, value_str: str):
    """
    Renders a clean white corporate metric card with tooltips and contextual metadata.
    """
    meta = RATIO_METADATA.get(key, {"title": key, "category": "Metric", "desc": ""})
    
    st.markdown(
        f"""
        <div class="ratio-card">
            <div class="ratio-header">
                <div class="ratio-title-group">
                    <span class="ratio-title">{meta['title']}</span>
                </div>
                <span class="ratio-category-pill">{meta['category']}</span>
            </div>
            <div class="ratio-value">{value_str}</div>
            <div class="ratio-desc">{meta['desc']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_company_ratios_module(ratios: FinancialRatios):
    """
    Renders the Financial Ratios grid layout.
    """
    logger.debug(f"Rendering Financial Ratios for: {ratios.ticker}")
    st.markdown(_RATIO_CARD_CSS, unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="module-title">
            {ICON_CHART_BAR} Key Financial Ratios
        </div>
        """,
        unsafe_allow_html=True
    )

    def format_ratio(val: Optional[float], decimals: int = 2) -> str:
        return "N/A" if val is None else f"{val:,.{decimals}f}"

    def format_percentage(val: Optional[float]) -> str:
        return "N/A" if val is None else f"{val * 100.0:.2f}%"

    def format_eps(val: Optional[float], currency: str) -> str:
        if val is None:
            return "N/A"
        symbol = "$" if currency.upper() == "USD" else f"{currency} "
        return f"{symbol}{val:,.2f}"

    pe_str = format_ratio(ratios.pe_ratio)
    pb_str = format_ratio(ratios.pb_ratio)
    roe_str = format_percentage(ratios.roe)
    pm_str = format_percentage(ratios.profit_margin)
    dy_str = format_percentage(ratios.dividend_yield)
    eps_str = format_eps(ratios.eps, ratios.currency)

    col1, col2 = st.columns(2)
    with col1:
        render_individual_ratio_card("pe_ratio", pe_str)
    with col2:
        render_individual_ratio_card("pb_ratio", pb_str)

    col3, col4 = st.columns(2)
    with col3:
        render_individual_ratio_card("roe", roe_str)
    with col4:
        render_individual_ratio_card("profit_margin", pm_str)

    col5, col6 = st.columns(2)
    with col5:
        render_individual_ratio_card("dividend_yield", dy_str)
    with col6:
        render_individual_ratio_card("eps", eps_str)

    logger.info(f"Dashboard rendering completed for ratios of '{ratios.ticker}'")