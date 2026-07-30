from utils.session_cache import set_cached_overview
import streamlit as st
from services import HistoricalPriceService, HistoricalPriceController
from components import render_time_range_selector, render_historical_price_chart, render_section_loader, render_error_banner
from utils.session_cache import (
    get_cached_historical_prices, set_cached_historical_prices,
    get_selected_time_range, get_historical_loading_status, set_historical_loading_status,
    get_historical_error, set_historical_error, get_cached_overview
)
from utils.error_handler import log_and_map_exception

st.set_page_config(page_title="Historical Price Chart | FinSight", layout="wide")

if not st.session_state.get("current_company"):
    st.warning("⚠️ Please select a company from the main **Dashboard** first.")
else:
    profile = st.session_state.current_company
    st.title(f"Historical Stock Trends — {profile.name} ({profile.ticker})")

    render_time_range_selector()
    cached_prices = get_cached_historical_prices()
    active_range = get_selected_time_range()
    
    if get_historical_loading_status():
        render_section_loader("Loading Price History", height=380)
        try:
            prices = HistoricalPriceController(HistoricalPriceService()).get_historical_prices(profile.ticker, active_range)
            set_cached_historical_prices(prices)
        except Exception as e:
            set_historical_error(log_and_map_exception(e, "historical"))
        finally:
            set_historical_loading_status(False)
            st.rerun()
    elif get_historical_error():
        render_error_banner(get_historical_error())
    elif cached_prices:
        overview = get_cached_overview()
        if overview is None:
            try:
                from services import FinancialOverviewService, OverviewController
                overview = OverviewController(FinancialOverviewService()).get_overview(profile.ticker)
                set_cached_overview(overview)
            except Exception as e:
                log_and_map_exception(e, "overview")
        currency = overview.currency if overview and overview.currency != "Not Available" else "£"
        render_historical_price_chart(cached_prices, profile.ticker, currency)
    else:
        set_historical_loading_status(True)
        st.rerun()