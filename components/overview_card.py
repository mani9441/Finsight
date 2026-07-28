"""
UI widgets and page sections for rendering the Financial Overview Module.
"""

import streamlit as st
from models import CompanyOverview
from utils import format_large_number
from core import get_logger

logger = get_logger("overview_card")

def render_company_overview_module(overview: CompanyOverview):
    """
    Renders the Financial Overview module layout inside the dashboard.
    Uses glassmorphic styling and organizes information into logical cards.
    """
    logger.debug(f"Rendering Financial Overview for: {overview.ticker}")

    # Section Title
    st.markdown("### 🏢 Financial Overview")

    # 1. Company Identity Card (Row 1)
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="glass-card-title">💼 Company Identity</div>
            <div style="display: flex; flex-wrap: wrap; gap: 2rem; align-items: baseline;">
                <div>
                    <span class="status-label">Company Name</span>
                    <div style="font-size: 1.6rem; font-weight: 800; color: #FFFFFF; line-height: 1.2;">{overview.name}</div>
                </div>
                <div>
                    <span class="status-label">Stock Ticker</span>
                    <div style="font-size: 1.3rem; font-weight: 700; color: #3B82F6;">{overview.ticker}</div>
                </div>
                <div>
                    <span class="status-label">Exchange</span>
                    <div style="font-size: 1.3rem; font-weight: 600; color: #94A3B8;">{overview.exchange}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. Key Business Metrics & Classifications Grid (Row 2 & Row 3 & Row 4)
    # Let's organize these into structured columns
    col1, col2 = st.columns(2)

    with col1:
        # Business Classification Card
        st.markdown(
            f"""
            <div class="glass-card" style="height: 100%;">
                <div class="glass-card-title">🔍 Sector & Industry</div>
                <div class="status-grid" style="grid-template-columns: repeat(2, 1fr);">
                    <div class="status-item">
                        <div class="status-label">Sector</div>
                        <div class="status-value" style="font-size: 1.05rem;">{overview.sector}</div>
                    </div>
                    <div class="status-item">
                        <div class="status-label">Industry</div>
                        <div class="status-value" style="font-size: 1.05rem;">{overview.industry}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        # Market, Geographic, and Website details
        # Format Market Cap
        market_cap_raw = overview.market_capitalization
        market_cap_str = format_large_number(market_cap_raw)
        if market_cap_str != "N/A" and overview.currency and overview.currency != "Not Available":
            market_cap_str = f"{overview.currency} {market_cap_str}"
        elif market_cap_str == "N/A":
            market_cap_str = "Not Available"

        # Website formatting
        if overview.website:
            website_html = f'<a href="{overview.website}" target="_blank" style="color: #3B82F6; text-decoration: none; font-weight: 600;">{overview.website}</a>'
        else:
            website_html = '<span style="color: #64748B;">Not Available</span>'

        st.markdown(
            f"""
            <div class="glass-card" style="height: 100%;">
                <div class="glass-card-title">📊 Market & Identity</div>
                <div class="status-grid" style="grid-template-columns: repeat(2, 1fr); margin-bottom: 0.75rem;">
                    <div class="status-item">
                        <div class="status-label">Market Cap</div>
                        <div class="status-value" style="color: #10B981; font-size: 1.15rem;">{market_cap_str}</div>
                    </div>
                    <div class="status-item">
                        <div class="status-label">Country / Currency</div>
                        <div class="status-value" style="font-size: 1.05rem;">{overview.country} ({overview.currency})</div>
                    </div>
                </div>
                <div style="padding-top: 0.5rem; text-align: left;">
                    <span class="status-label" style="display: block; margin-bottom: 0.25rem;">Website</span>
                    <div style="font-size: 0.95rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        {website_html}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 3. Business Summary Panel
    # Multi-line text support: we can use standard HTML or streamlit text, but to keep the glass-card style we write it in HTML
    # escaping newlines is important.
    summary_clean = overview.business_summary.replace("\n", "<br>")
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="glass-card-title">📖 Business Summary</div>
            <p style="font-size: 0.95rem; color: #E2E8F0; line-height: 1.6; text-align: justify; margin: 0;">
                {summary_clean}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    logger.info(f"Rendering completion for overview of '{overview.ticker}'")
