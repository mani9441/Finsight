"""
FinSight Main Entry Point.
Initializes configuration, logging, injects custom styles, and displays a
highly aesthetic system verification dashboard.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path

# Import Core & Config subsystems
from config.settings import settings
from core import setup_logging, get_logger
from core.constants import (
    APP_TITLE,
    APP_TAGLINE,
    THEME_COLORS,
    DEFAULT_CHART_LAYOUT
)
from utils.helpers import (
    format_currency,
    format_large_number,
    format_percent,
    get_date_range_days_ago
)

# Initialize logging system
setup_logging()
logger = get_logger("app")

def load_css():
    """
    Reads the main CSS file and injects it into the Streamlit page.
    """
    css_path = Path(settings.BASE_DIR) / "assets" / "styles" / "main.css"
    if css_path.exists():
        try:
            with open(css_path, "r", encoding="utf-8") as f:
                css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
            logger.info("Custom CSS style injected successfully.")
        except Exception as e:
            logger.error(f"Error loading custom stylesheet: {e}")
    else:
        logger.warning(f"CSS stylesheet not found at path: {css_path}")

def render_mockup_chart():
    """
    Generates a beautiful mock financial chart to verify Plotly integration
    and demonstrate custom styling constants.
    """
    # Generating mock stock trend
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now(), periods=30)
    prices = 150.0 + np.random.randn(30).cumsum() * 3

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, 
        y=prices, 
        mode='lines+markers', 
        name='Stock Value',
        line=dict(color=THEME_COLORS["SECONDARY"], width=3),
        marker=dict(size=6, color=THEME_COLORS["SUCCESS"])
    ))

    # Apply global chart formatting constants
    fig.update_layout(
        title="Mock Market Verification Trend (30 Days)",
        xaxis_title="Timeline",
        yaxis_title="Price ($)",
        height=320,
        **DEFAULT_CHART_LAYOUT
    )
    st.plotly_chart(fig, use_container_width=True)

def main():
    logger.info("Launching Streamlit Main App render...")
    
    # 1. Streamlit Page Setup
    st.set_page_config(
        page_title=f"{APP_TITLE} | Foundation Setup",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 2. Inject Styles
    load_css()

    # 3. Sidebar Configuration
    st.sidebar.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #FFFFFF; font-size: 1.8rem; font-weight: 800; margin-bottom: 0px;">⚡ {APP_TITLE}</h1>
            <p style="color: #94A3B8; font-size: 0.8rem;">{APP_TAGLINE}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.sidebar.markdown("### 🛠️ Core Diagnostics")
    
    # Sidebar environment metrics card
    st.sidebar.markdown(
        f"""
        <div class="glass-card" style="padding: 1rem; margin-bottom: 1.5rem;">
            <div class="status-label">Environment</div>
            <div class="status-value"><span class="badge badge-info">{settings.APP_ENV}</span></div>
            <div style="height: 10px;"></div>
            <div class="status-label">Logging Level</div>
            <div class="status-value">{settings.LOG_LEVEL}</div>
            <div style="height: 10px;"></div>
            <div class="status-label">Debug Mode</div>
            <div class="status-value">{"Enabled" if settings.DEBUG else "Disabled"}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Sidebar Navigation Mockups
    st.sidebar.markdown("### 📂 Navigation (Mockup)")
    st.sidebar.radio(
        "Select Dashboard View:",
        ["Foundation Diagnostics", "Market Analysis", "Sentiment Insights", "Advisory Center"],
        index=0
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💾 Configuration Actions")
    if st.sidebar.button("Reload .env Config"):
        st.cache_data.clear()
        st.success("App configuration reload triggered.")
        logger.info("Manual reload triggered via UI button.")

    # 4. Main Panel Render
    # Header Hero Section
    st.markdown(
        f"""
        <div class="hero-section">
            <h1 class="hero-title">{APP_TITLE}</h1>
            <p class="hero-subtitle">{APP_TAGLINE} | Phase 1 Foundation Active</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Main columns
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown(
            """
            <div class="glass-card">
                <div class="glass-card-title">🛡️ System Readiness & Checks</div>
                <p style="color: #94A3B8; font-size: 0.95rem;">
                    All directory structures, configuration modules, custom error models, and logging systems have loaded successfully.
                </p>
                <div class="status-grid">
                    <div class="status-item">
                        <div class="status-label">Config System</div>
                        <div class="badge badge-success">Loaded</div>
                    </div>
                    <div class="status-item">
                        <div class="status-label">Logging Handler</div>
                        <div class="badge badge-success">Active</div>
                    </div>
                    <div class="status-item">
                        <div class="status-label">Core Constants</div>
                        <div class="badge badge-success">Ready</div>
                    </div>
                    <div class="status-item">
                        <div class="status-label">Exceptions Base</div>
                        <div class="badge badge-success">Verified</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Plotly Verification Container
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="glass-card-title">📈 Chart Styling Integration</div>', unsafe_allow_html=True)
        render_mockup_chart()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(
            """
            <div class="glass-card">
                <div class="glass-card-title">🎛️ Utility Helper Verification</div>
                <p style="color: #94A3B8; font-size: 0.9rem; margin-bottom: 1.5rem;">
                    Interact with this panel to verify date-parsers, currency, percentage, and large-number helper functions in the utils module.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Interactive widgets inside a container
        with st.container():
            # Test number formatter
            raw_num = st.number_input("Enter Numeric Value:", value=1542300.0, step=100.0)
            
            # Format outputs
            formatted_currency = format_currency(raw_num)
            formatted_compact = format_large_number(raw_num)
            formatted_pct = format_percent(raw_num / 1000000.0, is_multiplier=True)

            st.markdown(
                f"""
                <div class="glass-card" style="margin-top: 1rem;">
                    <div style="display: flex; justify-content: space-between; padding: 0.5rem 0;">
                        <span style="color: #94A3B8;">Currency format:</span>
                        <strong style="color: {THEME_COLORS["SUCCESS"]};">{formatted_currency}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 0.5rem 0;">
                        <span style="color: #94A3B8;">Compact Suffix format:</span>
                        <strong style="color: {THEME_COLORS["SECONDARY"]};">{formatted_compact}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 0.5rem 0;">
                        <span style="color: #94A3B8;">Percentage format (scaled):</span>
                        <strong style="color: {THEME_COLORS["WARNING"]};">{formatted_pct}</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Date calculations verification
        st.markdown(
            """
            <div class="glass-card">
                <div class="glass-card-title">📅 Date Calculations</div>
            """,
            unsafe_allow_html=True
        )
        days_ago = st.slider("Select Days Window:", min_value=1, max_value=365, value=30)
        start_d, end_d = get_date_range_days_ago(days_ago)
        st.markdown(
            f"""
            <div style="font-size: 0.85rem; color: #E2E8F0;">
                <strong>Start range:</strong> {start_d.strftime('%Y-%m-%d %H:%M')}<br/>
                <strong>End range:</strong> {end_d.strftime('%Y-%m-%d %H:%M')}
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Footer
    st.markdown(
        f"""
        <div class="footer-text">
            FinSight Phase 1 Project Foundation Dashboard • Runtime logs are writing to {settings.LOG_FILE_PATH} • Refreshed at {datetime.now().strftime('%H:%M:%S')}
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
