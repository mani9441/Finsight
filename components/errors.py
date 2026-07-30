"""
Error & Warning Banner Components (Rich White Theme).
"""

import streamlit as st

def render_error_banner(message: str, title: str = "Execution Error"):
    st.markdown(
        f"""
        <div class="glass-card" style="border-left: 4px solid #E11D48; background-color: #FFF1F2;">
            <div style="font-weight: 700; color: #9F1239; font-size: 1rem; margin-bottom: 0.25rem;">
                ❌ {title}
            </div>
            <div style="font-size: 0.9rem; color: #881337; line-height: 1.4;">
                {message}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_warning_banner(message: str, title: str = "Advisory Warning"):
    st.markdown(
        f"""
        <div class="glass-card" style="border-left: 4px solid #D97706; background-color: #FEF3C7;">
            <div style="font-weight: 700; color: #92400E; font-size: 1rem; margin-bottom: 0.25rem;">
                ⚠️ {title}
            </div>
            <div style="font-size: 0.85rem; color: #78350F; line-height: 1.3;">
                {message}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )