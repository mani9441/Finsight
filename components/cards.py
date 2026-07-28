"""
Reusable visual UI components and card layouts for FinSight.
"""

import streamlit as st
from typing import Optional, List
from models import CompanyInfo, SentimentResult, RiskAssessment, AISummary
from core.constants import THEME_COLORS

def render_company_profile_card(profile: CompanyInfo):
    """
    Renders corporate metadata, description and officers inside a glassmorphic card.
    """
    website_link = f'<a href="{profile.website}" target="_blank" style="color: {THEME_COLORS["SECONDARY"]}; text-decoration: none;">{profile.website}</a>' if profile.website else "N/A"
    
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="glass-card-title">🏢 {profile.name} ({profile.ticker})</div>
            <p style="font-size: 0.9rem; color: #E2E8F0; line-height: 1.5; margin-bottom: 1rem;">
                {profile.summary}
            </p>
            <div class="status-grid" style="margin-top: 1rem;">
                <div class="status-item">
                    <div class="status-label">Sector</div>
                    <div style="font-size: 0.95rem; font-weight: 500;">{profile.sector}</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Industry</div>
                    <div style="font-size: 0.95rem; font-weight: 500;">{profile.industry}</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Website</div>
                    <div style="font-size: 0.95rem; font-weight: 500;">{website_link}</div>
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
    delta_html = ""
    if delta:
        color = THEME_COLORS["SUCCESS"] if delta.startswith("+") else THEME_COLORS["DANGER"]
        delta_html = f'<span style="font-size: 0.8rem; font-weight: 600; color: {color}; margin-left: 0.5rem;">{delta}</span>'
        
    help_attr = f'title="{help_text}"' if help_text else ""
    
    st.markdown(
        f"""
        <div class="status-item" style="padding: 1.25rem; text-align: left;" {help_attr}>
            <div class="status-label" style="margin-bottom: 0.25rem;">{label}</div>
            <div style="display: flex; align-items: baseline;">
                <span class="status-value" style="font-size: 1.4rem;">{value}</span>
                {delta_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_sentiment_card(sentiment: SentimentResult):
    """
    Renders an aggregated news sentiment analysis card.
    """
    # Dynamic class map
    badge_class = "badge-info"
    if sentiment.sentiment_label.upper() in ["POSITIVE", "STRONG_POSITIVE"]:
        badge_class = "badge-success"
    elif sentiment.sentiment_label.upper() in ["NEGATIVE", "STRONG_NEGATIVE"]:
        badge_class = "badge-warning"
        
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="glass-card-title">📊 News Sentiment Advisory</div>
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.25rem;">
                <span class="badge {badge_class}" style="font-size: 0.9rem; padding: 0.4rem 0.8rem;">
                    {sentiment.sentiment_label}
                </span>
                <span style="color: #94A3B8; font-size: 0.9rem;">
                    Based on <strong>{sentiment.article_count} articles</strong> analyzed.
                </span>
            </div>
            
            <div class="status-grid">
                <div class="status-item">
                    <div class="status-label">Average Score</div>
                    <div class="status-value">{sentiment.average_score:+.2f}</div>
                </div>
                <div class="status-item" style="border-left: 3px solid {THEME_COLORS['SUCCESS']};">
                    <div class="status-label">Positive Articles</div>
                    <div class="status-value" style="color: {THEME_COLORS['SUCCESS']};">{sentiment.positive_count}</div>
                </div>
                <div class="status-item" style="border-left: 3px solid {THEME_COLORS['WARNING']};">
                    <div class="status-label">Negative Articles</div>
                    <div class="status-value" style="color: {THEME_COLORS['WARNING']};">{sentiment.negative_count}</div>
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
    risk_color = THEME_COLORS["SUCCESS"]
    badge_class = "badge-success"
    if risk.risk_level.upper() == "CRITICAL":
        risk_color = THEME_COLORS["DANGER"]
        badge_class = "badge-danger"
    elif risk.risk_level.upper() == "HIGH":
        risk_color = THEME_COLORS["DANGER"]
        badge_class = "badge-warning"
    elif risk.risk_level.upper() == "MEDIUM":
        risk_color = THEME_COLORS["WARNING"]
        badge_class = "badge-warning"

    factors_li = "".join([f'<li style="margin-bottom: 0.4rem; font-size: 0.88rem; color: #E2E8F0;">⚠️ {f}</li>' for f in risk.risk_factors])
    
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="glass-card-title">⚠️ Risk Assessment Scorecard</div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.25rem;">
                <div>
                    <span class="status-label">Overall Risk Level</span>
                    <div style="margin-top: 0.25rem;">
                        <span class="badge {badge_class}" style="font-size: 0.9rem; padding: 0.4rem 0.8rem;">
                            {risk.risk_level}
                        </span>
                    </div>
                </div>
                <div style="text-align: right;">
                    <span class="status-label">Composite Score</span>
                    <div class="status-value" style="font-size: 1.8rem; color: {risk_color};">{risk.risk_score:.1f}/100</div>
                </div>
            </div>
            
            <div style="margin-top: 1rem;">
                <span class="status-label">Key Risk Factors Identified</span>
                <ul style="list-style-type: none; padding-left: 0; margin-top: 0.5rem; margin-bottom: 0;">
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
    strengths_html = "".join([f'<li style="color: #A7F3D0; margin-bottom: 0.3rem;">✓ {s}</li>' for s in ai_summary.strengths])
    weaknesses_html = "".join([f'<li style="color: #FCA5A5; margin-bottom: 0.3rem;">✗ {w}</li>' for w in ai_summary.weaknesses])

    st.markdown(
        f"""
        <div class="glass-card">
            <div class="glass-card-title">🤖 AI Advisory Executive Report</div>
            <p style="font-size: 0.95rem; line-height: 1.6; color: #E2E8F0;">
                {ai_summary.executive_summary}
            </p>
            
            <div class="feature-grid" style="margin-top: 1.25rem;">
                <div class="feature-box" style="border-left: 4px solid {THEME_COLORS['SUCCESS']};">
                    <div class="feature-name" style="color: #34D399;">Strengths & Opportunities</div>
                    <ul style="list-style-type: none; padding-left: 0; font-size: 0.85rem; margin-top: 0.5rem; margin-bottom: 0;">
                        {strengths_html}
                    </ul>
                </div>
                
                <div class="feature-box" style="border-left: 4px solid {THEME_COLORS['DANGER']};">
                    <div class="feature-name" style="color: #F87171;">Weaknesses & Threats</div>
                    <ul style="list-style-type: none; padding-left: 0; font-size: 0.85rem; margin-top: 0.5rem; margin-bottom: 0;">
                        {weaknesses_html}
                    </ul>
                </div>
            </div>
            
            <div style="margin-top: 1.5rem; padding-top: 1.25rem; border-top: 1px solid rgba(255, 255, 255, 0.05);">
                <div class="status-label">Investment Thesis</div>
                <blockquote style="border-left: 3px solid {THEME_COLORS['SECONDARY']}; padding-left: 0.75rem; color: #D1D5DB; font-style: italic; font-size: 0.9rem; margin-top: 0.4rem; margin-bottom: 0;">
                    "{ai_summary.investment_thesis}"
                </blockquote>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
