"""
FinSight Entry Point.
Implements the user interface foundation, session state machine, and dashboard layout.
Uses a mock application controller pipeline to populate UI cards and charts.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import List, Optional

# Core configurations
from config import settings
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

# Base models
from models import (
    CompanyInfo,
    FinancialMetrics,
    HistoricalPrice,
    NewsArticle,
    SentimentResult,
    RiskAssessment,
    AISummary,
)

# Services and Controller
from services.interfaces import (
    ICompanySearchService,
    IFinancialService,
    INewsService,
    ISentimentService,
    IRiskService,
    IAISummaryService,
)
from services.controller import ApplicationController
from services.common.response_validator import ResponseValidator
from core.exceptions import InvalidInputError

# UI components
from components.empty_state import render_empty_state
from components.loaders import render_skeleton_loader, render_section_loader
from components.errors import render_error_banner, render_warning_banner
from components.cards import (
    render_company_profile_card,
    render_metric_card,
    render_sentiment_card,
    render_risk_card,
    render_ai_advisory_card
)

# Initialize logging
setup_logging()
logger = get_logger("app_ui")

# =====================================================================
# Mock Service Implementations for Phase 4 Visual Validation
# =====================================================================

class MockCompanySearchService(ICompanySearchService):
    def search_companies(self, query: str) -> List[CompanyInfo]:
        profile = self.get_profile(query)
        return [profile] if profile else []

    def get_profile(self, ticker: str) -> Optional[CompanyInfo]:
        t = ticker.upper().strip()
        if t == "AAPL":
            return CompanyInfo(
                ticker="AAPL", name="Apple Inc.", sector="Technology",
                industry="Consumer Electronics", website="https://www.apple.com",
                summary="Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide. The company also sells various related services."
            )
        elif t == "MSFT":
            return CompanyInfo(
                ticker="MSFT", name="Microsoft Corporation", sector="Technology",
                industry="Software - Infrastructure", website="https://www.microsoft.com",
                summary="Microsoft Corporation develops, licenses, and supports software, services, devices, and solutions worldwide. The company operates in Productivity, Intelligent Cloud, and More Personal Computing segments."
            )
        elif t == "GOOGL":
            return CompanyInfo(
                ticker="GOOGL", name="Alphabet Inc.", sector="Communication Services",
                industry="Internet Content & Information", website="https://abc.xyz",
                summary="Alphabet Inc. offers various products and platforms in the United States, Europe, the Middle East, Africa, the Asia-Pacific, Canada, and Latin America."
            )
        else:
            return CompanyInfo(
                ticker=t, name=f"{t} Corporation", sector="Financials",
                industry="Asset Management", website=f"https://www.{t.lower()}.com",
                summary=f"This is a placeholder description for {t} Corporation. It provides mock financial products, assets allocation services, and general market consultations globally."
            )


class MockFinancialService(IFinancialService):
    def get_financial_metrics(self, ticker: str) -> Optional[FinancialMetrics]:
        t = ticker.upper().strip()
        # Custom mock metrics
        if t == "AAPL":
            return FinancialMetrics(
                ticker=t, currency="USD", market_cap=2950000000000.0,
                pe_ratio=31.4, ps_ratio=7.6, pb_ratio=38.2, enterprise_value=2980000000000.0,
                revenue=383280000000.0, gross_profit=170000000000.0, ebitda=125000000000.0,
                net_income=96990000000.0, gross_margin=0.441, operating_margin=0.301,
                profit_margin=0.253, eps=6.13, debt_to_equity=145.8, free_cash_flow=99500000000.0,
                roe=1.54, roa=0.27
            )
        else:
            return FinancialMetrics(
                ticker=t, currency="USD", market_cap=540000000000.0,
                pe_ratio=22.5, ps_ratio=4.8, pb_ratio=6.2, enterprise_value=550000000000.0,
                revenue=112000000000.0, gross_profit=48000000000.0, ebitda=29000000000.0,
                net_income=18500000000.0, gross_margin=0.428, operating_margin=0.258,
                profit_margin=0.165, eps=3.45, debt_to_equity=68.4, free_cash_flow=14500000000.0,
                roe=0.185, roa=0.092
            )

    def get_historical_prices(self, ticker: str, start_date: datetime, end_date: datetime) -> List[HistoricalPrice]:
        # Generate 30 days of mock stock pricing
        np.random.seed(42)
        days = (end_date - start_date).days
        dates = pd.date_range(start=start_date, end=end_date, periods=days)
        prices = []
        base_price = 180.0 if ticker.upper() == "AAPL" else 120.0
        
        current_price = base_price
        for d in dates:
            change = np.random.normal(0.2, 2.5)
            open_p = current_price
            close_p = current_price + change
            high_p = max(open_p, close_p) + abs(np.random.normal(1.0, 0.5))
            low_p = min(open_p, close_p) - abs(np.random.normal(1.0, 0.5))
            vol = int(np.random.normal(55000000, 15000000))
            
            prices.append(HistoricalPrice(
                date=d, open_val=open_p, high_val=high_p, low_val=low_p, close_val=close_p, volume=vol
            ))
            current_price = close_p
            
        return prices


class MockNewsService(INewsService):
    def get_recent_news(self, ticker: str, limit: int = 10) -> List[NewsArticle]:
        return [
            NewsArticle(
                title=f"{ticker} announces quarterly earnings beating wall street expectations",
                source="Yahoo Finance", published_at=datetime.now() - timedelta(hours=3),
                url="https://finance.yahoo.com", summary="The earnings report beat expectations on strong server demands.",
                content=""
            ),
            NewsArticle(
                title=f"Regulatory changes could impact {ticker} operations next fiscal year",
                source="Wall Street Journal", published_at=datetime.now() - timedelta(days=1),
                url="https://wsj.com", summary="Analysts review the structural guidelines passed by federal agencies.",
                content=""
            )
        ]


class MockSentimentService(ISentimentService):
    def analyze_sentiment(self, articles: List[NewsArticle]) -> SentimentResult:
        return SentimentResult(
            ticker="MOCK", average_score=0.28, sentiment_label="Positive",
            article_count=len(articles), positive_count=1, negative_count=0, neutral_count=1
        )


class MockRiskService(IRiskService):
    def assess_risk(self, metrics: FinancialMetrics, sentiment: SentimentResult) -> RiskAssessment:
        # Evaluate mock risk based on debt metrics
        debt_level = metrics.debt_to_equity or 0.0
        risk_score = min(max(debt_level * 0.3 + (1.0 - sentiment.average_score) * 20.0, 10.0), 95.0)
        risk_level = "Low"
        if risk_score > 75.0:
            risk_level = "Critical"
        elif risk_score > 50.0:
            risk_level = "High"
        elif risk_score > 30.0:
            risk_level = "Medium"

        return RiskAssessment(
            ticker=metrics.ticker, risk_score=risk_score, risk_level=risk_level,
            risk_factors=[
                "Sensitivity to industry regulations and compliance guidelines.",
                f"Debt-to-equity leverage calculated at {debt_level:.1f}%.",
                "Competitive pressure in segment operations."
            ]
        )


class MockAISummaryService(IAISummaryService):
    def generate_advisory_summary(
        self, company_info: CompanyInfo, metrics: FinancialMetrics, sentiment: SentimentResult, risk: RiskAssessment
    ) -> AISummary:
        exec_summary = (
            f"An executive review of {company_info.name} ({company_info.ticker}) suggests a favorable corporate setup. "
            f"Trading multipliers highlight key valuation levels, while news channels indicate a {sentiment.sentiment_label.lower()} market sentiment. "
            f"Evaluations on leverage ratios indicate risk parameters are under a {risk.risk_level.lower()} threat level."
        )
        thesis = f"Long-term trends remain favorable despite short-term fluctuations in {company_info.sector}."
        
        return AISummary(
            ticker=company_info.ticker,
            executive_summary=exec_summary,
            investment_thesis=thesis,
            strengths=[f"Favorable position in {company_info.industry} segment.", "Healthy operational cash flows."],
            weaknesses=["Increasing operational overhead constraints.", "Currency conversion exposures."]
        )

# =====================================================================
# Main Streamlit Application UI
# =====================================================================

def load_css():
    """
    Injects the custom main.css theme file.
    """
    css_path = Path(settings.BASE_DIR) / "assets" / "styles" / "main.css"
    if css_path.exists():
        try:
            with open(css_path, "r", encoding="utf-8") as f:
                css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        except Exception as e:
            logger.error(f"Error loading custom main.css stylesheet: {e}")


def initialize_session_state():
    """
    Prepares session state variables for navigation and search tracking.
    """
    if "ticker_input" not in st.session_state:
        st.session_state.ticker_input = ""
    if "selected_company" not in st.session_state:
        st.session_state.selected_company = None
    if "ui_state" not in st.session_state:
        st.session_state.ui_state = "empty"  # empty, loading, success, error
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = None
    if "error_message" not in st.session_state:
        st.session_state.error_message = ""


def render_header():
    """
    Renders branding header at top of main dashboard panel.
    """
    st.markdown(
        f"""
        <div class="hero-section">
            <h1 class="hero-title">{APP_TITLE}</h1>
            <p class="hero-subtitle">{APP_TAGLINE} | UI Blueprint Dashboard</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def draw_historical_chart(prices: List[HistoricalPrice]):
    """
    Draws a line plot of closing prices and bar plot of volume using Plotly.
    """
    if not prices:
        st.info("No pricing history available to chart.")
        return

    dates = [p.date for p in prices]
    closes = [p.close_val for p in prices]
    volumes = [p.volume for p in prices]

    # Create subplots using go.Figure
    fig = go.Figure()
    
    # Close price trace
    fig.add_trace(go.Scatter(
        x=dates, y=closes, mode='lines', name='Close Price',
        line=dict(color=THEME_COLORS["SECONDARY"], width=3)
    ))

    # Add bar chart for volume on a secondary y-axis if possible
    # For simplicity, we can plot them in a single styled chart or layout
    fig.update_layout(
        title="Historical Price Trend (Daily Closes)",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        height=320,
        **DEFAULT_CHART_LAYOUT
    )
    st.plotly_chart(fig, use_container_width=True)


