"""
Session Cache helper utilities for managing Streamlit session state for financial overview and historical stock price data.
"""

import streamlit as st
from datetime import datetime
from typing import Optional, List
from models import CompanyOverview, HistoricalPrice, FinancialRatios

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

