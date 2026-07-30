"""
Skeleton loading state visualizers with metallic shimmer effect (Rich White Theme).
"""

import streamlit as st

# --- SHIMMER ANIMATION & CARD STYLES ---
_SKELETON_CSS = """
<style>
    @keyframes metallic-shimmer {
        0% {
            background-position: -200px 0;
        }
        100% {
            background-position: calc(200px + 100%) 0;
        }
    }

    .skeleton-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
    }

    .skeleton-element {
        background: #F1F5F9;
        background-image: linear-gradient(
            90deg,
            #F1F5F9 0px,
            #E2E8F0 40px,
            #F1F5F9 80px
        );
        background-size: 200px 100%;
        background-repeat: no-repeat;
        border-radius: 6px;
        animation: metallic-shimmer 1.6s infinite linear;
    }

    /* Standard Placeholders */
    .sk-title { height: 18px; width: 35%; margin-bottom: 1rem; }
    .sk-badge { height: 22px; width: 75px; border-radius: 9999px; }
    .sk-text-line { height: 12px; width: 100%; margin-bottom: 0.5rem; }
    .sk-text-line-short { height: 12px; width: 65%; margin-bottom: 1rem; }
    
    /* Layout Grids */
    .sk-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 0.75rem;
        margin-top: 1rem;
    }
    .sk-cell {
        height: 55px;
        border-radius: 8px;
    }
    
    /* Chart Skeletons */
    .sk-chart-bars {
        display: flex;
        align-items: flex-end;
        gap: 0.5rem;
        height: 180px;
        padding-top: 1rem;
    }
    .sk-bar {
        flex: 1;
        border-radius: 4px 4px 0 0;
    }
</style>
"""


def _inject_css():
    st.markdown(_SKELETON_CSS, unsafe_allow_html=True)


def render_skeleton_loader(height: int = 150):
    """
    Renders a metallic shimmer skeleton card placeholder.
    (Preserves exact function signature for backward compatibility)
    """
    _inject_css()
    card_html = f"""
    <div class="skeleton-card" style="min-height: {height}px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div class="skeleton-element sk-title"></div>
            <div class="skeleton-element sk-badge"></div>
        </div>
        <div class="skeleton-element sk-text-line"></div>
        <div class="skeleton-element sk-text-line"></div>
        <div class="skeleton-element sk-text-line-short"></div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_section_loader(section_title: str, height: int = 150):
    """
    Renders a section title along with a shimmer skeleton loader.
    (Preserves exact function signature for backward compatibility)
    """
    st.markdown(f"#### {section_title}")
    render_skeleton_loader(height)


def render_metric_grid_skeleton():
    """
    Renders a dashboard metric grid skeleton.
    """
    _inject_css()
    grid_html = """
    <div class="skeleton-card">
        <div class="skeleton-element sk-title" style="width: 25%;"></div>
        <div class="sk-grid">
            <div class="skeleton-element sk-cell"></div>
            <div class="skeleton-element sk-cell"></div>
            <div class="skeleton-element sk-cell"></div>
            <div class="skeleton-element sk-cell"></div>
        </div>
    </div>
    """
    st.markdown(grid_html, unsafe_allow_html=True)


def render_chart_skeleton():
    """
    Renders a historical chart skeleton state.
    """
    _inject_css()
    chart_html = """
    <div class="skeleton-card">
        <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
            <div class="skeleton-element sk-title" style="width: 30%;"></div>
            <div class="skeleton-element sk-title" style="width: 20%;"></div>
        </div>
        <div class="sk-chart-bars">
            <div class="skeleton-element sk-bar" style="height: 40%;"></div>
            <div class="skeleton-element sk-bar" style="height: 65%;"></div>
            <div class="skeleton-element sk-bar" style="height: 50%;"></div>
            <div class="skeleton-element sk-bar" style="height: 85%;"></div>
            <div class="skeleton-element sk-bar" style="height: 70%;"></div>
            <div class="skeleton-element sk-bar" style="height: 95%;"></div>
            <div class="skeleton-element sk-bar" style="height: 60%;"></div>
        </div>
    </div>
    """
    st.markdown(chart_html, unsafe_allow_html=True)