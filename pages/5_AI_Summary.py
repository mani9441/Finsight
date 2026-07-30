from utils.session_cache import set_cached_risk
from utils.session_cache import set_cached_sentiment
from utils.session_cache import set_cached_news
from utils.session_cache import set_cached_ratios
from utils.session_cache import set_cached_overview
import streamlit as st
from services import LlmService, SummaryController
from components import render_company_summary_module, render_section_loader, render_error_banner
from utils.session_cache import (
    get_cached_summary, set_cached_summary, get_summary_loading_status, set_summary_loading_status,
    get_summary_error, set_summary_error, get_cached_overview, get_cached_ratios,
    get_cached_sentiment, get_cached_risk
)
from utils.error_handler import log_and_map_exception

st.set_page_config(page_title="AI Summary | FinSight", layout="wide")

if not st.session_state.get("current_company"):
    st.warning("⚠️ Please select a company from the main **Dashboard** first.")
else:
    profile = st.session_state.current_company
    st.title(f"AI Advisory Briefing — {profile.ticker}")

    cached_summary = get_cached_summary()
    if get_summary_loading_status():
        render_section_loader("Generating AI Executive Briefing", height=240)
        try:
            overview = get_cached_overview()
            if overview is None:
                from services import FinancialOverviewService, OverviewController
                overview = OverviewController(FinancialOverviewService()).get_overview(profile.ticker)
                set_cached_overview(overview)

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

            risk = get_cached_risk()
            if risk is None:
                from services import RiskEvaluationService, RiskController
                risk = RiskController(RiskEvaluationService()).get_risk_assessment(profile.ticker, ratios, sentiment)
                set_cached_risk(risk)

            summary = SummaryController(LlmService()).get_summary(
                profile.ticker,
                overview,
                ratios,
                sentiment,
                risk,
            )
            set_cached_summary(summary)
        except Exception as e:
            set_summary_error(log_and_map_exception(e, "summary"))
        finally:
            set_summary_loading_status(False)
            st.rerun()
    elif get_summary_error():
        render_error_banner(get_summary_error())
    elif cached_summary:
        render_company_summary_module(cached_summary)
    else:
        set_summary_loading_status(True)
        st.rerun()