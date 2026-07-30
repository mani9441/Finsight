import streamlit as st
from services import FinancialRatioService, RatioController
from components import render_company_ratios_module, render_section_loader, render_error_banner
from utils.session_cache import (
    get_cached_ratios, set_cached_ratios,
    get_ratios_loading_status, set_ratios_loading_status, get_ratios_error, set_ratios_error
)
from utils.error_handler import log_and_map_exception

st.set_page_config(page_title="Financial Ratios | FinSight", layout="wide")

if not st.session_state.get("current_company"):
    st.warning("⚠️ Please select a company from the main **Dashboard** first.")
else:
    profile = st.session_state.current_company
    st.title(f"Valuation & Profitability Ratios — {profile.ticker}")

    cached_ratios = get_cached_ratios()
    if get_ratios_loading_status():
        render_section_loader("Analyzing Key Financial Metrics", height=240)
        try:
            ratios = RatioController(FinancialRatioService()).get_ratios(profile.ticker)
            set_cached_ratios(ratios)
        except Exception as e:
            set_ratios_error(log_and_map_exception(e, "ratios"))
        finally:
            set_ratios_loading_status(False)
            st.rerun()
    elif get_ratios_error():
        render_error_banner(get_ratios_error())
    elif cached_ratios:
        render_company_ratios_module(cached_ratios)
    else:
        set_ratios_loading_status(True)
        st.rerun()