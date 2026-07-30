"""
UI component for rendering the interactive historical stock price chart using Plotly (White Theme).
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

logger = get_logger("historical_chart")

# Inline CSS for the time horizon bar & chart container
_CHART_UI_CSS = """
<style>
    .chart-container {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1rem 1.25rem 0.5rem 1.25rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    .chart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    .chart-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
    }
    .metric-pill-pos { background: #ECFDF5; color: #059669; }
    .metric-pill-neg { background: #FEF2F2; color: #DC2626; }
</style>
"""


def render_time_range_selector():
    """
    Renders an interactive segmented control bar for selecting time horizons.
    """
    ranges = TimeRangeManager.get_supported_ranges()
    active_range = get_selected_time_range()
    is_loading = get_historical_loading_status()

    # Use native st.segmented_control if supported, fallback to pill buttons
    if hasattr(st, "segmented_control"):
        selected = st.segmented_control(
            "Time Horizon",
            options=ranges,
            default=active_range,
            disabled=is_loading,
            label_visibility="collapsed",
            key="segmented_time_range"
        )
        if selected and selected != active_range:
            logger.info(f"User changed time range from '{active_range}' to '{selected}'")
            set_selected_time_range(selected)
            set_historical_loading_status(True)
            set_historical_error(None)
            st.rerun()
    else:
        # Fallback multi-column layout for earlier Streamlit versions
        st.write("<span style='font-size: 0.8rem; font-weight: 600; color: #64748B;'>TIME HORIZON</span>", unsafe_allow_html=True)
        cols = st.columns(len(ranges))
        for idx, r in enumerate(ranges):
            with cols[idx]:
                is_active = (r == active_range)
                btn_style = "primary" if is_active else "secondary"
                if st.button(
                    r, 
                    key=f"btn_range_{r.replace(' ', '_')}", 
                    type=btn_style,
                    use_container_width=True, 
                    disabled=is_loading
                ):
                    if not is_active:
                        logger.info(f"User changed time range from '{active_range}' to '{r}'")
                        set_selected_time_range(r)
                        set_historical_loading_status(True)
                        set_historical_error(None)
                        st.rerun()


def render_historical_price_chart(prices: List[HistoricalPrice], ticker: str, currency: str = "USD"):
    """
    Renders an interactive Plotly Area chart adapted for a clean Light White UI background.
    """
    logger.debug(f"Plotly Chart: Rendering for ticker '{ticker}'")
    st.markdown(_CHART_UI_CSS, unsafe_allow_html=True)
    
    if not prices:
        st.info("No historical price records available for the selected period.")
        return

    df = ChartDataProcessor.to_dataframe(prices)
    if df.empty:
        st.warning("Processed price dataset is empty.")
        return

    # Calculate period performance statistics
    start_close = df["Close"].iloc[0]
    end_close = df["Close"].iloc[-1]
    pct_change = ((end_close - start_close) / start_close) * 100
    change_val = end_close - start_close
    
    is_positive = pct_change >= 0
    theme_color = "#10B981" if is_positive else "#EF4444"  # Green vs Red dynamic color scheme
    bg_gradient = "rgba(16, 185, 129, 0.08)" if is_positive else "rgba(239, 68, 68, 0.08)"
    pill_class = "metric-pill-pos" if is_positive else "metric-pill-neg"
    sign = "+" if is_positive else ""

    # Header with ticker & performance badge
    st.markdown(
        f"""
        <div class="chart-header">
            <div>
                <span class="chart-title">{ticker} Price Performance</span>
                <span style="font-size: 1.1rem; font-weight: 700; color: #0F172A; margin-left: 0.5rem;">
                    {currency} {end_close:,.2f}
                </span>
            </div>
            <div class="{pill_class}">
                {sign}{change_val:,.2f} ({sign}{pct_change:.2f}%)
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    custom_data = df[["Open", "High", "Low", "Volume"]].values

    fig = go.Figure()
    
    # Area Trace with Dynamic Color Theme
    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["Close"],
        mode="lines",
        name="Close Price",
        line=dict(color=theme_color, width=2),
        fill="tozeroy",
        fillcolor=bg_gradient,
        customdata=custom_data,
        marker=dict(size=4, color=theme_color, opacity=0),
        hovertemplate=(
            "<b>Date:</b> %{x|%b %d, %Y}<br>"
            "<b>Close:</b> " + currency + " %{y:,.2f}<br>"
            "<b>Open:</b> " + currency + " %{customdata[0]:,.2f}<br>"
            "<b>High:</b> " + currency + " %{customdata[1]:,.2f}<br>"
            "<b>Low:</b> " + currency + " %{customdata[2]:,.2f}<br>"
            "<b>Volume:</b> %{customdata[3]:,}<extra></extra>"
        )
    ))

    # Clean White Layout
    fig.update_layout(
        xaxis=dict(
            showgrid=True, 
            gridcolor="#F1F5F9", 
            title=None,
            tickfont=dict(color="#64748B", size=10),
            linecolor="#E2E8F0",
            zeroline=False,
            showline=True
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor="#F1F5F9", 
            title=dict(text=f"Price ({currency})", font=dict(color="#64748B", size=10)),
            tickfont=dict(color="#64748B", size=10),
            linecolor="#E2E8F0",
            zeroline=False,
            showline=True
        ),
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        margin=dict(l=10, r=10, t=10, b=10),
        height=360,
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#0F172A",
            font_size=11,
            font_color="#F8FAFC",
            font_family="sans-serif"
        ),
        showlegend=False
    )

    st.plotly_chart(
        fig, 
        use_container_width=True, 
        config={
            "responsive": True, 
            "displayModeBar": "hover",
            "displaylogo": False,
            "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"]
        }
    )
    logger.info(f"Chart rendering completed for '{ticker}'")