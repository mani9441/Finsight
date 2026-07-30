from pathlib import Path
import streamlit as st
from core.constants import APP_TITLE, APP_TAGLINE

LOGO_PATH = Path("assets/logo.png")

# Modern Inline SVG Vector Logo
MODERN_SVG_LOGO = """
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 4px;">
    <svg width="38" height="38" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="40" height="40" rx="10" fill="url(#logo_grad)"/>
        <path d="M12 28L18 21L23 25L30 14" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M25 14H30V19" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="12" cy="28" r="2" fill="white"/>
        <circle cx="18" cy="21" r="2" fill="white"/>
        <circle cx="23" cy="25" r="2" fill="white"/>
        <circle cx="30" cy="14" r="2" fill="white"/>
        <defs>
            <linearGradient id="logo_grad" x1="0" y1="0" x2="40" y2="40" gradientUnits="userSpaceOnUse">
                <stop stop-color="#2563EB"/>
                <stop offset="1" stop-color="#1D4ED8"/>
            </linearGradient>
        </defs>
    </svg>
    <span style="font-size: 1.45rem; font-weight: 700; letter-spacing: -0.5px; color: #1E293B;">
        FinSight
    </span>
</div>
"""


def render_custom_sidebar(dashboard_page, price_page, ratios_page, risk_page, news_page, summary_page):
    """Renders sidebar elements with native line-art icons."""
    with st.sidebar:
        # 1. Branding Header
        if LOGO_PATH.exists():
            col_logo, col_title = st.columns([1, 4], vertical_alignment="center")
            with col_logo:
                st.image(str(LOGO_PATH), width=40)
            with col_title:
                st.markdown(f"### {APP_TITLE}")
        else:
            st.markdown(MODERN_SVG_LOGO, unsafe_allow_html=True)

        st.caption(APP_TAGLINE)
        st.divider()

        # 2. Custom Navigation Pages (Clean Material Line-Art Icons)
        st.markdown("**Overview**")
        st.page_link(dashboard_page, label="Dashboard", icon=":material/dashboard:")

        st.markdown("**Analysis**")
        st.page_link(price_page, label="Price Chart", icon=":material/show_chart:")
        st.page_link(ratios_page, label="Financial Ratios", icon=":material/analytics:")
        st.page_link(risk_page, label="Risk Assessment", icon=":material/shield:")

        st.markdown("**Intelligence**")
        st.page_link(news_page, label="News & Sentiment", icon=":material/newspaper:")
        st.page_link(summary_page, label="AI Summary", icon=":material/auto_awesome:")

        st.divider()

        # 3. Stock Search Section
        st.markdown("### Stock Search")

        ticker_input = st.text_input(
            "Ticker",
            value=st.session_state.get("ticker_input", ""),
            placeholder="AAPL, MSFT...",
            key="sidebar_ticker_input",
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Search", use_container_width=True, key="btn_sidebar_search"):
                if ticker_input.strip():
                    st.session_state.ticker_input = ticker_input.strip()
                    st.session_state.ui_state = "loading"
                    st.rerun()

        with col2:
            if st.button("Reset", use_container_width=True, key="btn_sidebar_reset"):
                st.session_state.ticker_input = ""
                st.session_state.ui_state = "empty"
                st.session_state.current_company = None
                st.rerun()