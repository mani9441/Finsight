"""
Reusable visual UI components and card layouts for FinSight.
"""

import streamlit as st
from typing import Optional, List
from models import CompanyInfo, SentimentResult, RiskAssessment, AISummary
from core.constants import THEME_COLORS

# --- COMMON ICON UTILITIES (SVG) ---
ICON_BUILDING = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect><path d="M9 22v-4h6v4"></path><path d="M8 6h.01"></path><path d="M16 6h.01"></path><path d="M12 6h.01"></path><path d="M12 10h.01"></path><path d="M12 14h.01"></path><path d="M16 10h.01"></path><path d="M16 14h.01"></path><path d="M8 10h.01"></path><path d="M8 14h.01"></path></svg>"""
ICON_SENTIMENT = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>"""
ICON_SHIELD_ALERT = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>"""
ICON_CPU = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="15" x2="23" y2="15"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="15" x2="4" y2="15"></line></svg>"""
ICON_CHECK = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>"""
ICON_CROSS = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>"""
ICON_ALERT_DOT = """<svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="8"/></svg>"""

# Embedded CSS overlay for UI enhancements
_GLASS_CARD_CSS = """
<style>
    .finsight-card {
        background: rgba(15, 23, 42, 0.65);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .finsight-card:hover {
        border-color: rgba(255, 255, 255, 0.18);
    }
    .card-header-title {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1rem;
        font-weight: 600;
        letter-spacing: 0.01em;
        color: #F8FAFC;
        margin-bottom: 0.75rem;
        text-transform: uppercase;
    }
    .card-header-title svg {
        color: #38BDF8;
    }
    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }
    .badge-pill-success { background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-pill-warning { background: rgba(245, 158, 11, 0.15); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-pill-danger  { background: rgba(239, 68, 68, 0.15); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    .badge-pill-info    { background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.3); }
    
    .data-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 0.75rem;
        margin-top: 1rem;
    }
    .data-cell {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 0.65rem 0.85rem;
    }
    .data-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        color: #94A3B8;
        font-weight: 500;
        letter-spacing: 0.05em;
        margin-bottom: 0.2rem;
    }
    .data-value {
        font-size: 0.95rem;
        font-weight: 600;
        color: #F1F5F9;
    }
</style>
"""


