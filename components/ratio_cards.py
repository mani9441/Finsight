"""
UI component for rendering the Financial Ratios section cards.
"""

import streamlit as st
from models import FinancialRatios
from core import get_logger
from core.constants import THEME_COLORS
from typing import Optional


logger = get_logger("ratio_cards")

# Educational definitions for tooltips
RATIO_DESCRIPTIONS = {
    "pe_ratio": "Price-to-Earnings Ratio: Compares a company's share price to its earnings per share. High PE could mean high growth expectations or overvaluation.",
    "pb_ratio": "Price-to-Book Ratio: Compares market value to book value (net assets). Often used to evaluate bank stocks or identify undervalued assets.",
    "roe": "Return on Equity: Measures how effectively the company generates profit from shareholders' equity. Higher values indicate higher efficiency.",
    "profit_margin": "Profit Margin: Measures the percentage of revenue that turns into net income. Represents the pricing power and operational efficiency of the business.",
    "dividend_yield": "Dividend Yield: Represents the annual dividend payout relative to the current stock price. Shows cash returns on investment.",
    "eps": "Earnings Per Share: Portion of a company's profit allocated to each outstanding share of common stock. Indicates profitability on a per-share basis."
}

def render_individual_ratio_card(name: str, value_str: str, tooltip_desc: str):
    """
    Renders a single premium financial ratio card.
    """
    st.markdown(
        f"""
        <div class="glass-card" style="margin-bottom: 1rem; padding: 1.25rem;" title="{tooltip_desc}">
            <div class="status-label" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span>{name}</span>
                <span style="color: #60A5FA; cursor: help; font-size: 0.8rem;">ℹ️</span>
            </div>
            <div class="status-value" style="font-size: 1.45rem; color: #FFFFFF;">{value_str}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_company_ratios_module(ratios: FinancialRatios):
    """
    Renders the complete Financial Ratios module in a card-based grid layout.
    """
    logger.debug(f"Rendering Financial Ratios for: {ratios.ticker}")

    st.markdown("### 📊 Key Financial Ratios")

    # Format values helper
    def format_ratio(val: Optional[float], decimals: int = 2) -> str:
        if val is None:
            return "Not Available"
        return f"{val:,.{decimals}f}"

    def format_percentage(val: Optional[float]) -> str:
        if val is None:
            return "Not Available"
        scaled_val = val * 100.0
        # If scaled value is negative/positive, display clean decimals
        return f"{scaled_val:.2f}%"

    def format_eps(val: Optional[float], currency: str) -> str:
        if val is None:
            return "Not Available"
        currency_symbol = "$" if currency.upper() == "USD" else f"{currency} "
        return f"{currency_symbol}{val:,.2f}"

    # Format each of the 6 ratios
    pe_str = format_ratio(ratios.pe_ratio)
    pb_str = format_ratio(ratios.pb_ratio)
    roe_str = format_percentage(ratios.roe)
    pm_str = format_percentage(ratios.profit_margin)
    dy_str = format_percentage(ratios.dividend_yield)
    eps_str = format_eps(ratios.eps, ratios.currency)

    # Render in the suggested structure:
    # -----------------------------------------
    # P/E Ratio        | Price-to-Book
    # -----------------------------------------
    # Return on Equity | Profit Margin
    # -----------------------------------------
    # Dividend Yield   | Earnings Per Share
    # -----------------------------------------
    
    # Row 1
    col1, col2 = st.columns(2)
    with col1:
        render_individual_ratio_card("P/E Ratio", pe_str, RATIO_DESCRIPTIONS["pe_ratio"])
    with col2:
        render_individual_ratio_card("Price-to-Book (P/B)", pb_str, RATIO_DESCRIPTIONS["pb_ratio"])

    # Row 2
    col3, col4 = st.columns(2)
    with col3:
        render_individual_ratio_card("Return on Equity (ROE)", roe_str, RATIO_DESCRIPTIONS["roe"])
    with col4:
        render_individual_ratio_card("Profit Margin", pm_str, RATIO_DESCRIPTIONS["profit_margin"])

    # Row 3
    col5, col6 = st.columns(2)
    with col5:
        render_individual_ratio_card("Dividend Yield", dy_str, RATIO_DESCRIPTIONS["dividend_yield"])
    with col6:
        render_individual_ratio_card("Earnings Per Share (EPS)", eps_str, RATIO_DESCRIPTIONS["eps"])

    logger.info(f"Dashboard rendering completed for ratios of '{ratios.ticker}'")
