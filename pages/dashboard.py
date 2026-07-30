from datetime import datetime
from pathlib import Path
import streamlit as st

from components import (
    render_empty_state,
    render_error_banner,
    render_executive_dashboard,
)
from config import settings
from core import get_logger, setup_logging
from core.constants import APP_TITLE
from services import (
    FinanceService,
    FinancialOverviewService,
    FinancialRatioService,
    HistoricalPriceController,
    HistoricalPriceService,
    LlmService,
    NewsController,
    NewsService,
    OverviewController,
    RatioController,
    RiskController,
    RiskEvaluationService,
    SummaryController,
)
from utils.error_handler import log_and_map_exception
from utils.session_cache import (
    clear_all_caches,
    get_cached_historical_prices,
    get_cached_overview,
    get_cached_ratios,
    get_cached_risk,
    get_cached_sentiment,
    initialize_dashboard_visibility_session,
    initialize_historical_session,
    initialize_news_session,
    initialize_overview_session,
    initialize_ratios_session,
    initialize_risk_session,
    initialize_summary_session,
    set_cached_historical_prices,
    set_cached_news,
    set_cached_overview,
    set_cached_ratios,
    set_cached_risk,
    set_cached_sentiment,
    set_cached_summary,
    set_historical_error,
    set_news_error,
    set_overview_error,
    set_ratios_error,
    set_risk_error,
    set_selected_time_range,
    set_summary_error,
)

setup_logging()
logger = get_logger("dashboard_ui")


def load_css():
    """Load global stylesheet if available."""
    css_path = Path(settings.BASE_DIR) / "assets" / "styles" / "main.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def init_all_sessions():
    """Initializes all session state variables."""
    if "ticker_input" not in st.session_state:
        st.session_state.ticker_input = ""
    if "ui_state" not in st.session_state:
        st.session_state.ui_state = "empty"
    if "error_message" not in st.session_state:
        st.session_state.error_message = ""
    if "current_company" not in st.session_state:
        st.session_state.current_company = None
    if "search_status" not in st.session_state:
        st.session_state.search_status = "empty"
    if "pipeline_status" not in st.session_state:
        st.session_state.pipeline_status = {}

    initialize_overview_session()
    initialize_historical_session()
    initialize_ratios_session()
    initialize_news_session()
    initialize_risk_session()
    initialize_summary_session()
    initialize_dashboard_visibility_session()


def run_data_pipeline(ticker: str, progress_bar, status_container):
    """Executes analytical data pipeline sequentially with dynamic status updating."""
    ticker = ticker.strip().upper()

    st.session_state.pipeline_status = {
        "search": {
            "status": "success",
            "timestamp": datetime.now(),
            "error": None,
        },
        "overview": {"status": "not_run", "timestamp": None, "error": None},
        "historical": {"status": "not_run", "timestamp": None, "error": None},
        "ratios": {"status": "not_run", "timestamp": None, "error": None},
        "news": {"status": "not_run", "timestamp": None, "error": None},
        "risk": {"status": "not_run", "timestamp": None, "error": None},
        "summary": {"status": "not_run", "timestamp": None, "error": None},
    }

    steps = [
        ("overview", "Fetching Company Profile & Financial Overview...", 0.15),
        ("historical", "Retrieving Historical Stock Trends (1 Year)...", 0.30),
        ("ratios", "Analyzing Corporate Valuation & Financial Ratios...", 0.45),
        ("news", "Gathering Market News Coverage & Sentiment...", 0.60),
        ("risk", "Computing Investment Risk Factors Scorecard...", 0.75),
        ("summary", "Querying AI Advisor to Generate Briefing Report...", 0.90),
    ]

    for key, label, progress_val in steps:
        status_container.info(f"Current Stage: {label}")
        progress_bar.progress(progress_val)

        try:
            if key == "overview":
                overview = OverviewController(
                    FinancialOverviewService()
                ).get_overview(ticker)
                set_cached_overview(overview)
                set_overview_error(None)
            elif key == "historical":
                prices = HistoricalPriceController(
                    HistoricalPriceService()
                ).get_historical_prices(ticker, "1 Year")
                set_cached_historical_prices(prices)
                set_historical_error(None)
            elif key == "ratios":
                ratios = RatioController(FinancialRatioService()).get_ratios(
                    ticker
                )
                set_cached_ratios(ratios)
                set_ratios_error(None)
            elif key == "news":
                articles, sentiment = NewsController(
                    NewsService()
                ).get_news_with_sentiment(ticker)
                set_cached_news(articles)
                set_cached_sentiment(sentiment)
                set_news_error(None)
            elif key == "risk":
                ratios = get_cached_ratios()
                sentiment = get_cached_sentiment()
                risk = RiskController(
                    RiskEvaluationService()
                ).get_risk_assessment(ticker, ratios, sentiment)
                set_cached_risk(risk)
                set_risk_error(None)
            elif key == "summary":
                overview = get_cached_overview()
                ratios = get_cached_ratios()
                sentiment = get_cached_sentiment()
                risk = get_cached_risk()
                summary = SummaryController(LlmService()).get_summary(
                    ticker, overview, ratios, sentiment, risk
                )
                set_cached_summary(summary)
                set_summary_error(None)

            st.session_state.pipeline_status[key] = {
                "status": "success",
                "timestamp": datetime.now(),
                "error": None,
            }
        except Exception as e:
            logger.error(f"Pipeline Stage Failed: {key} for {ticker}: {e}")
            friendly_err = log_and_map_exception(e, key)
            st.session_state.pipeline_status[key] = {
                "status": "failed",
                "timestamp": datetime.now(),
                "error": friendly_err,
            }
            if key == "overview":
                set_overview_error(friendly_err)
                set_cached_overview(None)
            elif key == "historical":
                set_historical_error(friendly_err)
                set_cached_historical_prices(None)
            elif key == "ratios":
                set_ratios_error(friendly_err)
                set_cached_ratios(None)
            elif key == "news":
                set_news_error(friendly_err)
                set_cached_news(None)
                set_cached_sentiment(None)
            elif key == "risk":
                set_risk_error(friendly_err)
                set_cached_risk(None)
            elif key == "summary":
                set_summary_error(friendly_err)
                set_cached_summary(None)

    progress_bar.progress(1.0)
    status_container.success("Pipeline Analysis Completed Successfully.")


