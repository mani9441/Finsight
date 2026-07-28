"""
UI components for rendering news articles and aggregated sentiment indicators.
"""

import streamlit as st
from typing import List
from models import NewsArticle, SentimentResult
from core import get_logger

logger = get_logger("news_cards")

def get_sentiment_badge_html(label: str) -> str:
    """
    Returns custom glassmorphic HTML badge code based on sentiment label.
    """
    lbl_upper = label.strip().upper()
    if lbl_upper == "POSITIVE":
        color_class = "badge-success"  # green
    elif lbl_upper == "NEGATIVE":
        color_class = "badge-danger"   # red
    else:
        color_class = "badge-info"     # gray/blue-gray
        
    return f'<span class="badge {color_class}">{label}</span>'


def render_overall_sentiment_card(sentiment: SentimentResult):
    """
    Displays the overall aggregated sentiment analytics header card.
    """
    badge_html = get_sentiment_badge_html(sentiment.sentiment_label)
    
    # Calculate score formatting
    score_prefix = "+" if sentiment.average_score > 0 else ""
    score_str = f"{score_prefix}{sentiment.average_score:.2f}"
    
    st.markdown(
        f"""
        <div class="glass-card" style="margin-bottom: 2rem; padding: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <h4 style="color: #64748B; margin: 0 0 0.5rem 0; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
                        Overall Market Sentiment
                    </h4>
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <span style="font-size: 1.8rem; font-weight: 800; color: #FFFFFF;">{sentiment.sentiment_label}</span>
                        {badge_html}
                    </div>
                </div>
                <div style="display: flex; gap: 2rem; flex-wrap: wrap; margin-top: 1rem; align-items: center;">
                    <div style="text-align: center;">
                        <div style="color: #64748B; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">Avg Score</div>
                        <div style="font-size: 1.25rem; font-weight: 700; color: #60A5FA;">{score_str}</div>
                    </div>
                    <div style="border-left: 1px solid #334155; height: 35px;"></div>
                    <div style="text-align: center;">
                        <div style="color: #10B981; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">Positive</div>
                        <div style="font-size: 1.25rem; font-weight: 700; color: #10B981;">{sentiment.positive_count}</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="color: #94A3B8; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">Neutral</div>
                        <div style="font-size: 1.25rem; font-weight: 700; color: #94A3B8;">{sentiment.neutral_count}</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="color: #EF4444; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">Negative</div>
                        <div style="font-size: 1.25rem; font-weight: 700; color: #EF4444;">{sentiment.negative_count}</div>
                    </div>
                    <div style="border-left: 1px solid #334155; height: 35px;"></div>
                    <div style="text-align: center;">
                        <div style="color: #64748B; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">Analyzed</div>
                        <div style="font-size: 1.25rem; font-weight: 700; color: #FFFFFF;">{sentiment.article_count} Articles</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_individual_news_card(article: NewsArticle):
    """
    Renders a single premium chronological news article card.
    """
    badge_html = get_sentiment_badge_html(article.sentiment_label)
    date_formatted = article.published_at.strftime("%b %d, %Y • %I:%M %p")
    
    st.markdown(
        f"""
        <div class="glass-card" style="margin-bottom: 1.25rem; padding: 1.5rem; transition: transform 0.2s ease-in-out;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; margin-bottom: 0.75rem;">
                <h4 style="color: #F8FAFC; margin: 0; font-size: 1.15rem; font-weight: 700; line-height: 1.4;">
                    {article.title}
                </h4>
                <div style="flex-shrink: 0; margin-top: 0.2rem;">
                    {badge_html}
                </div>
            </div>
            <div style="display: flex; gap: 0.5rem; align-items: center; color: #94A3B8; font-size: 0.8rem; margin-bottom: 1rem;">
                <span style="font-weight: 600; color: #60A5FA;">{article.source}</span>
                <span>•</span>
                <span>{date_formatted}</span>
            </div>
            <p style="color: #CBD5E1; font-size: 0.925rem; line-height: 1.6; margin: 0 0 1.25rem 0;">
                {article.summary}
            </p>
            <div style="display: flex; justify-content: flex-end;">
                <a href="{article.url}" target="_blank" class="read-more-btn" style="text-decoration: none; font-size: 0.85rem; font-weight: 600; color: #60A5FA; display: inline-flex; align-items: center; gap: 0.25rem;">
                    Read Full Article <span style="font-size: 0.9rem;">→</span>
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_news_sentiment_module(articles: List[NewsArticle], sentiment: SentimentResult):
    """
    Renders the news sentiment analysis header and list feed.
    """
    logger.debug(f"Rendering News Sentiment Module for ticker: {sentiment.ticker}")
    
    st.markdown("### 📰 News & Sentiment Analysis")
    
    # 1. Show overall summary card
    render_overall_sentiment_card(sentiment)
    
    # 2. Show feed of articles
    if not articles:
        st.info("No recent news articles were found for this company.")
        return
        
    st.markdown("#### Recent Coverage")
    for article in articles:
        render_individual_news_card(article)
        
    logger.info(f"Dashboard news rendering completed for '{sentiment.ticker}' with {len(articles)} articles.")
