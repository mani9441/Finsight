"""
Error reporting and warning presentation components for FinSight.
"""

import streamlit as st
from core.constants import THEME_COLORS

def render_error_banner(message: str, title: str = "Execution Error"):
    """
    Renders an inline error notification within a glassmorphic card container.
    """
    st.markdown(
        f"""
        <div class="glass-card" style="border-left: 4px solid {THEME_COLORS['DANGER']};">
            <div style="font-weight: 600; color: #F87171; font-size: 1.1rem; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                ❌ {title}
            </div>
            <div style="font-size: 0.9rem; color: #E2E8F0; line-height: 1.4;">
                {message}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_warning_banner(message: str, title: str = "Advisory Warning"):
    """
    Renders an inline warning card for partial data failures or configuration warnings.
    """
    st.markdown(
        f"""
        <div class="glass-card" style="border-left: 4px solid {THEME_COLORS['WARNING']}; padding: 1rem 1.25rem;">
            <div style="font-weight: 600; color: #FBBF24; font-size: 1rem; margin-bottom: 0.25rem; display: flex; align-items: center; gap: 0.5rem;">
                ⚠️ {title}
            </div>
            <div style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.3;">
                {message}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