def execute_company_search(progress_bar, status_container):
    """Executes ticker search and triggers data pipeline on hit."""
    query = st.session_state.ticker_input
    finance_service = FinanceService()
    try:
        profiles = finance_service.search_companies(query)
        if not profiles:
            st.session_state.ui_state = "error"
            st.session_state.error_message = (
                f"No company found matching '{query}'."
            )
            st.session_state.pipeline_status = {
                "search": {
                    "status": "failed",
                    "timestamp": datetime.now(),
                    "error": f"No company found matching '{query}'.",
                }
            }
        else:
            profile = profiles[0]
            if (
                st.session_state.current_company is None
                or st.session_state.current_company.ticker != profile.ticker
            ):
                clear_all_caches()
                set_selected_time_range("1 Year")
            st.session_state.current_company = profile

            run_data_pipeline(
                profile.ticker, progress_bar, status_container
            )
            st.session_state.ui_state = "success"
    except Exception as e:
        friendly_err = log_and_map_exception(e, "search")
        st.session_state.ui_state = "error"
        st.session_state.error_message = friendly_err
        st.session_state.pipeline_status = {
            "search": {
                "status": "failed",
                "timestamp": datetime.now(),
                "error": friendly_err,
            }
        }


# View Logic execution for Dashboard
load_css()
init_all_sessions()

if st.session_state.ui_state == "loading":
    with st.container(border=True):
        st.markdown("### Executing Analytical Pipeline")
        progress_bar = st.progress(0.0)
        status_container = st.empty()
        execute_company_search(progress_bar, status_container)
        st.rerun()

elif st.session_state.ui_state == "empty":
    render_empty_state()

elif st.session_state.ui_state == "error":
    render_error_banner(st.session_state.error_message)

elif st.session_state.ui_state == "success":
    st.title(f"{APP_TITLE} Dashboard")
    st.caption(
        "Comprehensive corporate performance & financial intelligence platform"
    )
    st.divider()

    profile = st.session_state.current_company
    render_executive_dashboard(
        profile=profile,
        overview=get_cached_overview(),
        prices=get_cached_historical_prices(),
        ratios=get_cached_ratios(),
        sentiment=get_cached_sentiment(),
        risk=get_cached_risk(),
        pipeline_status=st.session_state.pipeline_status,
    )
    st.info(
        "Navigation Tip: Use the left sidebar menu to navigate through detailed sub-pages and charts."
    )