"""
Application-wide constants and configurations.
Centralizes metadata, layout configurations, and default thresholds.
"""

# Project metadata
APP_TITLE = "FinSight"
APP_TAGLINE = "Financial Intelligence & News Sentiment Advisory"

# Default stock settings
DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META"]

# Financial Metrics Categories
METRIC_CATEGORIES = {
    "VALUATION": "Valuation Ratios",
    "PROFITABILITY": "Profitability Ratios",
    "LIQUIDITY_SOLVENCY": "Liquidity & Solvency Ratios",
    "GROWTH": "Growth Rates"
}

# NLP Sentiment Thresholds
SENTIMENT_THRESHOLDS = {
    "STRONG_POSITIVE": 0.5,
    "POSITIVE": 0.05,
    "NEUTRAL_MIN": -0.05,
    "NEUTRAL_MAX": 0.05,
    "NEGATIVE": -0.05,
    "STRONG_NEGATIVE": -0.5
}

# UI Theme Color Palettes (Hex values used in custom styling/charts)
THEME_COLORS = {
    "PRIMARY": "#1E3A8A",       # Sleek deep blue
    "SECONDARY": "#3B82F6",     # Electric blue
    "SUCCESS": "#10B981",       # Emerald green
    "WARNING": "#F59E0B",       # Warm amber
    "DANGER": "#EF4444",        # Vivid red
    "DARK_BG": "#0F172A",       # Slate 900
    "CARD_BG": "#1E293B",       # Slate 800
    "GLASS_BORDER": "rgba(255, 255, 255, 0.1)",
    "TEXT_MUTED": "#94A3B8"      # Slate 400
}

# Chart Configurations
DEFAULT_CHART_LAYOUT = {
    "template": "plotly_dark",
    "paper_bgcolor": "rgba(0, 0, 0, 0)",
    "plot_bgcolor": "rgba(0, 0, 0, 0)",
    "margin": dict(l=20, r=20, t=40, b=20),
    "font": {"family": "Outfit, Inter, system-ui, sans-serif"}
}
