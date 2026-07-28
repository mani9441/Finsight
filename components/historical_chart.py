"""
UI component for rendering the interactive historical stock price chart using Plotly.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import List, Optional
from models import HistoricalPrice
from services.finance.time_range_manager import TimeRangeManager
from services.finance.chart_data_processor import ChartDataProcessor
from utils.session_cache import (
    get_selected_time_range,
    set_selected_time_range,
    get_historical_loading_status,
    set_historical_loading_status,
    set_historical_error
)
from core import get_logger
from core.constants import THEME_COLORS

logger = get_logger("historical_chart")

def render_time_range_selector():
    """
    Renders a row of buttons representing supported historical periods.
    Disables interaction if the chart module is currently loading data.
    """
    ranges = TimeRangeManager.get_supported_ranges()
    active_range = get_selected_time_range()
    is_loading = get_historical_loading_status()

    st.write("Select Time Range:")
    cols = st.columns(len(ranges))
    
    for idx, r in enumerate(ranges):
        with cols[idx]:
            # Apply styling for selected button: Streamlit buttons cannot easily have custom selected colors
            # natively, but we can differentiate them or just let the default style render.
            # We prefix selected range with a dot or check icon, or rely on normal state buttons.
            btn_label = f"• {r}" if r == active_range else r
            
            if st.button(
                btn_label, 
                key=f"btn_range_{r.replace(' ', '_')}", 
                use_container_width=True, 
                disabled=is_loading
            ):
                logger.info(f"User changed time range from '{active_range}' to '{r}'")
                set_selected_time_range(r)
                set_historical_loading_status(True)
                set_historical_error(None)
                st.rerun()


def render_historical_price_chart(prices: List[HistoricalPrice], ticker: str, currency: str = "USD"):
    """
    Renders an interactive Plotly Area chart representing close price history.
    Includes custom hover details displaying Date, Open, High, Low, Close, and Volume.
    """
    logger.debug(f"Plotly Chart: Rendering for ticker '{ticker}'")
    
    if not prices:
        st.warning("No historical price records available to display.")
        return

    # 1. Convert to pandas DataFrame for Plotly consumption
    df = ChartDataProcessor.to_dataframe(prices)
    
    # 2. Extract values for hover card
    custom_data = df[["Open", "High", "Low", "Volume"]].values

    # 3. Create Scatter plot with area fill
    fig = go.Figure()
    
    # Render Close Price trend
    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["Close"],
        mode="lines",
        name="Close Price",
        line=dict(color=THEME_COLORS["SECONDARY"], width=2.5),
        fill="tozeroy",
        fillcolor="rgba(59, 130, 246, 0.05)",
        customdata=custom_data,
        hovertemplate=(
            "<b>Date:</b> %{x|%b %d, %Y}<br>"
            "<b>Close Price:</b> " + currency + " %{y:,.2f}<br>"
            "<b>Open:</b> " + currency + " %{customdata[0]:,.2f}<br>"
            "<b>High:</b> " + currency + " %{customdata[1]:,.2f}<br>"
            "<b>Low:</b> " + currency + " %{customdata[2]:,.2f}<br>"
            "<b>Volume:</b> %{customdata[3]:,}<extra></extra>"
        )
    ))

    # 4. Apply clean Glassmorphism Dashboard layouts
    fig.update_layout(
        xaxis=dict(
            showgrid=True, 
            gridcolor="rgba(255, 255, 255, 0.04)", 
            title=None,
            tickfont=dict(color="#94A3B8"),
            linecolor="rgba(255, 255, 255, 0.1)"
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor="rgba(255, 255, 255, 0.04)", 
            title=dict(text=f"Stock Price ({currency})", font=dict(color="#94A3B8", size=11)),
            tickfont=dict(color="#94A3B8"),
            linecolor="rgba(255, 255, 255, 0.1)"
        ),
        template="plotly_dark",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        margin=dict(l=20, r=20, t=20, b=20),
        height=380,
        hovermode="x unified",
        showlegend=False
    )

    # Render inside streamlit responsively
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True, "displayModeBar": True})
    
    logger.info(f"Chart rendering completed for '{ticker}'")
