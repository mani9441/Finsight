"""
FinSight Executive Dashboard Component.
Recreates the exact Dashboard Preview (Concept) layout from Section 11 of the poster.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import streamlit as st
import plotly.graph_objects as go

from models import (
    CompanyInfo,
    CompanyOverview,
    HistoricalPrice,
    FinancialRatios,
    SentimentResult,
    RiskAssessment,
)
from utils import format_large_number


def render_executive_dashboard(
    profile: CompanyInfo,
    overview: Optional[CompanyOverview],
    prices: Optional[List[HistoricalPrice]],
    ratios: Optional[FinancialRatios],
    sentiment: Optional[SentimentResult],
    risk: Optional[RiskAssessment],
    pipeline_status: Dict[str, Any],
):
    """
    Renders the exact FinSight poster Section 11 layout with live data.
    """

    # ------------------------------------------------------------------
    # 1. Currency & Data Normalization
    # ------------------------------------------------------------------
    currency_symbol = "$"
    if overview and overview.currency and overview.currency != "Not Available":
        raw_curr = overview.currency.strip().upper()
        if raw_curr in ["GBP", "£"]:
            currency_symbol = "£"
        elif raw_curr in ["EUR", "€"]:
            currency_symbol = "€"
        elif raw_curr in ["USD", "$"]:
            currency_symbol = "$"
        else:
            currency_symbol = raw_curr

    # Header calculations
    latest_price_str = "N/A"
    price_change_str = ""
    is_positive_change = True

    if prices and len(prices) > 0:
        latest_price = prices[-1].close_val
        latest_price_str = f"{currency_symbol}{latest_price:,.2f}"

        if len(prices) > 1:
            prev_price = prices[-2].close_val
            change_val = latest_price - prev_price
            change_pct = (change_val / prev_price) * 100 if prev_price else 0.0
            is_positive_change = change_val >= 0
            sign = "+" if is_positive_change else ""
            price_change_str = f"{sign}{currency_symbol}{change_val:,.2f} ({sign}{change_pct:.2f}%)"

    market_cap_str = "N/A"
    if overview and overview.market_capitalization:
        formatted_cap = format_large_number(overview.market_capitalization)
        if formatted_cap != "N/A":
            market_cap_str = f"{currency_symbol}{formatted_cap}"

    pe_val = f"{ratios.pe_ratio:.2f}" if ratios and ratios.pe_ratio is not None else "N/A"
    roe_val = f"{ratios.roe * 100:.1f}%" if ratios and ratios.roe is not None else "N/A"
    risk_score_str = f"{risk.risk_score:.1f}/10" if risk and risk.risk_score is not None else "N/A"
    risk_level_label = risk.risk_level if risk and risk.risk_level else "Moderate"

    # ------------------------------------------------------------------
    # 2. Header Banner (Matches Poster Top Banner)
    # ------------------------------------------------------------------
    with st.container(border=True):
        h_col1, h_col2 = st.columns([3, 1], vertical_alignment="center")

        with h_col1:
            exchange_lbl = overview.exchange if overview and overview.exchange else "NASDAQ"
            st.markdown(
                f"<h3 style='margin: 0;'>{profile.name} ({profile.ticker}) "
                f"<span style='font-size: 0.9rem; color: #64748B; font-weight: normal; margin-left: 8px;'>{exchange_lbl}</span></h3>",
                unsafe_allow_html=True,
            )

            # Price + Change indicator
            if price_change_str:
                color = "#059669" if is_positive_change else "#DC2626"
                st.markdown(
                    f"<h2 style='margin: 0;'>{latest_price_str} "
                    f"<span style='font-size: 1.1rem; color: {color}; font-weight: 600; margin-left: 10px;'>{price_change_str}</span></h2>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(f"<h2 style='margin: 0;'>{latest_price_str}</h2>", unsafe_allow_html=True)

        with h_col2:
            if profile.website:
                st.link_button("Official Website ↗", profile.website, use_container_width=True)

    st.write("")

    # ------------------------------------------------------------------
    # 3. Main Dashboard Layout (Two Columns as in Concept Preview)
    # ------------------------------------------------------------------
    left_main, right_main = st.columns([3, 2], gap="medium")

    # ================= LEFT COLUMN =================
    with left_main:
        # A. Stock Price Interactive Plotly Line Chart
        with st.container(border=True):
            st.markdown("##### Stock Price (1Y)")

            if prices and len(prices) > 0:
                dates = [p.date for p in prices]
                closes = [p.close_val for p in prices]

                fig_price = go.Figure()
                fig_price.add_trace(
                    go.Scatter(
                        x=dates,
                        y=closes,
                        mode="lines",
                        name="Close Price",
                        line=dict(color="#2563EB", width=2),
                        fill="tozeroy",
                        fillcolor="rgba(37, 99, 235, 0.08)",
                    )
                )

                fig_price.update_layout(
                    height=260,
                    margin=dict(l=10, r=10, t=10, b=10),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickprefix=currency_symbol),
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                )
                st.plotly_chart(fig_price, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("Stock price data is not loaded.")

        # B. Key Metrics Bottom Bar (Market Cap, P/E, ROE, Risk Score)
        with st.container(border=True):
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.caption("Market Cap")
                st.markdown(f"**{market_cap_str}**")
            with m2:
                st.caption("P/E Ratio")
                st.markdown(f"**{pe_val}**")
            with m3:
                st.caption("ROE")
                st.markdown(f"**{roe_val}**")
            with m4:
                st.caption("Risk Score")
                if "LOW" in risk_level_label.upper():
                    st.success(f"🟢 {risk_level_label}", icon="🛡️")
                elif "HIGH" in risk_level_label.upper() or "CRITICAL" in risk_level_label.upper():
                    st.error(f"🔴 {risk_level_label}")
                else:
                    st.warning(f"🟡 {risk_level_label}")

    # ================= RIGHT COLUMN =================
    with right_main:
        # A. Sentiment Score Gauge Chart
        with st.container(border=True):
            st.markdown("##### Sentiment Score")

            # Temporary debug output to verify the value entering the dashboard
            if sentiment:
                st.caption(f"🔍 Pipeline Data: {sentiment.sentiment_label} | Avg Score: {sentiment.average_score:+.4f} | {sentiment.article_count} articles")
            else:
                st.caption("🔍 Pipeline Data: Sentiment object is None")

            sent_score = sentiment.average_score if sentiment else 0.0
            sent_label = sentiment.sentiment_label if sentiment else "Neutral"

            # Plotly Gauge Meter
            fig_gauge = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=sent_score,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": sent_label, "font": {"size": 14, "color": "#1E293B"}},
                    number={"valueformat": "+.2f"},
                    gauge={
                        "axis": {"range": [-1, 1], "tickwidth": 1, "tickcolor": "#64748B"},
                        "bar": {"color": "#2563EB"},
                        "bgcolor": "white",
                        "borderwidth": 1,
                        "bordercolor": "#E2E8F0",
                        "steps": [
                            {"range": [-1, -0.2], "color": "#FEE2E2"},
                            {"range": [-0.2, 0.2], "color": "#F1F5F9"},
                            {"range": [0.2, 1], "color": "#D1FAE5"},
                        ],
                    },
                )
            )

            fig_gauge.update_layout(
                height=170,
                margin=dict(l=15, r=15, t=25, b=10),
                paper_bgcolor="white",
            )
            st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

            # Additional key statistics under the gauge
            st.markdown("---")
            c_stat1, c_stat2, c_stat3 = st.columns(3)
            
            with c_stat1:
                st.caption("Sentiment Label")
                if sentiment:
                    lbl = sentiment.sentiment_label
                    if "POS" in lbl.upper():
                        st.markdown(f"<span style='color: #059669; font-weight: bold;'>{lbl}</span>", unsafe_allow_html=True)
                    elif "NEG" in lbl.upper():
                        st.markdown(f"<span style='color: #DC2626; font-weight: bold;'>{lbl}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='color: #64748B; font-weight: bold;'>{lbl}</span>", unsafe_allow_html=True)
                else:
                    st.markdown("**Neutral**")
                    
            with c_stat2:
                st.caption("Average Score")
                if sentiment:
                    st.markdown(f"**{sentiment.average_score:+.2f}**")
                else:
                    st.markdown("**0.00**")
                    
            with c_stat3:
                st.caption("Articles Analyzed")
                if sentiment:
                    st.markdown(f"**{sentiment.article_count}**")
                else:
                    st.markdown("**0**")

        # B. AI Company Summary
        with st.container(border=True):
            st.markdown("##### AI Company Summary")
            if overview and overview.business_summary:
                # Truncated or full summary preview
                summary_text = overview.business_summary
                if len(summary_text) > 320:
                    summary_text = summary_text[:320] + "..."
                st.caption(summary_text)
            else:
                st.caption("No AI summary available for this company.")

    st.write("")

    # ------------------------------------------------------------------
    # 4. Analytical Pipeline Status Logs
    # ------------------------------------------------------------------
    with st.expander("⚙️ Pipeline Logs & Last Refresh Status", expanded=False):
        stages = [
            ("Company Search & Identity", "search"),
            ("Financial Overview Service", "overview"),
            ("Historical Prices Service", "historical"),
            ("Financial Ratios Engine", "ratios"),
            ("News & Sentiment Engine", "news"),
            ("Risk Evaluation Engine", "risk"),
            ("AI Advisor Briefing", "summary"),
        ]

        for title, key in stages:
            stage_status = pipeline_status.get(key, {})
            status_name = stage_status.get("status", "not_run")
            timestamp = stage_status.get("timestamp")

            time_str = (
                timestamp.strftime("%b %d, %H:%M:%S")
                if isinstance(timestamp, datetime)
                else "N/A"
            )

            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.write(f"**{title}**")
            with c2:
                if status_name == "success":
                    st.caption("Completed")
                elif status_name == "failed":
                    st.caption("Failed")
                else:
                    st.caption("Pending")
            with c3:
                st.caption(time_str)