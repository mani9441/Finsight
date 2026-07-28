"""
Loading state visualization components for FinSight.
"""

import streamlit as st

def render_skeleton_loader(height: int = 150):
    """
    Renders a CSS-based animated pulsing skeleton block to reserve space in the UI.
    """
    st.markdown(
        f"""
        <style>
        @keyframes pulse {{
            0% {{ background-color: rgba(30, 41, 59, 0.4); }}
            50% {{ background-color: rgba(30, 41, 59, 0.7); }}
            100% {{ background-color: rgba(30, 41, 59, 0.4); }}
        }}
        .skeleton-block {{
            height: {height}px;
            width: 100%;
            border-radius: 8px;
            animation: pulse 1.5s infinite ease-in-out;
            border: 1px solid rgba(255, 255, 255, 0.05);
            margin-bottom: 1rem;
        }}
        </style>
        <div class="skeleton-block"></div>
        """,
        unsafe_allow_html=True
    )


def render_section_loader(section_title: str, height: int = 150):
    """
    Renders a skeleton block prepended by a section title to maintain layout stability.
    """
    st.markdown(f"#### {section_title}")
    render_skeleton_loader(height)
