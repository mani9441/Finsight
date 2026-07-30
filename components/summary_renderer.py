"""
UI component for rendering the AI-generated Company Summary (Rich White Theme).
"""

import streamlit as st
from models import AISummary
from core import get_logger

logger = get_logger("summary_renderer")

def render_company_summary_module(summary: AISummary):
    logger.debug(f"Rendering AI Company Summary for ticker: {summary.ticker}")

    st.markdown("### AI Executive Briefing")

    # Executive Summary Card
    st.markdown(
        f"""
        <div class="glass-card" style="margin-bottom: 1.5rem; padding: 1.5rem;">
            <h4 style="color: #2563EB; margin: 0 0 0.75rem 0; font-size: 1.1rem; font-weight: 700;">Executive Analysis</h4>
            <p style="color: #0F172A; font-size: 1rem; line-height: 1.6; margin: 0;">
                {summary.executive_summary}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)
    
    with col1:
        strengths_list = "".join([f'<li style="margin-bottom: 0.5rem; color: #334155;">{s}</li>' for s in summary.strengths])
        st.markdown(
            f"""
            <div class="glass-card" style="margin-bottom: 1.5rem; padding: 1.25rem; border-left: 4px solid #059669; min-height: 200px;">
                <h4 style="color: #059669; margin: 0 0 0.75rem 0; font-size: 1rem; font-weight: 700; text-transform: uppercase;">
                    Key Strengths & Opportunities
                </h4>
                <ul style="margin: 0; padding-left: 1.25rem;">
                    {strengths_list if summary.strengths else '<li style="color: #94A3B8;">No major strengths flagged.</li>'}
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        weaknesses_list = "".join([f'<li style="margin-bottom: 0.5rem; color: #334155;">{w}</li>' for w in summary.weaknesses])
        st.markdown(
            f"""
            <div class="glass-card" style="margin-bottom: 1.5rem; padding: 1.25rem; border-left: 4px solid #E11D48; min-height: 200px;">
                <h4 style="color: #E11D48; margin: 0 0 0.75rem 0; font-size: 1rem; font-weight: 700; text-transform: uppercase;">
                    Potential Concerns & Risks
                </h4>
                <ul style="margin: 0; padding-left: 1.25rem;">
                    {weaknesses_list if summary.weaknesses else '<li style="color: #94A3B8;">No major risks flagged.</li>'}
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Investment Thesis
    st.markdown(
        f"""
        <div class="glass-card" style="margin-bottom: 1.5rem; padding: 1.25rem; border-left: 4px solid #2563EB; background-color: #EFF6FF;">
            <h4 style="color: #1E40AF; margin: 0 0 0.5rem 0; font-size: 0.85rem; font-weight: 700; text-transform: uppercase;">
                Investment Thesis Summary
            </h4>
            <p style="color: #1E293B; font-size: 0.95rem; font-style: italic; margin: 0; line-height: 1.5;">
                "{summary.investment_thesis}"
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Disclaimer Footer
    generated_str = summary.generated_at.strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(
        f"""
        <div class="glass-card" style="padding: 1.25rem; background: #F8FAFC; border: 1px solid #E2E8F0;">
            <p style="color: #64748B; font-size: 0.8rem; line-height: 1.5; margin: 0 0 0.75rem 0;">
                <strong>⚠️ Disclaimer:</strong> Generated AI insights are for informational purposes only and do not constitute financial advice.
            </p>
            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #E2E8F0; padding-top: 0.5rem; color: #94A3B8; font-size: 0.75rem;">
                <div>Engine: <span style="color: #2563EB;">{summary.model_name}</span></div>
                <div>Timestamp: {generated_str}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )