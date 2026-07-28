"""
UI components for rendering corporate investment Risk Indicators.
"""

import streamlit as st
from models import RiskAssessment
from core import get_logger

logger = get_logger("risk_cards")

def get_risk_badge_html(level: str) -> str:
    """
    Returns custom color-coded HTML badge based on risk level.
    """
    lvl_upper = level.strip().upper()
    if "LOW" in lvl_upper:
        color_class = "badge-success"  # green
    elif "HIGH" in lvl_upper or "CRITICAL" in lvl_upper:
        color_class = "badge-danger"   # red
    else:
        color_class = "badge-warning"  # orange/yellow
        
    return f'<span class="badge {color_class}">{level}</span>'


def render_company_risk_module(assessment: RiskAssessment):
    """
    Renders the risk classification, custom badges, explanations, and supporting factor lists.
    """
    logger.debug(f"Rendering Risk Assessment Module for: {assessment.ticker}")

    st.markdown("### ⚡ Investment Risk Indicator")

    badge_html = get_risk_badge_html(assessment.risk_level)

    # 1. Main indicator card
    st.markdown(
        f"""
        <div class="glass-card" style="margin-bottom: 1.5rem; padding: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                <h4 style="color: #64748B; margin: 0; font-size: 0.95rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
                    Assessment Classification
                </h4>
                {badge_html}
            </div>
            <p style="color: #F8FAFC; font-size: 1.05rem; line-height: 1.6; margin: 0 0 1rem 0;">
                {assessment.risk_explanation}
            </p>
            <div style="color: #64748B; font-size: 0.75rem; font-style: italic;">
                ⚠️ Educational rating only. This does not represent financial advice or price forecasting.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. Supporting factors list
    st.markdown("#### Supporting Risk Factors")
    
    if not assessment.risk_factors:
        st.markdown(
            """
            <div class="glass-card" style="padding: 1.25rem; border-left: 4px solid #10B981;">
                <p style="color: #10B981; margin: 0; font-weight: 600; font-size: 0.95rem;">
                    ✓ No critical profitability, valuation, or sentiment risk factors were flagged for this company.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Render lists of warning factors
        factors_html = "".join([f'<li style="margin-bottom: 0.5rem; color: #E2E8F0;">{f}</li>' for f in assessment.risk_factors])
        st.markdown(
            f"""
            <div class="glass-card" style="padding: 1.5rem; border-left: 4px solid #F59E0B;">
                <p style="color: #F59E0B; margin: 0 0 0.75rem 0; font-weight: 700; font-size: 0.95rem; text-transform: uppercase;">
                    Flagged Warning Considerations:
                </p>
                <ul style="margin: 0; padding-left: 1.25rem;">
                    {factors_html}
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    logger.info(f"Dashboard risk rendering completed for '{assessment.ticker}'")