def trigger_search_pipeline(ticker: str):
    """
    Executes search and switches session states.
    In Phase 4, we use mock services in the controller pipeline.
    """
    ticker_clean = ticker.strip().upper()
    try:
        # Validate syntax
        ResponseValidator.validate_ticker_input(ticker_clean)
        
        # Set loading state
        st.session_state.ui_state = "loading"
        st.session_state.selected_company = ticker_clean
        st.session_state.error_message = ""
        
        logger.info(f"UI state set to LOADING for ticker {ticker_clean}")
        
    except InvalidInputError as e:
        st.session_state.ui_state = "error"
        st.session_state.error_message = str(e)
        st.session_state.selected_company = None
        st.session_state.analysis_results = None
        logger.warning(f"Validation failed for query '{ticker}': {e}")


def execute_mock_analysis():
    """
    Orchestrates mock service flows inside the controller pipeline.
    Runs only while session state is in 'loading'.
    """
    ticker = st.session_state.selected_company
    logger.info(f"Running mock analysis pipeline for {ticker}")
    
    # Instantiate mock layers
    mock_company = MockCompanySearchService()
    mock_finance = MockFinancialService()
    mock_news = MockNewsService()
    mock_sentiment = MockSentimentService()
    mock_risk = MockRiskService()
    mock_ai = MockAISummaryService()
    
    controller = ApplicationController(
        company_service=mock_company,
        financial_service=mock_finance,
        news_service=mock_news,
        sentiment_service=mock_sentiment,
        risk_service=mock_risk,
        ai_service=mock_ai
    )
    
    # Execute analysis (the controller catches sub-errors itself)
    results = controller.analyze_ticker(ticker, date_window_days=30)
    
    # Evaluate output
    if results.get("profile") is None:
        st.session_state.ui_state = "error"
        # Extract the profile error
        profile_errors = [err for err in results.get("errors", []) if "Profile" in err]
        st.session_state.error_message = profile_errors[0] if profile_errors else f"Unable to resolve symbol {ticker}."
        st.session_state.analysis_results = None
        logger.warning(f"Mock analysis failed for {ticker}")
    else:
        st.session_state.analysis_results = results
        st.session_state.ui_state = "success"
        logger.info(f"Mock analysis completed with success status for {ticker}")


