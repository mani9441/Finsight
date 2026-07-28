"""
Session Cache helper utilities for managing Streamlit session state for financial overview and historical stock price data.
"""

import streamlit as st
from datetime import datetime
from typing import Optional, List
from models import CompanyOverview, HistoricalPrice, FinancialRatios, NewsArticle, SentimentResult, RiskAssessment, AISummary

OVERVIEW_DATA_KEY = "overview_data"
OVERVIEW_TIMESTAMP_KEY = "overview_timestamp"
OVERVIEW_LOADING_KEY = "overview_loading"
OVERVIEW_ERROR_KEY = "overview_error"

# Phase 7 Cache Keys
HISTORICAL_PRICES_KEY = "historical_prices"
SELECTED_TIME_RANGE_KEY = "selected_time_range"
HISTORICAL_TIMESTAMP_KEY = "historical_timestamp"
HISTORICAL_LOADING_KEY = "historical_loading"
HISTORICAL_ERROR_KEY = "historical_error"

# Phase 8 Cache Keys
RATIOS_DATA_KEY = "financial_ratios"
RATIOS_TIMESTAMP_KEY = "ratio_timestamp"
RATIOS_LOADING_KEY = "ratio_loading"
RATIOS_ERROR_KEY = "ratio_error"

# Phase 9 Cache Keys
NEWS_ARTICLES_KEY = "news_articles"
OVERALL_SENTIMENT_KEY = "overall_sentiment"
NEWS_TIMESTAMP_KEY = "news_timestamp"
NEWS_LOADING_KEY = "news_loading"
NEWS_ERROR_KEY = "news_error"

# Phase 10 Cache Keys
RISK_DATA_KEY = "risk_assessment"
RISK_TIMESTAMP_KEY = "risk_timestamp"
RISK_LOADING_KEY = "risk_loading"
RISK_ERROR_KEY = "risk_error"

# Phase 11 Cache Keys
SUMMARY_DATA_KEY = "ai_summary"
SUMMARY_TIMESTAMP_KEY = "summary_timestamp"
SUMMARY_LOADING_KEY = "summary_loading"
SUMMARY_ERROR_KEY = "summary_error"


def initialize_overview_session():
    """
    Initializes required session keys for the Financial Overview module.
    """
    if OVERVIEW_DATA_KEY not in st.session_state:
        st.session_state[OVERVIEW_DATA_KEY] = None
    if OVERVIEW_TIMESTAMP_KEY not in st.session_state:
        st.session_state[OVERVIEW_TIMESTAMP_KEY] = None
    if OVERVIEW_LOADING_KEY not in st.session_state:
        st.session_state[OVERVIEW_LOADING_KEY] = False
    if OVERVIEW_ERROR_KEY not in st.session_state:
        st.session_state[OVERVIEW_ERROR_KEY] = None


def get_cached_overview() -> Optional[CompanyOverview]:
    """
    Retrieves the cached CompanyOverview model from the session state.
    """
    return st.session_state.get(OVERVIEW_DATA_KEY)


def set_cached_overview(overview: Optional[CompanyOverview]):
    """
    Stores the CompanyOverview model and sets the retrieval timestamp.
    """
    st.session_state[OVERVIEW_DATA_KEY] = overview
    if overview is not None:
        st.session_state[OVERVIEW_TIMESTAMP_KEY] = datetime.now()
    else:
        st.session_state[OVERVIEW_TIMESTAMP_KEY] = None


def get_overview_timestamp() -> Optional[datetime]:
    """
    Retrieves the timestamp when the overview data was loaded.
    """
    return st.session_state.get(OVERVIEW_TIMESTAMP_KEY)


def get_overview_loading_status() -> bool:
    """
    Checks if the overview module is currently in a loading state.
    """
    return st.session_state.get(OVERVIEW_LOADING_KEY, False)


def set_overview_loading_status(status: bool):
    """
    Sets the loading status for the overview module.
    """
    st.session_state[OVERVIEW_LOADING_KEY] = status


