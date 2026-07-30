"""
UI components for rendering corporate investment Risk Indicators in White UI Theme.
Using native Streamlit containers and CSS styling for robust multi-version rendering.
Zero-emoji implementation with full data retention.
"""

import streamlit as st
from models import RiskAssessment
from core import get_logger

logger = get_logger("risk_cards")


def inject_risk_module_css():
    """Injects CSS once at module load time to keep DOM clean."""
    st.markdown(
        """
        <style>
            .risk-badge {
                display: inline-flex;
                align-items: center;
                font-size: 0.75rem;
                font-weight: 700;
                padding: 0.25rem 0.65rem;
                border-radius: 9999px;
                letter-spacing: 0.04em;
                text-transform: uppercase;
            }
            .risk-badge-low  { background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0; }
            .risk-badge-med  { background: #FFFBEB; color: #D97706; border: 1px solid #FDE68A; }
            .risk-badge-high { background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_risk_badge_html(level: str) -> tuple[str, str]:
    """Returns (badge_html_string, color_hex_code)."""
    lvl_upper = level.strip().upper()
    
    if "LOW" in lvl_upper:
        return '<span class="risk-badge risk-badge-low">LOW RISK</span>', "#059669"
    elif "HIGH" in lvl_upper or "CRITICAL" in lvl_upper:
        return f'<span class="risk-badge risk-badge-high">{lvl_upper} RISK</span>', "#DC2626"
    else:
        return '<span class="risk-badge risk-badge-med">MEDIUM RISK</span>', "#D97706"


def render_company_risk_module(assessment: RiskAssessment):
    """
    Renders corporate risk assessment using native Streamlit containers, metrics,
    and structured layout elements. Retains all input data and metrics.
    """
    logger.debug(f"Rendering Risk Assessment Module for: {assessment.ticker}")
    inject_risk_module_css()

    st.subheader(f"Investment Risk Indicator -- {assessment.ticker}")

    badge_html, color_code = get_risk_badge_html(assessment.risk_level)
    risk_score_val = getattr(assessment, "risk_score", 15.0)
    score_pct = max(0, min(100, int(risk_score_val)))

    # Main Card Container
    with st.container(border=True):
        col_classification, col_score = st.columns([0.7, 0.3])

        with col_classification:
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; gap: 0.6rem; margin-top: 0.25rem;">
                    <span style="font-size: 0.85rem; font-weight: 600; color: #475569; text-transform: uppercase;">
                        Classification:
                    </span>
                    {badge_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_score:
            st.metric(label="Risk Score", value=f"{risk_score_val:.1f} / 100")

        # Visual Risk Gauge Bar
        st.markdown(
            f"""
            <div style="width: 100%; height: 8px; background: #F1F5F9; border-radius: 4px; overflow: hidden; margin: 0.5rem 0 1rem 0;">
                <div style="width: {score_pct}%; height: 100%; background: {color_code}; border-radius: 4px;"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Full Assessment Explanation Data
        st.write(assessment.risk_explanation)

        st.caption(
            "Note: Educational rating model. Does not constitute official financial advisory or investment solicitation."
        )

    # Risk Factors Section
    st.markdown("### Risk Consideration Factors")

    # Dynamic Factor List Output
    if not assessment.risk_factors:
        st.success("No critical profitability or negative sentiment risk factors flagged.")
    else:
        with st.container(border=True):
            st.markdown("**Identified Risk Parameters**")
            for factor in assessment.risk_factors:
                st.markdown(f"- {factor}")