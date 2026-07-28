"""
FinSight Entry Point.
Implements Phase 5 — Company Search Module.
Accepts user input, validates it, resolves symbol or company name using Yahoo Finance,
and establishes the active company context. Renders only the Company Overview section.
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
from models import CompanyInfo
from services import FinanceService
from services.common.response_validator import ResponseValidator
from core.exceptions import InvalidInputError, DataRetrievalError

# UI components
from components.empty_state import render_empty_state
from components.errors import render_error_banner

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


def render_header():
    """
    Renders branding header at top of main dashboard panel.
    """
    st.markdown(
        f"""
        <div class="hero-section">
            <h1 class="hero-title">{APP_TITLE}</h1>
            <p class="hero-subtitle">{APP_TAGLINE} | Company Search Active</p>
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
        logger.info(f"UI state set to LOADING for query: '{query_clean}'")
        
    except InvalidInputError as e:
        st.session_state.ui_state = "error"
        st.session_state.error_message = str(e)
        st.session_state.current_company = None
        st.session_state.search_status = "error"
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
        logger.error(f"Data retrieval failed during resolution: {e}")
    except Exception as e:
        st.session_state.ui_state = "error"
        st.session_state.error_message = "An unexpected error occurred while contacting financial services. Please try again."
        st.session_state.current_company = None
        st.session_state.search_status = "error"
        logger.error(f"Unexpected error during resolution: {e}")


def render_company_overview(profile: CompanyInfo):
    """
    Renders corporate profile identity card (metadata, description).
    """
    website_link = f'<a href="{profile.website}" target="_blank" style="color: #3B82F6; text-decoration: none;">{profile.website}</a>' if profile.website else "N/A"
    
    st.markdown(
        f"""
        <div class="glass-card" style="margin-top: 1rem;">
            <div class="glass-card-title">🏢 Company Profile & Details</div>
            <h3 style="margin-top: 0px; color: #FFFFFF; font-weight: 700;">{profile.name} ({profile.ticker})</h3>
            <p style="font-size: 0.95rem; color: #E2E8F0; line-height: 1.6; margin-bottom: 1.5rem;">
                {profile.summary}
            </p>
            <div class="status-grid">
                <div class="status-item">
                    <div class="status-label">Sector</div>
                    <div class="status-value" style="font-size: 1rem;">{profile.sector}</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Industry</div>
                    <div class="status-value" style="font-size: 1rem;">{profile.industry}</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Corporate Website</div>
                    <div class="status-value" style="font-size: 1rem; color: #3B82F6;">{website_link}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def main():
    # Setup Streamlit page configuration
    st.set_page_config(
        page_title=f"{APP_TITLE} | Company Search",
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
            # Render ONLY the resolved Company Overview card
            render_company_overview(profile)
            
            st.markdown(
                """
                <div style="margin-top: 2rem; text-align: center; color: #64748B; font-size: 0.85rem; font-style: italic;">
                    💡 Financial ratios, charts, news sentiment and risk indicator panels are disabled during the Search Phase verification.
                </div>
                """,
                unsafe_allow_html=True
            )

    # =====================================================================
    # FOOTER
    # =====================================================================
    st.markdown(
        f"""
        <div class="footer-text">
            {APP_TITLE} • Company Search Gateway • Verified at {datetime.now().strftime('%H:%M:%S')}
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