def get_overview_error() -> Optional[str]:
    """
    Retrieves any error message encountered during overview data fetching.
    """
    return st.session_state.get(OVERVIEW_ERROR_KEY)


def set_overview_error(error: Optional[str]):
    """
    Sets the error state message for the overview module.
    """
    st.session_state[OVERVIEW_ERROR_KEY] = error


def clear_overview_cache():
    """
    Resets the overview data, timestamp, and errors in the session state cache.
    """
    st.session_state[OVERVIEW_DATA_KEY] = None
    st.session_state[OVERVIEW_TIMESTAMP_KEY] = None
    st.session_state[OVERVIEW_LOADING_KEY] = False
    st.session_state[OVERVIEW_ERROR_KEY] = None


# =====================================================================
# PHASE 7 HISTORICAL PRICES SESSION MANAGEMENT
# =====================================================================

def initialize_historical_session():
    """
    Initializes required session keys for the Historical Stock Price module.
    """
    if HISTORICAL_PRICES_KEY not in st.session_state:
        st.session_state[HISTORICAL_PRICES_KEY] = None
    if SELECTED_TIME_RANGE_KEY not in st.session_state:
        # Defaults automatically to "1 Year" historical view as requested
        st.session_state[SELECTED_TIME_RANGE_KEY] = "1 Year"
    if HISTORICAL_TIMESTAMP_KEY not in st.session_state:
        st.session_state[HISTORICAL_TIMESTAMP_KEY] = None
    if HISTORICAL_LOADING_KEY not in st.session_state:
        st.session_state[HISTORICAL_LOADING_KEY] = False
    if HISTORICAL_ERROR_KEY not in st.session_state:
        st.session_state[HISTORICAL_ERROR_KEY] = None


def get_cached_historical_prices() -> Optional[List[HistoricalPrice]]:
    """
    Retrieves cached HistoricalPrice objects list.
    """
    return st.session_state.get(HISTORICAL_PRICES_KEY)


def set_cached_historical_prices(prices: Optional[List[HistoricalPrice]]):
    """
    Stores historical price records and updates retrieval timestamp.
    """
    st.session_state[HISTORICAL_PRICES_KEY] = prices
    if prices is not None:
        st.session_state[HISTORICAL_TIMESTAMP_KEY] = datetime.now()
    else:
        st.session_state[HISTORICAL_TIMESTAMP_KEY] = None


def get_selected_time_range() -> str:
    """
    Retrieves currently active human-readable time range.
    """
    return st.session_state.get(SELECTED_TIME_RANGE_KEY, "1 Year")


def set_selected_time_range(time_range: str):
    """
    Saves currently selected active human-readable time range.
    """
    st.session_state[SELECTED_TIME_RANGE_KEY] = time_range


def get_historical_loading_status() -> bool:
    """
    Checks if the historical price chart module is loading data.
    """
    return st.session_state.get(HISTORICAL_LOADING_KEY, False)


def set_historical_loading_status(status: bool):
    """
    Sets loading status for historical price chart module.
    """
    st.session_state[HISTORICAL_LOADING_KEY] = status


def get_historical_error() -> Optional[str]:
    """
    Retrieves errors encountered during historical stock price retrieval.
    """
    return st.session_state.get(HISTORICAL_ERROR_KEY)


def set_historical_error(error: Optional[str]):
    """
    Stores error state message for historical price chart module.
    """
    st.session_state[HISTORICAL_ERROR_KEY] = error


def clear_historical_cache():
    """
    Clears cached price datasets, status indicator fields, and timestamps.
    """
    st.session_state[HISTORICAL_PRICES_KEY] = None
    # Preserve SELECTED_TIME_RANGE_KEY across company searches so user's choice persists
    st.session_state[HISTORICAL_TIMESTAMP_KEY] = None
    st.session_state[HISTORICAL_LOADING_KEY] = False
    st.session_state[HISTORICAL_ERROR_KEY] = None


# =====================================================================
# PHASE 8 FINANCIAL RATIOS SESSION MANAGEMENT
# =====================================================================

