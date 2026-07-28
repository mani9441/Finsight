"""
Empty State Component for FinSight landing dashboard view.
"""

import streamlit as st


def render_empty_state():
    # Hero / Header Card
    st.markdown(
        """<div class="glass-card" style="padding: 3rem 2rem; text-align: center; margin-top: 1rem;">
    <h2 class="hero-title" style="margin-bottom: 0.75rem;">
        🔍 Begin Financial Analysis
    </h2>
    <div class="empty-description">
        FinSight parses corporate filings, historical stock pricing, recent news sentiment,
        and risk parameters to generate AI-driven investment briefs.
    </div>
</div>""",
        unsafe_allow_html=True,
    )

    # Grid Features Block (Uses your CSS .feature-grid)
    st.markdown(
        """<div class="feature-grid">
    <div class="feature-box">
        <div class="feature-icon">📊</div>
        <div class="feature-name">Financial Metrics</div>
        <div class="feature-desc">
            Valuation multipliers, profitability margins,
            debt-to-equity leverage, and returns.
        </div>
    </div>
    <div class="feature-box">
        <div class="feature-icon">📈</div>
        <div class="feature-name">Price Visualization</div>
        <div class="feature-desc">
            Interactive historical daily chart showing
            closing trends and volume activity.
        </div>
    </div>
    <div class="feature-box">
        <div class="feature-icon">🗣️</div>
        <div class="feature-name">Sentiment Analysis</div>
        <div class="feature-desc">
            Aggregate news coverage scores (positive,
            neutral, negative bias) to capture market mood.
        </div>
    </div>
    <div class="feature-box">
        <div class="feature-icon">🤖</div>
        <div class="feature-name">AI Advisory Briefs</div>
        <div class="feature-desc">
            LLM-generated executive summary,
            investment thesis, and strengths/weaknesses.
        </div>
    </div>
</div>""",
        unsafe_allow_html=True,
    )

    # Footer Action Prompt
    st.markdown(
        """<div class="glass-card" style="margin-top: 1.5rem; text-align: center; padding: 1.25rem;">
    <span style="color: #94A3B8;">
        👈 Use the <strong style="color: #F8FAFC;">sidebar panel</strong> to enter a stock ticker
        (e.g., <strong style="color: #60A5FA;">AAPL</strong>, <strong style="color: #60A5FA;">MSFT</strong>,
        <strong style="color: #60A5FA;">GOOGL</strong>) and click <strong>Search</strong> to begin.
    </span>
</div>""",
        unsafe_allow_html=True,
    )