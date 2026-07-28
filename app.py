"""
FinSight Entry Point.
Implements:
- Phase 5 — Company Search Module
- Phase 6 — Financial Overview Module
- Phase 7 — Historical Stock Price Visualization Module
- Phase 8 — Financial Ratios Module
- Phase 9 — News Retrieval & Sentiment Analysis Module
- Phase 10 — Risk Indicator Module
- Phase 11 — AI Company Summary Module (Google Gemini 2.5 Flash)
"""

import streamlit as st
from datetime import datetime
from pathlib import Path

# Core configurations
from config import settings
from core import setup_logging, get_logger
from core.constants import (
    APP_TITLE,
    APP_TAGLINE
)
from models import CompanyInfo, CompanyOverview, HistoricalPrice, FinancialRatios, NewsArticle, SentimentResult, RiskAssessment, AISummary
from services import (
    FinanceService, 
    FinancialOverviewService, 
    OverviewController,
    HistoricalPriceService,
    HistoricalPriceController,
    FinancialRatioService,
    RatioController,
    NewsService,
    NewsController,
    RiskEvaluationService,
    RiskController,
    LlmService,
    SummaryController
)
from services.common.response_validator import ResponseValidator
from core.exceptions import InvalidInputError, DataRetrievalError

# UI components
from components import (
    render_empty_state,
    render_error_banner,
    render_section_loader,
    render_company_overview_module,
    render_time_range_selector,
    render_historical_price_chart,
    render_company_ratios_module,
    render_news_sentiment_module,
    render_company_risk_module,
    render_company_summary_module
)
from utils.session_cache import (
    initialize_overview_session,
    get_cached_overview,
    set_cached_overview,
    get_overview_loading_status,
    set_overview_loading_status,
    get_overview_error,
    set_overview_error,
    clear_overview_cache,
    
    # Phase 7 Cache Helpers
    initialize_historical_session,
    get_cached_historical_prices,
    set_cached_historical_prices,
    get_selected_time_range,
    set_selected_time_range,
    get_historical_loading_status,
    set_historical_loading_status,
    get_historical_error,
    set_historical_error,
    clear_historical_cache,
    
    # Phase 8 Cache Helpers
    initialize_ratios_session,
    get_cached_ratios,
    set_cached_ratios,
    get_ratios_loading_status,
    set_ratios_loading_status,
    get_ratios_error,
    set_ratios_error,
    clear_ratios_cache,
    
    # Phase 9 Cache Helpers
    initialize_news_session,
    get_cached_news,
    set_cached_news,
    get_cached_sentiment,
    set_cached_sentiment,
    get_news_loading_status,
    set_news_loading_status,
    get_news_error,
    set_news_error,
    clear_news_cache,
    
    # Phase 10 Cache Helpers
    initialize_risk_session,
    get_cached_risk,
    set_cached_risk,
    get_risk_loading_status,
    set_risk_loading_status,
    get_risk_error,
    set_risk_error,
    clear_risk_cache,
    
    # Phase 11 Cache Helpers
    initialize_summary_session,
    get_cached_summary,
    set_cached_summary,
    get_summary_loading_status,
    set_summary_loading_status,
    get_summary_error,
    set_summary_error,
    clear_summary_cache
)

# Initialize logging
setup_logging()
logger = get_logger("app_ui")

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
    Prepares session state variables for navigation and search context tracking.
    """
    if "ticker_input" not in st.session_state:
        st.session_state.ticker_input = ""
    if "ui_state" not in st.session_state:
        st.session_state.ui_state = "empty"  # empty, loading, success, error
    if "error_message" not in st.session_state:
        st.session_state.error_message = ""
        
    # Phase 5 Session Context tracking
    if "current_company" not in st.session_state:
        st.session_state.current_company = None
    if "search_status" not in st.session_state:
        st.session_state.search_status = "empty"
    if "search_timestamp" not in st.session_state:
        st.session_state.search_timestamp = None

    # Phase 6 Session Overview Cache tracking
    initialize_overview_session()
    
    # Phase 7 Session Historical Cache tracking
    initialize_historical_session()

    # Phase 8 Session Ratios Cache tracking
    initialize_ratios_session()

    # Phase 9 Session News Cache tracking
    initialize_news_session()

    # Phase 10 Session Risk Cache tracking
    initialize_risk_session()

    # Phase 11 Session Summary Cache tracking
    initialize_summary_session()


def render_header():
    """
    Renders branding header at top of main dashboard panel.
    """
    st.markdown(
        f"""
        <div class="hero-section">
            <h1 class="hero-title">{APP_TITLE}</h1>
            <p class="hero-subtitle">{APP_TAGLINE} | Financial Analytics Dashboard</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def trigger_search_pipeline(query: str):
    """
    Executes search input validation and triggers state transitions.
    """
    query_clean = query.strip()
    try:
        # Validate query format (prevent empty/whitespaces/special issues)
        if not query_clean:
            raise InvalidInputError("Please enter a company name or ticker.")
            
        if len(query_clean) > 50:
            raise InvalidInputError("Search query is too long. Please restrict query to 50 characters.")
            
        # Set loading state
        st.session_state.ui_state = "loading"
        st.session_state.error_message = ""
        
        # Clear all module session caches
        clear_overview_cache()
        clear_historical_cache()
        clear_ratios_cache()
        clear_news_cache()
        clear_risk_cache()
        clear_summary_cache()
        set_selected_time_range("1 Year")
        
        logger.info(f"UI state set to LOADING for query: '{query_clean}'")
        
    except InvalidInputError as e:
        st.session_state.ui_state = "error"
        st.session_state.error_message = str(e)
        st.session_state.current_company = None
        st.session_state.search_status = "error"
        clear_overview_cache()
        clear_historical_cache()
        clear_ratios_cache()
        clear_news_cache()
        clear_risk_cache()
        clear_summary_cache()
        logger.warning(f"Input validation failed for query '{query}': {e}")


def execute_company_resolution():
    """
    Queries FinanceService to resolve name/symbol to a CompanyInfo instance.
    Runs during the 'loading' phase.
    """
    query = st.session_state.ticker_input
    logger.info(f"Initiating resolution service lookup for: '{query}'")
    
    finance_service = FinanceService()
    
    try:
        profiles = finance_service.search_companies(query)
        
        if not profiles:
            st.session_state.ui_state = "error"
            st.session_state.error_message = f"Company could not be found for search query: '{query}'"
            st.session_state.current_company = None
            st.session_state.search_status = "error"
            clear_overview_cache()
            clear_historical_cache()
            clear_ratios_cache()
            clear_news_cache()
            clear_risk_cache()
            clear_summary_cache()
            logger.warning(f"Resolution failed to locate any public company profile for '{query}'")
        else:
            profile = profiles[0]
            st.session_state.current_company = profile
            st.session_state.search_status = "success"
            st.session_state.search_timestamp = datetime.now()
            st.session_state.ui_state = "success"
            logger.info(f"Resolution succeeded. Set active company context: {profile.name} ({profile.ticker})")
            
    except DataRetrievalError as e:
        st.session_state.ui_state = "error"
        st.session_state.error_message = str(e)
        st.session_state.current_company = None
        st.session_state.search_status = "error"
        clear_overview_cache()
        clear_historical_cache()
        clear_ratios_cache()
        clear_news_cache()
        clear_risk_cache()
        clear_summary_cache()
        logger.error(f"Data retrieval failed during resolution: {e}")
    except Exception as e:
        st.session_state.ui_state = "error"
        st.session_state.error_message = "An unexpected error occurred while contacting financial services. Please try again."
        st.session_state.current_company = None
        st.session_state.search_status = "error"
        clear_overview_cache()
        clear_historical_cache()
        clear_ratios_cache()
        clear_news_cache()
        clear_risk_cache()
        clear_summary_cache()
        logger.error(f"Unexpected error during resolution: {e}")