def initialize_ratios_session():
    """
    Initializes required session keys for the Financial Ratios module.
    """
    if RATIOS_DATA_KEY not in st.session_state:
        st.session_state[RATIOS_DATA_KEY] = None
    if RATIOS_TIMESTAMP_KEY not in st.session_state:
        st.session_state[RATIOS_TIMESTAMP_KEY] = None
    if RATIOS_LOADING_KEY not in st.session_state:
        st.session_state[RATIOS_LOADING_KEY] = False
    if RATIOS_ERROR_KEY not in st.session_state:
        st.session_state[RATIOS_ERROR_KEY] = None


def get_cached_ratios() -> Optional[FinancialRatios]:
    """
    Retrieves the cached FinancialRatios model from the session state.
    """
    return st.session_state.get(RATIOS_DATA_KEY)


def set_cached_ratios(ratios: Optional[FinancialRatios]):
    """
    Stores the FinancialRatios model and updates retrieval timestamp.
    """
    st.session_state[RATIOS_DATA_KEY] = ratios
    if ratios is not None:
        st.session_state[RATIOS_TIMESTAMP_KEY] = datetime.now()
    else:
        st.session_state[RATIOS_TIMESTAMP_KEY] = None


def get_ratios_timestamp() -> Optional[datetime]:
    """
    Retrieves the timestamp when the financial ratios data was loaded.
    """
    return st.session_state.get(RATIOS_TIMESTAMP_KEY)


def get_ratios_loading_status() -> bool:
    """
    Checks if the financial ratios module is currently loading data.
    """
    return st.session_state.get(RATIOS_LOADING_KEY, False)


def set_ratios_loading_status(status: bool):
    """
    Sets loading status for the financial ratios module.
    """
    st.session_state[RATIOS_LOADING_KEY] = status


def get_ratios_error() -> Optional[str]:
    """
    Retrieves errors encountered during financial ratios retrieval.
    """
    return st.session_state.get(RATIOS_ERROR_KEY)


def set_ratios_error(error: Optional[str]):
    """
    Stores error state message for the financial ratios module.
    """
    st.session_state[RATIOS_ERROR_KEY] = error


def clear_ratios_cache():
    """
    Clears cached financial ratios datasets, status indicator fields, and timestamps.
    """
    st.session_state[RATIOS_DATA_KEY] = None
    st.session_state[RATIOS_TIMESTAMP_KEY] = None
    st.session_state[RATIOS_LOADING_KEY] = False
    st.session_state[RATIOS_ERROR_KEY] = None


# =====================================================================
# PHASE 9 NEWS RETRIEVAL & SENTIMENT ANALYSIS SESSION MANAGEMENT
# =====================================================================

def initialize_news_session():
    """
    Initializes required session keys for the News Sentiment module.
    """
    if NEWS_ARTICLES_KEY not in st.session_state:
        st.session_state[NEWS_ARTICLES_KEY] = None
    if OVERALL_SENTIMENT_KEY not in st.session_state:
        st.session_state[OVERALL_SENTIMENT_KEY] = None
    if NEWS_TIMESTAMP_KEY not in st.session_state:
        st.session_state[NEWS_TIMESTAMP_KEY] = None
    if NEWS_LOADING_KEY not in st.session_state:
        st.session_state[NEWS_LOADING_KEY] = False
    if NEWS_ERROR_KEY not in st.session_state:
        st.session_state[NEWS_ERROR_KEY] = None


def get_cached_news() -> Optional[List[NewsArticle]]:
    """
    Retrieves the cached NewsArticle list from the session state.
    """
    return st.session_state.get(NEWS_ARTICLES_KEY)


def set_cached_news(articles: Optional[List[NewsArticle]]):
    """
    Stores the NewsArticle list and updates retrieval timestamp.
    """
    st.session_state[NEWS_ARTICLES_KEY] = articles
    if articles is not None:
        st.session_state[NEWS_TIMESTAMP_KEY] = datetime.now()
    else:
        st.session_state[NEWS_TIMESTAMP_KEY] = None


