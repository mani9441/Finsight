"""
UI component for rendering the AI-generated Company Summary and educational disclaimers.
"""

import streamlit as st
from models import AISummary
from core import get_logger

logger = get_logger("summary_renderer")

def render_company_summary_module(summary: AISummary):
    """
    Renders the AI Summary card block complete with disclaimer alerts and metadata footers.
    """
    logger.debug(f"Rendering AI Company Summary for ticker: {summary.ticker}")

    st.markdown("### 🤖 AI Company Summary")

    # 1. Executive Summary box
    st.markdown(
        f"""
        <div class="glass-card" style="margin-bottom: 1.5rem; padding: 1.5rem;">
            <h4 style="color: #60A5FA; margin: 0 0 0.75rem 0; font-size: 1.1rem; font-weight: 700;">Executive Analysis</h4>
            <p style="color: #F8FAFC; font-size: 1rem; line-height: 1.6; margin: 0;">
                {summary.executive_summary}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. Strengths and Weaknesses 2-column grid
    col1, col2 = st.columns(2)
    
    with col1:
        strengths_list = "".join([f'<li style="margin-bottom: 0.5rem; color: #CBD5E1;">{s}</li>' for s in summary.strengths])
        st.markdown(
            f"""
            <div class="glass-card" style="margin-bottom: 1.5rem; padding: 1.5rem; border-left: 4px solid #10B981; min-height: 220px;">
                <h4 style="color: #10B981; margin: 0 0 0.75rem 0; font-size: 1.05rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
                    Key Strengths & Opportunities
                </h4>
                <ul style="margin: 0; padding-left: 1.25rem;">
                    {strengths_list if summary.strengths else '<li style="color: #94A3B8;">No significant strengths flagged from provided metrics.</li>'}
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        weaknesses_list = "".join([f'<li style="margin-bottom: 0.5rem; color: #CBD5E1;">{w}</li>' for w in summary.weaknesses])
        st.markdown(
            f"""
            <div class="glass-card" style="margin-bottom: 1.5rem; padding: 1.5rem; border-left: 4px solid #EF4444; min-height: 220px;">
                <h4 style="color: #EF4444; margin: 0 0 0.75rem 0; font-size: 1.05rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
                    Potential Concerns & Risks
                </h4>
                <ul style="margin: 0; padding-left: 1.25rem;">
                    {weaknesses_list if summary.weaknesses else '<li style="color: #94A3B8;">No critical risk flags detected from provided metrics.</li>'}
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 3. Investment Thesis highlighted panel
    st.markdown(
        f"""
        <div class="glass-card" style="margin-bottom: 1.5rem; padding: 1.25rem; border-left: 4px solid #60A5FA; background: rgba(96, 165, 250, 0.05);">
            <h4 style="color: #60A5FA; margin: 0 0 0.5rem 0; font-size: 0.9rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
                Advisory Thesis Outline
            </h4>
            <p style="color: #E2E8F0; font-size: 0.975rem; font-style: italic; margin: 0; line-height: 1.5;">
                "{summary.investment_thesis}"
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 4. Disclaimer and metadata footer
    generated_str = summary.generated_at.strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(
        f"""
        <div class="glass-card" style="padding: 1.25rem; background: rgba(15, 23, 42, 0.6); border: 1px solid #1E293B;">
            <p style="color: #94A3B8; font-size: 0.8rem; line-height: 1.5; margin: 0 0 1rem 0;">
                <strong>⚠️ Disclaimer:</strong> The AI-generated advisory summary is provided for informational and educational purposes only. It does not constitute investment recommendations, financial advice, or buy/sell triggers. All financial calculations and parameters originate from internal FinSight data streams, and AI serves strictly as an explanation layer.
            </p>
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; border-top: 1px solid #1E293B; padding-top: 0.75rem; color: #64748B; font-size: 0.75rem; font-weight: 600;">
                <div>Generated Using: <span style="color: #60A5FA;">{summary.model_name}</span> (Status: <span style="color: #10B981;">{summary.status}</span>)</div>
                <div>Timestamp: <span>{generated_str}</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    logger.info(f"Dashboard summary rendering completed for '{summary.ticker}'")