def main():
    # Setup Streamlit page configuration
    st.set_page_config(
        page_title=f"{APP_TITLE} | Financial Analysis Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Load custom theme stylesheet
    load_css()

    # Setup session variables
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
        "Enter Ticker or Company Name:", 
        value=st.session_state.ticker_input,
        max_chars=50, 
        placeholder="e.g. AAPL, Microsoft, GOOGL"
    )
    
    col_btn_search, col_btn_clear = st.sidebar.columns([1, 1])
    
    with col_btn_search:
        if st.button("Search", use_container_width=True):
            if ticker_query.strip():
                st.session_state.ticker_input = ticker_query
                trigger_search_pipeline(ticker_query)
                st.rerun()
            else:
                st.sidebar.warning("Please enter a search query.")
                
    with col_btn_clear:
        if st.button("Reset", use_container_width=True):
            st.session_state.ticker_input = ""
            st.session_state.ui_state = "empty"
            st.session_state.current_company = None
            st.session_state.search_status = "empty"
            st.session_state.search_timestamp = None
            st.session_state.error_message = ""
            clear_overview_cache()
            clear_historical_cache()
            clear_ratios_cache()
            clear_news_cache()
            clear_risk_cache()
            clear_summary_cache()
            set_selected_time_range("1 Year")
            logger.info("Dashboard state context reset.")
            st.rerun()

    # Ticker suggestion buttons
    st.sidebar.markdown("#### Suggested Lookups")
    cols_suggestions = st.sidebar.columns(3)
    suggestions = ["AAPL", "MSFT", "GOOGL"]
    for idx, sug in enumerate(suggestions):
        with cols_suggestions[idx]:
            if st.button(sug, key=f"sug_{sug}", use_container_width=True):
                st.session_state.ticker_input = sug
                trigger_search_pipeline(sug)
                st.rerun()

    st.sidebar.markdown("---")
    
    # Context Diagnostic Panel
    st.sidebar.markdown("### 💾 Active Context")
    active_company_name = st.session_state.current_company.name if st.session_state.current_company else "None"
    active_company_ticker = st.session_state.current_company.ticker if st.session_state.current_company else "None"
    st.sidebar.markdown(
        f"""
        <div class="glass-card" style="padding: 1rem; margin-bottom: 1.5rem;">
            <div class="status-label">Company Name</div>
            <div class="status-value" style="font-size: 0.9rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{active_company_name}</div>
            <div style="height: 10px;"></div>
            <div class="status-label">Symbol Context</div>
            <div class="status-value">{active_company_ticker}</div>
            <div style="height: 10px;"></div>
            <div class="status-label">Context Status</div>
            <div class="status-value"><span class="badge badge-info">{st.session_state.search_status}</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================================
    # MAIN PANEL REACTIVE RENDERING
    # =====================================================================
    # 1. Page branding header
    render_header()

    # 2. Page routing states
    if st.session_state.ui_state == "loading":
        with st.spinner("Resolving target company and loading profile..."):
            execute_company_resolution()
            st.rerun()

    elif st.session_state.ui_state == "empty":
        render_empty_state()

    elif st.session_state.ui_state == "error":
        render_error_banner(
            message=st.session_state.error_message,
            title="Search Resolution Failure"
        )

    elif st.session_state.ui_state == "success":
        profile = st.session_state.current_company
        if profile:
            # -------------------------------------------------------------
            # MODULE 1: Financial Overview Module (Phase 6)
            # -------------------------------------------------------------
            cached_overview = get_cached_overview()
            overview_err = get_overview_error()
            
            if get_overview_loading_status():
                render_section_loader("Financial Overview", height=220)
                
                try:
                    overview_service = FinancialOverviewService()
                    overview_controller = OverviewController(overview_service)
                    overview = overview_controller.get_overview(profile.ticker)
                    set_cached_overview(overview)
                    set_overview_error(None)
                except Exception as e:
                    logger.error(f"Overview retrieval failed for ticker '{profile.ticker}': {e}")
                    set_overview_error("Unable to retrieve company information. Please check your network connection or try again.")
                    set_cached_overview(None)
                finally:
                    set_overview_loading_status(False)
                    st.rerun()
                    
            elif overview_err:
                render_error_banner(
                    message=overview_err,
                    title="Overview Load Failure"
                )
                if st.button("🔄 Retry Loading Overview"):
                    set_overview_loading_status(True)
                    set_overview_error(None)
                    st.rerun()
                    
            elif cached_overview and cached_overview.ticker == profile.ticker:
                render_company_overview_module(cached_overview)
            else:
                set_overview_loading_status(True)
                set_overview_error(None)
                st.rerun()

            # -------------------------------------------------------------
            # MODULE 2: Historical Price Visualization Module (Phase 7)
            # -------------------------------------------------------------
            # Ensure overview loaded successfully before displaying prices chart
            if cached_overview and cached_overview.ticker == profile.ticker:
                st.markdown("---")
                
                # Visual time range buttons bar
                render_time_range_selector()
                
                cached_prices = get_cached_historical_prices()
                hist_err = get_historical_error()
                active_range = get_selected_time_range()
                
                if get_historical_loading_status():
                    render_section_loader("Historical Price Chart", height=380)
                    
                    try:
                        hist_service = HistoricalPriceService()
                        hist_controller = HistoricalPriceController(hist_service)
                        prices = hist_controller.get_historical_prices(profile.ticker, active_range)
                        set_cached_historical_prices(prices)
                        set_historical_error(None)
                    except Exception as e:
                        logger.error(f"Historical price retrieval failed for ticker '{profile.ticker}': {e}")
                        set_historical_error("Unable to retrieve historical stock prices.")
                        set_cached_historical_prices(None)
                    finally:
                        set_historical_loading_status(False)
                        st.rerun()
                        
                elif hist_err:
                    render_error_banner(
                        message=hist_err,
                        title="Historical Prices Load Failure"
                    )
                    if st.button("🔄 Retry Loading Historical Prices", key="retry_prices"):
                        set_historical_loading_status(True)
                        set_historical_error(None)
                        st.rerun()
                        
                elif cached_prices:
                    # Renders custom Plotly line/area trend visualizer
                    currency = cached_overview.currency if cached_overview.currency != "Not Available" else "USD"
                    render_historical_price_chart(cached_prices, profile.ticker, currency)
                else:
                    set_historical_loading_status(True)
                    set_historical_error(None)
                    st.rerun()

            # -------------------------------------------------------------
            # MODULE 3: Financial Ratios Module (Phase 8)
            # -------------------------------------------------------------
            # Ensure overview and prices loaded successfully before displaying ratios
            if cached_overview and cached_overview.ticker == profile.ticker and cached_prices:
                st.markdown("---")
                
                cached_ratios = get_cached_ratios()
                ratios_err = get_ratios_error()
                
                if get_ratios_loading_status():
                    render_section_loader("Financial Ratios", height=240)
                    
                    try:
                        ratio_service = FinancialRatioService()
                        ratio_controller = RatioController(ratio_service)
                        ratios = ratio_controller.get_ratios(profile.ticker)
                        set_cached_ratios(ratios)
                        set_ratios_error(None)
                    except Exception as e:
                        logger.error(f"Ratios retrieval failed for ticker '{profile.ticker}': {e}")
                        set_ratios_error("Unable to retrieve financial ratios.")
                        set_cached_ratios(None)
                    finally:
                        set_ratios_loading_status(False)
                        st.rerun()
                        
                elif ratios_err:
                    render_error_banner(
                        message=ratios_err,
                        title="Financial Ratios Load Failure"
                    )
                    if st.button("🔄 Retry Loading Financial Ratios", key="retry_ratios"):
                        set_ratios_loading_status(True)
                        set_ratios_error(None)
                        st.rerun()
                        
                elif cached_ratios:
                    # Renders card metrics list with educational descriptions
                    render_company_ratios_module(cached_ratios)
                else:
                    set_ratios_loading_status(True)
                    set_ratios_error(None)
                    st.rerun()

            # -------------------------------------------------------------
            # MODULE 4: News Retrieval & Sentiment Analysis Module (Phase 9)
            # -------------------------------------------------------------
            # Ensure ratios loaded successfully before displaying news sentiment
            if cached_overview and cached_overview.ticker == profile.ticker and cached_ratios:
                st.markdown("---")
                
                cached_news = get_cached_news()
                cached_sentiment = get_cached_sentiment()
                news_err = get_news_error()
                
                if get_news_loading_status():
                    render_section_loader("News & Sentiment Analysis", height=300)
                    
                    try:
                        news_service = NewsService()
                        news_controller = NewsController(news_service)
                        articles, sentiment = news_controller.get_news_with_sentiment(profile.ticker)
                        set_cached_news(articles)
                        set_cached_sentiment(sentiment)
                        set_news_error(None)
                    except Exception as e:
                        logger.error(f"News retrieval failed for ticker '{profile.ticker}': {e}")
                        set_news_error("Unable to retrieve recent news.")
                        set_cached_news(None)
                        set_cached_sentiment(None)
                    finally:
                        set_news_loading_status(False)
                        st.rerun()
                        
                elif news_err:
                    render_error_banner(
                        message=news_err,
                        title="News Load Failure"
                    )
                    if st.button("🔄 Retry Loading News", key="retry_news"):
                        set_news_loading_status(True)
                        set_news_error(None)
                        st.rerun()
                        
                elif cached_news is not None and cached_sentiment is not None:
                    # Renders aggregated sentiment card and chronological feed cards list
                    render_news_sentiment_module(cached_news, cached_sentiment)
                else:
                    set_news_loading_status(True)
                    set_news_error(None)
                    st.rerun()

            # -------------------------------------------------------------
            # MODULE 5: Risk Indicator Module (Phase 10)
            # -------------------------------------------------------------
            # Ensure news sentiment loaded successfully before assessing risk
            if cached_overview and cached_overview.ticker == profile.ticker and cached_news is not None and cached_sentiment is not None:
                st.markdown("---")
                
                cached_risk = get_cached_risk()
                risk_err = get_risk_error()
                
                if get_risk_loading_status():
                    render_section_loader("Investment Risk Assessment", height=200)
                    
                    try:
                        risk_service = RiskEvaluationService()
                        risk_controller = RiskController(risk_service)
                        risk_assessment = risk_controller.get_risk_assessment(profile.ticker, cached_ratios, cached_sentiment)
                        set_cached_risk(risk_assessment)
                        set_risk_error(None)
                    except Exception as e:
                        logger.error(f"Risk evaluation failed for ticker '{profile.ticker}': {e}")
                        set_risk_error(str(e) or "Unable to generate the risk indicator.")
                        set_cached_risk(None)
                    finally:
                        set_risk_loading_status(False)
                        st.rerun()
                        
                elif risk_err:
                    render_error_banner(
                        message=risk_err,
                        title="Risk Assessment Failure"
                    )
                    if st.button("🔄 Retry Generating Risk Indicator", key="retry_risk"):
                        set_risk_loading_status(True)
                        set_risk_error(None)
                        st.rerun()
                        
                elif cached_risk:
                    # Renders overall risk badge and supporting factor list
                    render_company_risk_module(cached_risk)
                else:
                    set_risk_loading_status(True)
                    set_risk_error(None)
                    st.rerun()

            # -------------------------------------------------------------
            # MODULE 6: AI Company Summary Module (Phase 11)
            # -------------------------------------------------------------
            # Ensure risk assessment loaded successfully before generating summary
            if cached_overview and cached_overview.ticker == profile.ticker and cached_risk:
                st.markdown("---")
                
                cached_summary = get_cached_summary()
                summary_err = get_summary_error()
                
                if get_summary_loading_status():
                    render_section_loader("AI Company Summary", height=240)
                    
                    try:
                        summary_service = LlmService()
                        summary_controller = SummaryController(summary_service)
                        ai_summary = summary_controller.get_summary(
                            profile.ticker,
                            cached_overview,
                            cached_ratios,
                            cached_sentiment,
                            cached_risk
                        )
                        set_cached_summary(ai_summary)
                        set_summary_error(None)
                    except Exception as e:
                        logger.error(f"AI summary generation failed for ticker '{profile.ticker}': {e}")
                        set_summary_error(str(e) or "Unable to generate the AI summary.")
                        set_cached_summary(None)
                    finally:
                        set_summary_loading_status(False)
                        st.rerun()
                        
                elif summary_err:
                    render_error_banner(
                        message=summary_err,
                        title="AI Summary Load Failure"
                    )
                    if st.button("🔄 Retry Generating AI Summary", key="retry_summary"):
                        set_summary_loading_status(True)
                        set_summary_error(None)
                        st.rerun()
                        
                elif cached_summary:
                    # Renders overall AI-generated summary and disclaimer
                    render_company_summary_module(cached_summary)
                else:
                    set_summary_loading_status(True)
                    set_summary_error(None)
                    st.rerun()

    # =====================================================================
    # FOOTER
    # =====================================================================
    st.markdown(
        f"""
        <div class="footer-text">
            {APP_TITLE} • AI Summary Module • Verified at {datetime.now().strftime('%H:%M:%S')}
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