def get_cached_sentiment() -> Optional[SentimentResult]:
    """
    Retrieves the cached SentimentResult summary model from the session state.
    """
    return st.session_state.get(OVERALL_SENTIMENT_KEY)


def set_cached_sentiment(sentiment: Optional[SentimentResult]):
    """
    Stores the SentimentResult summary model.
    """
    st.session_state[OVERALL_SENTIMENT_KEY] = sentiment


def get_news_timestamp() -> Optional[datetime]:
    """
    Retrieves the timestamp when the news articles were loaded.
    """
    return st.session_state.get(NEWS_TIMESTAMP_KEY)


def get_news_loading_status() -> bool:
    """
    Checks if the news sentiment module is currently loading data.
    """
    return st.session_state.get(NEWS_LOADING_KEY, False)


def set_news_loading_status(status: bool):
    """
    Sets loading status for the news sentiment module.
    """
    st.session_state[NEWS_LOADING_KEY] = status


def get_news_error() -> Optional[str]:
    """
    Retrieves errors encountered during news retrieval and sentiment analysis.
    """
    return st.session_state.get(NEWS_ERROR_KEY)


def set_news_error(error: Optional[str]):
    """
    Stores error state message for the news sentiment module.
    """
    st.session_state[NEWS_ERROR_KEY] = error


def clear_news_cache():
    """
    Clears cached news articles, sentiment analytics, and timestamps.
    """
    st.session_state[NEWS_ARTICLES_KEY] = None
    st.session_state[OVERALL_SENTIMENT_KEY] = None
    st.session_state[NEWS_TIMESTAMP_KEY] = None
    st.session_state[NEWS_LOADING_KEY] = False
    st.session_state[NEWS_ERROR_KEY] = None


# =====================================================================
# PHASE 10 RISK INDICATOR SESSION MANAGEMENT
# =====================================================================

def initialize_risk_session():
    """
    Initializes required session keys for the Risk Indicator module.
    """
    if RISK_DATA_KEY not in st.session_state:
        st.session_state[RISK_DATA_KEY] = None
    if RISK_TIMESTAMP_KEY not in st.session_state:
        st.session_state[RISK_TIMESTAMP_KEY] = None
    if RISK_LOADING_KEY not in st.session_state:
        st.session_state[RISK_LOADING_KEY] = False
    if RISK_ERROR_KEY not in st.session_state:
        st.session_state[RISK_ERROR_KEY] = None


def get_cached_risk() -> Optional[RiskAssessment]:
    """
    Retrieves the cached RiskAssessment model from the session state.
    """
    return st.session_state.get(RISK_DATA_KEY)


def set_cached_risk(assessment: Optional[RiskAssessment]):
    """
    Stores the RiskAssessment model and updates retrieval timestamp.
    """
    st.session_state[RISK_DATA_KEY] = assessment
    if assessment is not None:
        st.session_state[RISK_TIMESTAMP_KEY] = datetime.now()
    else:
        st.session_state[RISK_TIMESTAMP_KEY] = None


def get_risk_timestamp() -> Optional[datetime]:
    """
    Retrieves the timestamp when the risk assessment was computed.
    """
    return st.session_state.get(RISK_TIMESTAMP_KEY)


def get_risk_loading_status() -> bool:
    """
    Checks if the risk indicator module is currently evaluating data.
    """
    return st.session_state.get(RISK_LOADING_KEY, False)


def set_risk_loading_status(status: bool):
    """
    Sets loading status for the risk indicator module.
    """
    st.session_state[RISK_LOADING_KEY] = status


def get_risk_error() -> Optional[str]:
    """
    Retrieves errors encountered during risk evaluation.
    """
    return st.session_state.get(RISK_ERROR_KEY)


def set_risk_error(error: Optional[str]):
    """
    Stores error state message for the risk indicator module.
    """
    st.session_state[RISK_ERROR_KEY] = error


