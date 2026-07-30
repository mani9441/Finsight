from pathlib import Path
import streamlit as st

LOGO_PATH = Path("assets/logo.png")

# Modern Inline SVG Vector Logo
HERO_SVG_LOGO = """
<div style="display: flex; justify-content: center; align-items: center; margin-bottom: 12px;">
    <svg width="64" height="64" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="40" height="40" rx="10" fill="url(#hero_logo_grad)"/>
        <path d="M12 28L18 21L23 25L30 14" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M25 14H30V19" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="12" cy="28" r="2" fill="white"/>
        <circle cx="18" cy="21" r="2" fill="white"/>
        <circle cx="23" cy="25" r="2" fill="white"/>
        <circle cx="30" cy="14" r="2" fill="white"/>
        <defs>
            <linearGradient id="hero_logo_grad" x1="0" y1="0" x2="40" y2="40" gradientUnits="userSpaceOnUse">
                <stop stop-color="#2563EB"/>
                <stop offset="1" stop-color="#1D4ED8"/>
            </linearGradient>
        </defs>
    </svg>
</div>
"""


def render_empty_state():
    """
    Renders an executive landing page guiding the user from:
    Hero Logo -> Title/Subtitle -> Central Search -> Trust Indicators -> Pipeline -> Capabilities -> Footer.
    """
    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 1. HERO SECTION & CENTRAL SEARCH
    # ---------------------------------------------------------
    hero_col1, hero_col2, hero_col3 = st.columns([1, 8, 1])
    with hero_col2:
        # Centered Logo above FinSight title
        if LOGO_PATH.exists():
            l_col1, l_col2, l_col3 = st.columns([2, 1, 2])
            with l_col2:
                st.image(str(LOGO_PATH), use_container_width=True)
        else:
            st.markdown(HERO_SVG_LOGO, unsafe_allow_html=True)

        st.markdown(
            "<h1 style='text-align: center; font-size: 2.8rem; margin-bottom: 0px;'>FinSight</h1>"
            "<h3 style='text-align: center; font-weight: 400; color: #6c757d; margin-top: 5px;'>Corporate Financial Intelligence Platform</h3>",
            unsafe_allow_html=True,
        )
        st.write("")
        st.markdown(
            "<p style='text-align: center; font-size: 1.15rem; color: #495057;'>"
            "Analyze companies using live market data, financial statements, AI insights, "
            "and news sentiment in one executive dashboard."
            "</p>",
            unsafe_allow_html=True,
        )
        st.write("")

        # Centerpiece Search Bar
        with st.form("hero_search_form", clear_on_submit=False):
            search_query = st.text_input(
                "Search public company...",
                value=st.session_state.get("ticker_input", ""),
                placeholder="Search public company... (e.g. Apple, AAPL, Microsoft, Tesla...)",
                key="empty_hero_input",
                label_visibility="collapsed",
            )

            # Centered Analyze Button
            btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
            with btn_col2:
                submitted = st.form_submit_button(
                    "Analyze Company →",
                    type="primary",
                    use_container_width=True,
                )

            if submitted and search_query.strip():
                st.session_state.ticker_input = search_query.strip()
                st.session_state.ui_state = "loading"
                st.rerun()

        st.write("")

        # Subtle Popular Search Chips
        st.markdown(
            "<p style='text-align: center; font-size: 0.88rem; color: #6c757d; margin-bottom: 8px;'><b>Popular Searches</b></p>",
            unsafe_allow_html=True,
        )

        chip_col1, chip_col2, chip_col3, chip_col4, chip_col5, chip_col6 = st.columns(6)

        popular_chips = [
            ("Apple", "AAPL", chip_col1),
            ("Microsoft", "MSFT", chip_col2),
            ("NVIDIA", "NVDA", chip_col3),
            ("Amazon", "AMZN", chip_col4),
            ("Alphabet", "GOOGL", chip_col5),
            ("Meta", "META", chip_col6),
        ]

        for label, ticker, col in popular_chips:
            with col:
                if st.button(f"○ {label}", key=f"chip_{ticker}", use_container_width=True):
                    st.session_state.ticker_input = ticker
                    st.session_state.ui_state = "loading"
                    st.rerun()

        st.write("")

        # Trust Indicators Row
        t1, t2, t3, t4, t5 = st.columns(5)
        t1.markdown("<p style='text-align: center; font-size: 0.85rem;'>✓ Live Market Data</p>", unsafe_allow_html=True)
        t2.markdown("<p style='text-align: center; font-size: 0.85rem;'>✓ Financial Ratios</p>", unsafe_allow_html=True)
        t3.markdown("<p style='text-align: center; font-size: 0.85rem;'>✓ Risk Assessment</p>", unsafe_allow_html=True)
        t4.markdown("<p style='text-align: center; font-size: 0.85rem;'>✓ News Sentiment</p>", unsafe_allow_html=True)
        t5.markdown("<p style='text-align: center; font-size: 0.85rem;'>✓ AI Executive Summary</p>", unsafe_allow_html=True)

    st.divider()

    # ---------------------------------------------------------
    # 2. HOW FINSIGHT WORKS (WORKFLOW PIPELINE)
    # ---------------------------------------------------------
    st.markdown("<h3 style='text-align: center;'>How FinSight Works</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6c757d;'>End-to-end analytical pipeline triggered instantly upon search.</p>", unsafe_allow_html=True)
    st.write("")

    w1, w2, w3, w4, w5 = st.columns(5)

    with w1:
        with st.container(border=True):
            st.markdown("**1. Search**")
            st.caption("Target public company or ticker symbol.")

    with w2:
        with st.container(border=True):
            st.markdown("**2. Collect Data**")
            st.caption("Ingest price history & balance sheet items.")

    with w3:
        with st.container(border=True):
            st.markdown("**3. Analyze News**")
            st.caption("Scrape market headlines & sentiment analysis.")

    with w4:
        with st.container(border=True):
            st.markdown("**4. Calculate Risk**")
            st.caption("Evaluate leverage, liquidity & volatility using ratios.")

    with w5:
        with st.container(border=True):
            st.markdown("**5. AI Briefing**")
            st.caption("Synthesize core investment thesis using LLM.")

    st.divider()

    # ---------------------------------------------------------
    # 3. CAPABILITY CARDS (Material Line-Art Icons)
    # ---------------------------------------------------------
    st.markdown("### Platform Capabilities")
    st.write("")

    cap_col1, cap_col2 = st.columns(2)

    with cap_col1:
        with st.container(border=True):
            st.markdown(":material/show_chart: **Market Intelligence**")
            st.markdown(
                """
                * **Historical price trends** across multiple timeframes
                * **Interactive charts** with custom volume overlays
                * **Volume analysis** & trading activity telemetry
                * **Multi-timeframe comparison** and performance baselines
                """
            )

        with st.container(border=True):
            st.markdown(":material/newspaper: **News Intelligence**")
            st.markdown(
                """
                * **Live company news** coverage from global publishers
                * **Sentiment scoring** (-1.0 to +1.0 spectrum)
                * **Positive / Negative trend** correlation against price
                * **Multi-source aggregation** filtered for market impact
                """
            )

    with cap_col2:
        with st.container(border=True):
            st.markdown(":material/analytics: **Financial Health**")
            st.markdown(
                """
                * **Profitability margins** (Gross, Operating, Net)
                * **Liquidity ratios** (Current, Quick, Cash position)
                * **Leverage & Debt** health indicators
                * **DuPont analysis** breaking down ROE efficiency
                """
            )

        with st.container(border=True):
            st.markdown(":material/auto_awesome: **AI Advisor**")
            st.markdown(
                """
                * **Executive summary** distilled from financial disclosures
                * **Investment thesis** outlining key bullish & bearish drivers
                * **Risk factor classification** (Market, Credit, Operational)
                * **Key takeaways** formatted for rapid executive briefings
                """
            )

    st.divider()

    # ---------------------------------------------------------
    # 4. FOOTER
    # ---------------------------------------------------------
    f_col1, f_col2, f_col3 = st.columns(3)

    with f_col1:
        st.caption("**Market Data:** Yahoo Finance API")
    with f_col2:
        st.caption("**AI Synthesis:** Advanced LLM Integration")
    with f_col3:
        st.caption("**News Telemetry:** Aggregated Financial News APIs")