def render_company_profile_card(profile: CompanyInfo):
    """
    Renders corporate metadata, description and officers inside a glassmorphic card.
    """
    st.markdown(_GLASS_CARD_CSS, unsafe_allow_html=True)
    
    website_link = (
        f'<a href="{profile.website}" target="_blank" style="color: {THEME_COLORS["SECONDARY"]}; text-decoration: none; font-weight: 500;">'
        f'{profile.website.replace("https://", "").replace("http://", "")} ↗</a>'
    ) if profile.website else "N/A"
    
    st.markdown(
        f"""
        <div class="finsight-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <div class="card-header-title" style="margin-bottom: 0;">
                    {ICON_BUILDING} {profile.name}
                </div>
                <span class="badge-pill badge-pill-info">{profile.ticker}</span>
            </div>
            <p style="font-size: 0.88rem; color: #CBD5E1; line-height: 1.6; margin-bottom: 1rem;">
                {profile.summary}
            </p>
            <div class="data-grid">
                <div class="data-cell">
                    <div class="data-label">Sector</div>
                    <div class="data-value">{profile.sector}</div>
                </div>
                <div class="data-cell">
                    <div class="data-label">Industry</div>
                    <div class="data-value">{profile.industry}</div>
                </div>
                <div class="data-cell">
                    <div class="data-label">Website</div>
                    <div class="data-value" style="font-size: 0.85rem;">{website_link}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_metric_card(label: str, value: str, delta: Optional[str] = None, help_text: Optional[str] = None):
    """
    Renders a premium individual metric card.
    """
    st.markdown(_GLASS_CARD_CSS, unsafe_allow_html=True)
    
    delta_html = ""
    if delta:
        is_positive = delta.startswith("+")
        color = THEME_COLORS["SUCCESS"] if is_positive else THEME_COLORS["DANGER"]
        bg = "rgba(16, 185, 129, 0.1)" if is_positive else "rgba(239, 68, 68, 0.1)"
        arrow = "▲" if is_positive else "▼"
        delta_html = f"""
        <span style="font-size: 0.75rem; font-weight: 600; color: {color}; background: {bg}; padding: 2px 6px; border-radius: 4px; margin-left: 0.5rem;">
            {arrow} {delta}
        </span>
        """
        
    help_attr = f'title="{help_text}"' if help_text else ""
    
    st.markdown(
        f"""
        <div class="data-cell" style="padding: 1rem;" {help_attr}>
            <div class="data-label" style="margin-bottom: 0.35rem;">{label}</div>
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <span style="font-size: 1.35rem; font-weight: 700; color: #F8FAFC;">{value}</span>
                {delta_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_sentiment_card(sentiment: SentimentResult):
    """
    Renders an aggregated news sentiment analysis card with a visual score scale bar.
    """
    st.markdown(_GLASS_CARD_CSS, unsafe_allow_html=True)
    
    badge_class = "badge-pill-info"
    label_upper = sentiment.sentiment_label.upper()
    if "POSITIVE" in label_upper:
        badge_class = "badge-pill-success"
    elif "NEGATIVE" in label_upper:
        badge_class = "badge-pill-danger"
    elif "NEUTRAL" in label_upper:
        badge_class = "badge-pill-warning"

    # Calculate normalized position for progress indicator (-1.0 to 1.0 -> 0% to 100%)
    score_pct = max(0, min(100, int((sentiment.average_score + 1) / 2 * 100)))

    st.markdown(
        f"""
        <div class="finsight-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <div class="card-header-title" style="margin-bottom: 0;">
                    {ICON_SENTIMENT} News Sentiment Analysis
                </div>
                <span class="badge-pill {badge_class}">
                    {sentiment.sentiment_label.replace('_', ' ')}
                </span>
            </div>
            
            <!-- Sentiment Gauge Visual -->
            <div style="margin-bottom: 1.25rem;">
                <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: #64748B; margin-bottom: 0.25rem; font-weight: 600;">
                    <span>BEARISH (-1.0)</span>
                    <span>NEUTRAL (0.0)</span>
                    <span>BULLISH (+1.0)</span>
                </div>
                <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; position: relative;">
                    <div style="position: absolute; left: {score_pct}%; top: -3px; width: 12px; height: 12px; background: #38BDF8; border: 2px solid #0F172A; border-radius: 50%; transform: translateX(-50%); shadow: 0 0 8px #38BDF8;"></div>
                </div>
            </div>

            <div class="data-grid">
                <div class="data-cell">
                    <div class="data-label">Avg Score</div>
                    <div class="data-value">{sentiment.average_score:+.2f}</div>
                </div>
                <div class="data-cell" style="border-left: 2px solid {THEME_COLORS['SUCCESS']};">
                    <div class="data-label">Positive Articles</div>
                    <div class="data-value" style="color: {THEME_COLORS['SUCCESS']};">{sentiment.positive_count}</div>
                </div>
                <div class="data-cell" style="border-left: 2px solid {THEME_COLORS['WARNING']};">
                    <div class="data-label">Negative Articles</div>
                    <div class="data-value" style="color: {THEME_COLORS['WARNING']};">{sentiment.negative_count}</div>
                </div>
                <div class="data-cell">
                    <div class="data-label">Total Volume</div>
                    <div class="data-value">{sentiment.article_count}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_risk_card(risk: RiskAssessment):
    """
    Renders risk assessment indicators and identified risk factors.
    """
    st.markdown(_GLASS_CARD_CSS, unsafe_allow_html=True)
    
    badge_class = "badge-pill-success"
    risk_color = THEME_COLORS["SUCCESS"]
    
    risk_upper = risk.risk_level.upper()
    if risk_upper in ["CRITICAL", "HIGH"]:
        risk_color = THEME_COLORS["DANGER"]
        badge_class = "badge-pill-danger"
    elif risk_upper == "MEDIUM":
        risk_color = THEME_COLORS["WARNING"]
        badge_class = "badge-pill-warning"

    factors_li = "".join([
        f'<li style="display: flex; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.5rem; font-size: 0.85rem; color: #CBD5E1;">'
        f'<span style="color: {risk_color}; margin-top: 2px;">{ICON_ALERT_DOT}</span>'
        f'<span>{f}</span></li>' 
        for f in risk.risk_factors
    ])
    
    st.markdown(
        f"""
        <div class="finsight-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
                <div class="card-header-title" style="margin-bottom: 0;">
                    {ICON_SHIELD_ALERT} Risk Scorecard
                </div>
                <span class="badge-pill {badge_class}">{risk.risk_level} RISK</span>
            </div>
            
            <div style="display: flex; align-items: baseline; justify-content: space-between; padding: 0.75rem 1rem; background: rgba(0, 0, 0, 0.2); border-radius: 8px; margin-bottom: 1rem;">
                <span class="data-label" style="margin-bottom: 0;">Composite Risk Index</span>
                <div>
                    <span style="font-size: 1.6rem; font-weight: 700; color: {risk_color};">{risk.risk_score:.1f}</span>
                    <span style="font-size: 0.8rem; color: #64748B;"> / 100</span>
                </div>
            </div>
            
            <div>
                <div class="data-label" style="margin-bottom: 0.5rem;">Identified Risk Vectors</div>
                <ul style="list-style-type: none; padding-left: 0; margin: 0;">
                    {factors_li}
                </ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_ai_advisory_card(ai_summary: AISummary):
    """
    Renders LLM generated advisor executive review, list of strengths/weaknesses and investment thesis.
    """
    st.markdown(_GLASS_CARD_CSS, unsafe_allow_html=True)
    
    strengths_html = "".join([
        f'<li style="display: flex; align-items: center; gap: 0.4rem; color: #6EE7B7; margin-bottom: 0.4rem; font-size: 0.83rem;">'
        f'<span style="color: #34D399;">{ICON_CHECK}</span> {s}</li>' 
        for s in ai_summary.strengths
    ])
    
    weaknesses_html = "".join([
        f'<li style="display: flex; align-items: center; gap: 0.4rem; color: #FCA5A5; margin-bottom: 0.4rem; font-size: 0.83rem;">'
        f'<span style="color: #F87171;">{ICON_CROSS}</span> {w}</li>' 
        for w in ai_summary.weaknesses
    ])

    st.markdown(
        f"""
        <div class="finsight-card">
            <div class="card-header-title">
                {ICON_CPU} Executive Intelligence Brief
            </div>
            
            <p style="font-size: 0.88rem; line-height: 1.65; color: #E2E8F0; margin-bottom: 1.25rem;">
                {ai_summary.executive_summary}
            </p>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 1.25rem;">
                <div style="background: rgba(16, 185, 129, 0.04); border-left: 3px solid #34D399; padding: 0.75rem 1rem; border-radius: 0 8px 8px 0;">
                    <div class="data-label" style="color: #34D399; margin-bottom: 0.5rem;">Key Strengths</div>
                    <ul style="list-style-type: none; padding-left: 0; margin: 0;">
                        {strengths_html}
                    </ul>
                </div>
                
                <div style="background: rgba(239, 68, 68, 0.04); border-left: 3px solid #F87171; padding: 0.75rem 1rem; border-radius: 0 8px 8px 0;">
                    <div class="data-label" style="color: #F87171; margin-bottom: 0.5rem;">Key Risks & Vulnerabilities</div>
                    <ul style="list-style-type: none; padding-left: 0; margin: 0;">
                        {weaknesses_html}
                    </ul>
                </div>
            </div>
            
            <div style="padding-top: 1rem; border-top: 1px solid rgba(255, 255, 255, 0.08);">
                <div class="data-label" style="margin-bottom: 0.3rem;">Strategic Thesis</div>
                <div style="padding: 0.75rem 1rem; background: rgba(56, 189, 248, 0.05); border-radius: 8px; border: 1px dashed rgba(56, 189, 248, 0.2); font-style: italic; color: #93C5FD; font-size: 0.85rem; line-height: 1.5;">
                    "{ai_summary.investment_thesis}"
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )