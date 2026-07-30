"""
UI components for rendering news articles and aggregated sentiment indicators in a White UI theme.
"""

from typing import List
import streamlit as st
from models import NewsArticle, SentimentResult
from core import get_logger

logger = get_logger("news_cards")

# --- GLOBAL STYLES (Inject ONCE at app load/module initialization) ---
def inject_news_module_css():
    """Injects styles once to avoid DOM pollution inside card loops."""
    st.markdown(
        """
        <style>
            /* Sentiment Badges */
            .news-badge {
                display: inline-flex;
                align-items: center;
                font-size: 0.75rem;
                font-weight: 700;
                padding: 0.2rem 0.68rem;
                border-radius: 9999px;
                letter-spacing: 0.03em;
                text-transform: uppercase;
            }
            .badge-success { background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0; }
            .badge-danger  { background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; }
            .badge-info    { background: #EFF6FF; color: #2563EB; border: 1px solid #BFDBFE; }

            .source-tag {
                font-weight: 600;
                color: #2563EB;
                background: #EFF6FF;
                padding: 0.15rem 0.5rem;
                border-radius: 4px;
                font-size: 0.75rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_sentiment_badge_html(label: str) -> str:
    """Returns a clean HTML badge string with appropriate theme classes."""
    lbl_upper = label.strip().upper()
    badge_class = "badge-info"
    
    if lbl_upper in ["POSITIVE", "STRONG_POSITIVE"]:
        badge_class = "badge-success"
    elif lbl_upper in ["NEGATIVE", "STRONG_NEGATIVE"]:
        badge_class = "badge-danger"
        
    formatted_label = label.replace("_", " ")
    return f'<span class="news-badge {badge_class}">{formatted_label}</span>'


def render_overall_sentiment_card(sentiment: SentimentResult):
    """
    Renders overall market sentiment using native Streamlit containers and columns,
    preventing HTML escaping issues while maintaining enterprise styling.
    """
    badge_html = get_sentiment_badge_html(sentiment.sentiment_label)
    score_prefix = "+" if sentiment.average_score > 0 else ""
    score_str = f"{score_prefix}{sentiment.average_score:.2f}"
    score_pct = max(0, min(100, int((sentiment.average_score + 1) / 2 * 100)))

    with st.container(border=True):
        st.caption("OVERALL MARKET SENTIMENT")
        
        # Header Row
        col_title, col_metrics = st.columns([1.2, 2], gap="large")
        
        with col_title:
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-top: 0.25rem;">
                    <span style="font-size: 1.5rem; font-weight: 800; color: #0F172A;">
                        {sentiment.sentiment_label.replace('_', ' ')}
                    </span>
                    {badge_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_metrics:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Avg Score", score_str)
            m2.metric("Positive", sentiment.positive_count)
            m3.metric("Neutral", sentiment.neutral_count)
            m4.metric("Negative", sentiment.negative_count)

        st.divider()

        # Gauge Bar
        st.markdown(
            f"""
            <div>
                <div style="display: flex; justify-content: space-between; font-size: 0.7rem; color: #64748B; font-weight: 700; margin-bottom: 0.3rem;">
                    <span>BEARISH (-1.0)</span>
                    <span>NEUTRAL (0.0)</span>
                    <span>BULLISH (+1.0)</span>
                </div>
                <div style="width: 100%; height: 8px; background: #F1F5F9; border-radius: 4px; position: relative;">
                    <div style="position: absolute; left: {score_pct}%; top: -2px; width: 12px; height: 12px; background: #2563EB; border: 2px solid #FFFFFF; border-radius: 50%; transform: translateX(-50%); box-shadow: 0 1px 3px rgba(0,0,0,0.2);"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_individual_news_card(article: NewsArticle):
    """Renders individual news stories using native Streamlit containers."""
    badge_html = get_sentiment_badge_html(article.sentiment_label)
    date_formatted = article.published_at.strftime("%b %d, %Y • %I:%M %p")

    with st.container(border=True):
        col_heading, col_badge = st.columns([0.82, 0.18])
        
        #with col_heading:
            #st.markdown(f"##### {article.title}")
        with col_badge:
            st.markdown(f"<div style='text-align: right;'>{badge_html}</div>", unsafe_allow_html=True)

        st.markdown(
            f'<span class="source-tag">{article.source}</span> &nbsp;•&nbsp; <span style="color: #64748B; font-size: 0.8rem;">{date_formatted}</span>',
            unsafe_allow_html=True,
        )

        st.write(article.summary)

        # Native Link Button eliminates raw SVG anchor tags
        col_spacer, col_link = st.columns([0.7, 0.3])
        with col_link:
            st.link_button("Read Full Article ↗", article.url, use_container_width=True)


def render_news_sentiment_module(articles: List[NewsArticle], sentiment: SentimentResult):
    """Renders the complete Market News & Sentiment dashboard section."""
    inject_news_module_css()
    logger.debug(f"Rendering News Sentiment Module for ticker: {sentiment.ticker}")

    st.subheader(f" Market News & Sentiment Analysis — {sentiment.ticker}")
    
    render_overall_sentiment_card(sentiment)

    if not articles:
        st.info("No recent news articles were found for this company.")
        return

    st.markdown("### Recent Articles Feed")
    for article in articles:
        render_individual_news_card(article)