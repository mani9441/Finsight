from utils.session_cache import set_cached_sentiment
from utils.session_cache import set_cached_news
from utils.session_cache import set_cached_ratios
import streamlit as st
from services import RiskEvaluationService, RiskController
from components import render_company_risk_module, render_section_loader, render_error_banner
from utils.session_cache import (
    get_cached_risk, set_cached_risk, get_risk_loading_status, set_risk_loading_status,
    get_risk_error, set_risk_error, get_cached_ratios, get_cached_sentiment
)
from utils.error_handler import log_and_map_exception

st.set_page_config(page_title="Risk Assessment | FinSight", layout="wide")

if not st.session_state.get("current_company"):
    st.warning("⚠️ Please select a company from the main **Dashboard** first.")
else:
    profile = st.session_state.current_company
    st.title(f"⚡ Investment Risk Scorecard — {profile.ticker}")

    cached_risk = get_cached_risk()
    if get_risk_loading_status():
        render_section_loader("Calculating Risk Factors", height=200)
        try:
            ratios = get_cached_ratios()
            if ratios is None:
                from services import FinancialRatioService, RatioController
                ratios = RatioController(FinancialRatioService()).get_ratios(profile.ticker)
                set_cached_ratios(ratios)

            sentiment = get_cached_sentiment()
            if sentiment is None:
                from services import NewsService, NewsController
                articles, sentiment = NewsController(NewsService()).get_news_with_sentiment(profile.ticker)
                set_cached_news(articles)
                set_cached_sentiment(sentiment)

            risk = RiskController(RiskEvaluationService()).get_risk_assessment(profile.ticker, ratios, sentiment)
            set_cached_risk(risk)
        except Exception as e:
            set_risk_error(log_and_map_exception(e, "risk"))
        finally:
            set_risk_loading_status(False)
            st.rerun()
    elif get_risk_error():
        render_error_banner(get_risk_error())
    elif cached_risk:
        render_company_risk_module(cached_risk)
    else:
        set_risk_loading_status(True)
        st.rerun()