def main():
    # Setup Streamlit page configuration
    st.set_page_config(
        page_title=f"{APP_TITLE} | Dashboard Framework",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Load custom theme stylesheet
    load_css()

    # Setup state
    initialize_session_state()

    # =====================================================================
    # SIDEBAR CONTROLS
    # =====================================================================
    st.sidebar.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #FFFFFF; font-size: 1.8rem; font-weight: 800; margin-bottom: 0px;">⚡ {APP_TITLE}</h1>
            <p style="color: #94A3B8; font-size: 0.8rem;">{APP_TAGLINE}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.sidebar.markdown("### 🔍 Search Company")
    
    # Input field and button
    ticker_query = st.sidebar.text_input(
        "Enter Stock Ticker or Name:", 
        value=st.session_state.ticker_input,
        max_chars=10, 
        placeholder="e.g. AAPL, MSFT, GOOGL"
    )
    
    col_btn_search, col_btn_clear = st.sidebar.columns([1, 1])
    
    with col_btn_search:
        if st.button("Analyze", use_container_width=True):
            if ticker_query:
                st.session_state.ticker_input = ticker_query
                trigger_search_pipeline(ticker_query)
                st.rerun()
            else:
                st.sidebar.warning("Please enter a ticker value.")
                
    with col_btn_clear:
        if st.button("Reset", use_container_width=True):
            st.session_state.ticker_input = ""
            st.session_state.selected_company = None
            st.session_state.ui_state = "empty"
            st.session_state.analysis_results = None
            st.session_state.error_message = ""
            logger.info("Session state reset triggered.")
            st.rerun()

    # Suggestions shortcuts
    st.sidebar.markdown("#### Suggested Tickers")
    cols_suggestions = st.sidebar.columns(3)
    suggestions = ["AAPL", "MSFT", "GOOGL"]
    for idx, sug in enumerate(suggestions):
        with cols_suggestions[idx]:
            if st.button(sug, key=f"sug_{sug}", use_container_width=True):
                st.session_state.ticker_input = sug
                trigger_search_pipeline(sug)
                st.rerun()

    st.sidebar.markdown("---")
    
    # Sidebar status panel
    st.sidebar.markdown("### 🛠️ Subsystems Status")
    st.sidebar.markdown(
        f"""
        <div class="glass-card" style="padding: 1rem; margin-bottom: 1.5rem;">
            <div class="status-label">Active State</div>
            <div class="status-value"><span class="badge badge-info">{st.session_state.ui_state}</span></div>
            <div style="height: 10px;"></div>
            <div class="status-label">Environment</div>
            <div class="status-value">{settings.APP_ENV}</div>
            <div style="height: 10px;"></div>
            <div class="status-label">Mock data</div>
            <div class="status-value">Active Blueprint</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================================
    # MAIN PANEL REACTIVE RENDERING
    # =====================================================================
    # 1. Renders fixed banner
    render_header()

    # 2. Handles transitional states
    if st.session_state.ui_state == "loading":
        # Render loading skeletons and trigger pipeline
        with st.spinner("Executing analysis pipeline..."):
            execute_mock_analysis()
            st.rerun()

    elif st.session_state.ui_state == "empty":
        render_empty_state()

    elif st.session_state.ui_state == "error":
        # Renders the error component banner
        render_error_banner(
            message=st.session_state.error_message,
            title="Analysis Failure"
        )
        st.markdown(
            """
            <div style="text-align: center; margin-top: 2rem;">
                <p style="color: #64748B;">Please adjust the ticker input in the sidebar panel and try again.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    elif st.session_state.ui_state == "success":
        # Renders completed dashboard populated with aggregated data models
        res = st.session_state.analysis_results
        
        # Display warnings if there are non-critical errors caught by controller
        if res.get("errors"):
            for err in res["errors"]:
                render_warning_banner(message=err, title="Data Retrieval Notice")
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            
        profile: CompanyInfo = res["profile"]
        metrics: FinancialMetrics = res["metrics"]
        prices: List[HistoricalPrice] = res["prices"]
        sentiment: SentimentResult = res["sentiment"]
        risk: RiskAssessment = res["risk"]
        ai_summary: AISummary = res["ai_summary"]

        # Grids and Layout
        # Column A: Company Metadata + Chart + Ratios
        col_main, col_widgets = st.columns([3, 2])
        
        with col_main:
            # Section 1: Company Profile
            render_company_profile_card(profile)
            
            # Section 2: Historical Pricing Chart
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            draw_historical_chart(prices)
            st.markdown('</div>', unsafe_allow_html=True)

            # Section 3: Financial Ratio metrics
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="glass-card-title">🔢 Financial Overview & Ratios</div>', unsafe_allow_html=True)
            
            col_metric_1, col_metric_2, col_metric_3 = st.columns(3)
            with col_metric_1:
                render_metric_card(
                    label="Market Capitalization", 
                    value=format_large_number(metrics.market_cap),
                    help_text="The total dollar market value of a company's outstanding shares."
                )
                render_metric_card(
                    label="EPS (Trailing 12M)", 
                    value=f"${metrics.eps:.2f}" if metrics.eps is not None else "N/A",
                    help_text="Earnings Per Share: net income divided by common shares outstanding."
                )
            with col_metric_2:
                render_metric_card(
                    label="P/E Valuation Ratio", 
                    value=f"{metrics.pe_ratio:.2f}x" if metrics.pe_ratio is not None else "N/A",
                    help_text="Price-to-Earnings: share price divided by earnings per share."
                )
                render_metric_card(
                    label="Return on Equity (ROE)", 
                    value=format_percent(metrics.roe, is_multiplier=True),
                    help_text="A measure of financial performance calculated by dividing net income by shareholders' equity."
                )
            with col_metric_3:
                render_metric_card(
                    label="Debt-to-Equity Ratio", 
                    value=f"{metrics.debt_to_equity:.1f}%" if metrics.debt_to_equity is not None else "N/A",
                    help_text="Calculated by dividing a company's total liabilities by its shareholder equity."
                )
                render_metric_card(
                    label="Free Cash Flow", 
                    value=format_large_number(metrics.free_cash_flow),
                    help_text="Cash a company generates after cash outflows to support operations and maintain assets."
                )
            st.markdown('</div>', unsafe_allow_html=True)

        with col_widgets:
            # Section 4: News Sentiment Badge Card
            if sentiment:
                render_sentiment_card(sentiment)
                
            # Section 5: Risk Indicator
            if risk:
                render_risk_card(risk)
                
            # Section 6: AI Generated Summary advisory report
            if ai_summary:
                render_ai_advisory_card(ai_summary)

    # =====================================================================
    # FOOTER
    # =====================================================================
    st.markdown(
        f"""
        <div class="footer-text">
            {APP_TITLE} • Responsive Dashboard Architecture Framework • Verified at {datetime.now().strftime('%Y-%m-%d %H:%M')}
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
