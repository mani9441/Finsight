"""
Empty State Component for FinSight landing dashboard view.
"""

import streamlit as st
from core.constants import THEME_COLORS

def render_empty_state():
    """
    Displays the welcoming instructions on launch when no search has been executed.
    """
    st.markdown(
        f"""
        <div class="glass-card" style="padding: 3rem; text-align: center; margin-top: 1rem;">
            <h2 style="font-size: 2.2rem; font-weight: 800; margin-bottom: 0.5rem; background: linear-gradient(120deg, #FFFFFF 30%, #93C5FD 90%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                🔍 Begin Financial Analysis
            </h2>
            <p style="color: #94A3B8; font-size: 1.1rem; max-width: 600px; margin: 0 auto 2.5rem auto;">
                FinSight parses corporate filings, historical stock pricing, recent news sentiment, and risk parameters to generate AI-driven investment briefs.
            </p>
            
            <div class="feature-grid">
                <div class="feature-box" style="text-align: left;">
                    <div class="feature-icon">📊</div>
                    <div class="feature-name">Financial Metrics</div>
                    <div class="feature-desc">Valuation multipliers, profitability margins, debt-to-equity leverage, and returns.</div>
                </div>
                <div class="feature-box" style="text-align: left;">
                    <div class="feature-icon">📈</div>
                    <div class="feature-name">Price Visualization</div>
                    <div class="feature-desc">Interactive historical daily chart showing closing trends and volume activity.</div>
                </div>
                <div class="feature-box" style="text-align: left;">
                    <div class="feature-icon">🗣️</div>
                    <div class="feature-name">Sentiment Analysis</div>
                    <div class="feature-desc">Aggregate news coverage scores (positive, neutral, negative bias) to capture market mood.</div>
                </div>
                <div class="feature-box" style="text-align: left;">
                    <div class="feature-icon">🤖</div>
                    <div class="feature-name">AI Advisory Briefs</div>
                    <div class="feature-desc">LLM-generated executive summary, investment thesis, and strengths/weaknesses charts.</div>
                </div>
            </div>
            
            <div style="margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid rgba(255, 255, 255, 0.05); color: #94A3B8; font-size: 0.9rem;">
                👈 Use the sidebar panel to enter a stock ticker (e.g. <strong>AAPL</strong>, <strong>MSFT</strong>, <strong>GOOGL</strong>) and click Analyze to begin.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