def clear_risk_cache():
    """
    Clears cached risk models, status indicators, and timestamps.
    """
    st.session_state[RISK_DATA_KEY] = None
    st.session_state[RISK_TIMESTAMP_KEY] = None
    st.session_state[RISK_LOADING_KEY] = False
    st.session_state[RISK_ERROR_KEY] = None


# =====================================================================
# PHASE 11 AI SUMMARY MODULE SESSION MANAGEMENT
# =====================================================================

def initialize_summary_session():
    """
    Initializes required session keys for the AI Summary module.
    """
    if SUMMARY_DATA_KEY not in st.session_state:
        st.session_state[SUMMARY_DATA_KEY] = None
    if SUMMARY_TIMESTAMP_KEY not in st.session_state:
        st.session_state[SUMMARY_TIMESTAMP_KEY] = None
    if SUMMARY_LOADING_KEY not in st.session_state:
        st.session_state[SUMMARY_LOADING_KEY] = False
    if SUMMARY_ERROR_KEY not in st.session_state:
        st.session_state[SUMMARY_ERROR_KEY] = None


def get_cached_summary() -> Optional[AISummary]:
    """
    Retrieves the cached AISummary model from the session state.
    """
    return st.session_state.get(SUMMARY_DATA_KEY)


def set_cached_summary(summary: Optional[AISummary]):
    """
    Stores the AISummary model and updates retrieval timestamp.
    """
    st.session_state[SUMMARY_DATA_KEY] = summary
    if summary is not None:
        st.session_state[SUMMARY_TIMESTAMP_KEY] = datetime.now()
    else:
        st.session_state[SUMMARY_TIMESTAMP_KEY] = None


def get_summary_timestamp() -> Optional[datetime]:
    """
    Retrieves the timestamp when the AI summary was generated.
    """
    return st.session_state.get(SUMMARY_TIMESTAMP_KEY)


def get_summary_loading_status() -> bool:
    """
    Checks if the AI summary module is currently generating data.
    """
    return st.session_state.get(SUMMARY_LOADING_KEY, False)


def set_summary_loading_status(status: bool):
    """
    Sets loading status for the AI summary module.
    """
    st.session_state[SUMMARY_LOADING_KEY] = status


def get_summary_error() -> Optional[str]:
    """
    Retrieves errors encountered during AI summary generation.
    """
    return st.session_state.get(SUMMARY_ERROR_KEY)


def set_summary_error(error: Optional[str]):
    """
    Stores error state message for the AI summary module.
    """
    st.session_state[SUMMARY_ERROR_KEY] = error


def clear_summary_cache():
    """
    Clears cached AI summary models, status indicators, and timestamps.
    """
    st.session_state[SUMMARY_DATA_KEY] = None
    st.session_state[SUMMARY_TIMESTAMP_KEY] = None
    st.session_state[SUMMARY_LOADING_KEY] = False
    st.session_state[SUMMARY_ERROR_KEY] = None


# =====================================================================
# PHASE 15 DASHBOARD VISIBILITY AND BULK CACHE RESET
# =====================================================================

DASHBOARD_VISIBLE_KEY = "dashboard_visible"

def initialize_dashboard_visibility_session():
    """
    Initializes dashboard visibility state variable.
    """
    if DASHBOARD_VISIBLE_KEY not in st.session_state:
        st.session_state[DASHBOARD_VISIBLE_KEY] = False


def get_dashboard_visibility() -> bool:
    """
    Checks if the dashboard is currently set to be visible.
    """
    return st.session_state.get(DASHBOARD_VISIBLE_KEY, False)


def set_dashboard_visibility(visible: bool):
    """
    Sets the dashboard visibility state.
    """
    st.session_state[DASHBOARD_VISIBLE_KEY] = visible


def clear_all_caches():
    """
    Clears all company-specific session data caches across all modules.
    """
    clear_overview_cache()
    clear_historical_cache()
    clear_ratios_cache()
    clear_news_cache()
    clear_risk_cache()
    clear_summary_cache()

